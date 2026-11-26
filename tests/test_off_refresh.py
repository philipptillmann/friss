import copy
import json
import unittest
from unittest.mock import patch
from uuid import uuid4
import httpx
from app import main,off_refresh
import test_api as support

class OFFRefreshTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload
    def mock(self,food=None,status=200,change=None):
        original=httpx.AsyncClient
        def handle(request):
            if change:change()
            return httpx.Response(status,json={'status':1,'product':food} if food is not None else {'status':0})
        return patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handle),**kw))
    async def entry(self,**extra):
        with self.mock({'product_name':'Noodles','nutriments':{'energy-kcal_100g':0,'fat_100g':0,'proteins_100g':0}}):
            r=await self.client.post('/entries',json=self.payload(type='barcode',drink=None,barcode='0123456789012',quantity={'value':150,'unit':'g'},**extra))
        self.assertEqual(r.status_code,201,r.text);return r.json()
    async def refresh(self,e):return await self.client.post('/entries/'+e['id']+'/refresh-off',json={'revision':e['revision']})

    def test_detection_uses_raw_source_and_not_rounded_values(self):
        e={'type':'barcode','barcode':'0123456789012','source':{'provider':'Open Food Facts'},'food':{'nutriments':{}}}
        self.assertTrue(off_refresh.empty(e))
        e['food']['nutriments']={'energy-kcal_100g':0,'salt_100g':'0','nutrition-score-fr_100g':20}
        self.assertTrue(off_refresh.empty(e))
        e['food']['nutriments']['proteins_100g']=.000001;self.assertFalse(off_refresh.empty(e))
        e['food']['nutriments']={'energy-kcal_100g':0,'vitamin-c_100g':1};self.assertFalse(off_refresh.empty(e))
        self.assertFalse(off_refresh.empty({**e,'type':'barcode_bls','bls_code':'A'}))

    async def test_refresh_recalculates_only_selected_and_preserves_metadata(self):
        e=await self.entry();other=await self.entry()
        self.assertTrue((await self.client.get('/entries/'+e['id'])).json()['off_nutrition_empty'])
        audit=(await self.client.get('/statistics/day',params={'day':'2026-10-04','tz':'UTC'})).json()
        self.assertTrue(next(r for r in audit['rows'] if r['id']==e['id'])['off_nutrition_empty'])
        original=(main.DATA/'originals'/f"{e['id']}.json").read_bytes()
        with self.mock({'product_name':'Noodles updated','nutriments':{'energy-kcal_100g':200,'proteins_100g':8}}):
            result=await self.refresh(e)
        self.assertEqual(result.status_code,200,result.text);data=result.json();self.assertTrue(data['changed']);self.assertFalse(data['entry']['off_nutrition_empty'])
        updated=main.load_entry(e['id']);self.assertEqual(updated['nutrients']['dietaryEnergyConsumed']['value'],300)
        self.assertEqual(updated['revision'],2)
        for key in ['timestamp','quantity','barcode','health_status','id']:self.assertEqual(updated[key],e[key])
        self.assertEqual(main.load_entry(other['id']),other)
        self.assertEqual((main.DATA/'originals'/f"{e['id']}.json").read_bytes(),original)
        self.assertTrue((main.DATA/'originals'/f"{e['id']}-revision-1.json").exists())
        with self.mock(updated['food']):
            result=await self.refresh(updated)
        self.assertFalse(result.json()['changed']);self.assertEqual(main.load_entry(e['id'])['revision'],2)
        self.assertEqual((await self.refresh(e)).status_code,409)

    async def test_failure_and_concurrent_update_keep_saved_values(self):
        e=await self.entry()
        for food,status in [(None,200),(None,503),([],200)]:
            with self.mock(food,status):r=await self.refresh(e)
            self.assertEqual(r.status_code,502,r.text);self.assertEqual(main.load_entry(e['id']),e)
        def change():
            current=main.load_entry(e['id']);current['description']='concurrent edit';main.save_entry(current)
        with self.mock({'product_name':'New','nutriments':{'energy-kcal_100g':123}},change=change):r=await self.refresh(e)
        self.assertEqual(r.status_code,409);self.assertEqual(main.load_entry(e['id'])['description'],'concurrent edit')
        self.assertEqual(main.load_entry(e['id'])['nutrients'],e['nutrients'])

    async def test_recipe_ingredient_and_health_guards(self):
        recipe={'id':str(uuid4()),'name':'Noodles recipe','servings':1};await self.client.post('/recipes',json=recipe)
        ingredient=await self.entry(recipe_id=recipe['id'])
        intake=(await self.client.post('/recipes/'+recipe['id']+'/intake',json={'id':str(uuid4()),'timestamp':'2026-11-26T12:00:00Z','amount':1,'unit':'portion'})).json()
        with self.mock({'product_name':'Fixed','nutriments':{'energy-kcal_100g':100}}):r=await self.refresh(ingredient)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual((await self.client.get('/recipes/'+recipe['id'])).json()['nutrients']['dietaryEnergyConsumed']['value'],150)
        self.assertEqual(main.load_entry(intake['id'])['nutrients']['dietaryEnergyConsumed']['value'],0)
        e=await self.entry();e['health_status']='claimed';main.save_entry(e)
        self.assertEqual((await self.refresh(e)).status_code,409)
        e['health_status']='synced';e['health_export_nutrients']=copy.deepcopy(e['nutrients']);main.save_entry(e)
        with self.mock({'product_name':'Fixed','nutriments':{'energy-kcal_100g':100}}):r=await self.refresh(e)
        self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['health_correction_required'])
        self.assertEqual(main.load_entry(e['id'])['health_export_nutrients'],e['health_export_nutrients'])
        self.assertEqual(main.load_entry(e['id'])['health_status'],'synced')

    async def test_missing_quantity_zero_policy_auth_and_wrong_source(self):
        e=await self.entry()
        with main.db() as c:c.execute('INSERT INTO preferences VALUES(1,?)',(json.dumps({'missing_nutrients_as_zero':True}),))
        self.assertTrue((await self.client.get('/entries/'+e['id']+'/details')).json()['off_nutrition_empty'])
        e['quantity']=None;main.save_entry(e)
        with self.mock({'product_name':'Fixed','nutriments':{'energy-kcal_100g':10}}):r=await self.refresh(e)
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['entry']['status'],'needs_review')
        self.assertFalse(r.json()['entry']['off_nutrition_empty'])
        url='/entries/'+e['id']+'/refresh-off'
        self.assertEqual((await self.client.post(url,json={'revision':1},headers={'Authorization':'bad'})).status_code,401)
        water=(await self.client.post('/entries',json=self.payload())).json()
        self.assertEqual((await self.refresh(water)).status_code,422)
        # Prepared daily exports block mutation as well as individual claims.
        e=await self.entry()
        with main.db() as c:c.execute('INSERT INTO health_days VALUES(?,?,?,?)',('test','2026-11-26','UTC',json.dumps({'entry_ids':[e['id']],'status':'prepared'})))
        self.assertEqual((await self.refresh(e)).status_code,409)
