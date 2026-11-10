import json
import io
import zipfile
import unittest
from uuid import uuid4
from app import main,backups
import test_api as support
import test_recipes

class PlanningTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    setup_recipe=test_recipes.RecipeTests.setup_recipe

    async def plan(self,recipe,**extra):
        id=str(uuid4());body={'day':'2026-11-11','recipe_id':recipe['id'],'amount':2,'unit':'portion',**extra}
        r=await self.client.put('/planning/meals/'+id,json=body)
        self.assertEqual(r.status_code,200,r.text)
        return r.json(),body
    async def shopping(self):
        return (await self.client.get('/planning/shopping',params={'start':'2026-11-11','end':'2026-11-17'})).json()
    async def stock(self,amount=50,**extra):
        id=str(uuid4());body={'name':'Zutat','source':'bls','source_id':'RECIPE_TEST','amount':amount,'unit':'g',**extra}
        r=await self.client.put('/planning/inventory/'+id,json=body)
        self.assertEqual(r.status_code,200,r.text)
        return r.json()

    async def test_plan_scaling_stock_aggregate_and_no_premature_intake(self):
        r,i=await self.setup_recipe();p,b=await self.plan(r)
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual((await self.client.get('/health-export/pending')).json(),[])
        await self.plan(r,amount=100,unit='g') # 100/600*300=50g
        await self.stock(50);await self.stock(25)
        s=await self.shopping();self.assertEqual(len(s['items']),1)
        item=s['items'][0];self.assertEqual(item['required'],200);self.assertEqual(item['available'],75);self.assertEqual(item['to_buy'],125)
        await self.stock(999,unit='ml')
        await self.stock(999,source='text',source_id='') # same name is NOT same linked BLS reference
        await self.stock(999,expires='2026-11-10')
        self.assertEqual((await self.shopping())['items'][0]['to_buy'],125)
        response=await self.client.put('/planning/check/'+item['id'],json={'checked':True,'start':'2026-11-11','end':'2026-11-17'})
        self.assertEqual(response.status_code,200)
        self.assertTrue((await self.shopping())['items'][0]['checked'])
        await self.stock(1)
        self.assertFalse((await self.shopping())['items'][0]['checked'])

    async def test_eating_snapshot_time_retry_and_deletion(self):
        r,i=await self.setup_recipe();p,b=await self.plan(r)
        # Change live recipe ingredient; planned snapshot must remain 300g.
        with main.db() as c:
            raw=json.loads(c.execute('SELECT payload FROM entries WHERE id=?',(i['id'],)).fetchone()['payload'])
            raw['quantity']['value']=999;c.execute('UPDATE entries SET payload=? WHERE id=?',(json.dumps(raw),i['id']))
        url='/planning/meals/'+p['id']+'/eat';body={'timestamp':'2026-11-12T19:30:00+01:00'}
        result=await self.client.post(url,json=body);self.assertEqual(result.status_code,200,result.text)
        id=result.json()['entry_id'];e=(await self.client.get('/entries/'+id)).json()
        self.assertEqual(e['timestamp'],body['timestamp']);self.assertEqual(e['nutrients']['dietaryEnergyConsumed']['value'],300)
        self.assertEqual(e['recipe_snapshot']['ingredients'][0]['quantity']['value'],300)
        self.assertEqual(e['health_status'],'pending')
        self.assertTrue((await self.client.post(url,json=body)).json()['already_logged'])
        self.assertEqual(len((await self.client.get('/entries')).json()),1)
        self.assertEqual((await self.shopping())['items'],[])
        self.assertEqual((await self.client.put('/planning/meals/'+p['id'],json={**b,'version':1})).status_code,409)
        await self.client.delete('/entries/'+id)
        self.assertTrue((await self.client.post(url,json=body)).json()['already_logged'])
        self.assertEqual((await self.client.get('/entries')).json(),[])

    async def test_toggles_preserve_data_and_shopping_manual(self):
        r,i=await self.setup_recipe();p,b=await self.plan(r);await self.stock()
        m={'name':'Apples','amount':3,'unit':'piece'}
        self.assertEqual((await self.client.put('/planning/shopping/'+str(uuid4()),json=m)).status_code,200)
        cfg=(await self.client.get('/planning/settings')).json()
        cfg= (await self.client.put('/planning/settings',json={**cfg,'inventory_enabled':False})).json()
        self.assertEqual((await self.shopping())['items'][0]['available'],0)
        self.assertEqual((await self.client.get('/planning/inventory')).status_code,409)
        cfg=(await self.client.put('/planning/settings',json={**cfg,'planning_enabled':False})).json()
        self.assertEqual(len((await self.shopping())['items']),1)
        self.assertEqual((await self.client.post('/planning/meals/'+p['id']+'/eat',json={'timestamp':'2026-11-12T19:00:00+01:00'})).status_code,409)
        await self.client.put('/planning/settings',json={**cfg,'planning_enabled':True,'inventory_enabled':True})
        self.assertEqual(len((await self.client.get('/planning/inventory')).json()),1)
        self.assertEqual(len((await self.shopping())['items']),2)

    async def test_versions_validation_auth_and_backups(self):
        r,i=await self.setup_recipe();p,b=await self.plan(r)
        self.assertEqual((await self.client.put('/planning/meals/'+p['id'],json=b)).json()['version'],1) # retry
        self.assertEqual((await self.client.put('/planning/meals/'+p['id'],json={**b,'version':0,'amount':3})).status_code,409)
        self.assertEqual((await self.client.delete('/planning/meals/'+p['id']+'?version=3')).status_code,409)
        for body in [{**b,'amount':0},{**b,'unit':'fraction','amount':2}]:
            self.assertEqual((await self.client.put('/planning/meals/'+str(uuid4()),json=body)).status_code,422)
        self.assertEqual((await self.client.post('/planning/meals/'+p['id']+'/eat',json={'timestamp':'2026-11-11T19:00:00'})).status_code,422)
        self.assertEqual((await self.client.get('/planning/settings',headers={'Authorization':'bad'})).status_code,401)
        archive=backups.build(main.db,main.DATA,'1.42.0')
        doc,blobs=backups.unpack(archive,main.db)
        self.assertTrue(doc['tables']['planning_records'])
        # Pre-feature backup must restore with an empty planning table.
        doc['tables'].pop('planning_records');doc['files']={}
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr('backup.json',json.dumps(doc))
        old,_=backups.unpack(out.getvalue(),main.db)
        self.assertEqual(old['tables']['planning_records'],[])
