import json
import unittest
from uuid import uuid4
from unittest.mock import patch
from app import main,backups
import test_api as support

class BarcodeBLSTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload
    def seed(self):
        with main.db() as c:
            for code,energy in [('A',100),('B',250)]:
                f={'bls_code':code,'name_de':'Lebensmittel '+code,'name_en':'Food '+code,'nutrients':{'dietaryEnergyConsumed':energy,'dietaryVitaminC':10}}
                c.execute('INSERT INTO foods VALUES(?,?,?)',(code,json.dumps(f),'lebensmittel food '+code.lower()))
    async def link(self,code='A',version=0):
        return await self.client.put('/barcode-bls/0123456789012',json={'version':version,'bls_code':code})
    def item(self,**extra):
        return self.payload(type='barcode_bls',drink=None,barcode='0123456789012',quantity={'value':150,'unit':'g'},**extra)

    async def test_link_required_bls_only_recipe_and_snapshot(self):
        self.seed();body=self.item()
        self.assertFalse((await self.client.get('/barcode-bls/0123456789012')).json()['linked'])
        self.assertEqual((await self.client.post('/entries',json=body)).status_code,409)
        self.assertEqual((await self.client.get('/entries')).json(),[])
        link=(await self.link()).json();self.assertEqual(link['version'],1)
        # OFF must never be contacted in this mode.
        with patch('app.main.httpx.AsyncClient',side_effect=AssertionError('Remote lookup forbidden')):
            r=await self.client.post('/entries',json=body)
        self.assertEqual(r.status_code,201,r.text);entry=r.json()
        self.assertEqual(entry['nutrients']['dietaryEnergyConsumed']['value'],150)
        self.assertEqual(entry['nutrients']['dietaryVitaminC']['value'],15)
        self.assertEqual(entry['source']['provider'],'BLS');self.assertEqual(entry['source']['barcode'],body['barcode'])
        self.assertEqual(entry['bls_code'],'A')
        await self.link('B',1)
        self.assertEqual((await self.client.post('/entries',json=body)).json()['bls_code'],'A')
        self.assertEqual((await self.client.get('/entries/'+entry['id'])).json()['bls_code'],'A')
        recipe={'id':str(uuid4()),'name':'Test','servings':1}
        await self.client.post('/recipes',json=recipe)
        ingredient=await self.client.post('/entries',json=self.item(recipe_id=recipe['id']))
        self.assertEqual(ingredient.status_code,201,ingredient.text)
        self.assertEqual(ingredient.json()['nutrients']['dietaryEnergyConsumed']['value'],375)
        self.assertEqual(len((await self.client.get('/entries')).json()),1)
        self.assertEqual((await self.client.get('/recipes/'+recipe['id'])).json()['ingredients'][0]['bls_code'],'B')
        await self.client.delete('/barcode-bls/0123456789012?version=2')
        self.assertEqual((await self.client.post('/entries',json=self.item())).status_code,409)
        # Existing entries retain code A even after link deletion and amount review.
        reviewed=await self.client.post('/entries/'+entry['id']+'/resolve',json={'quantity':{'value':200,'unit':'g'}})
        self.assertEqual(reviewed.status_code,200,reviewed.text)
        self.assertEqual(reviewed.json()['nutrients']['dietaryEnergyConsumed']['value'],200)

    async def test_versions_retries_guards_and_backup(self):
        self.seed()
        self.assertEqual((await self.link()).status_code,200)
        self.assertEqual((await self.link()).json()['version'],1)
        self.assertEqual((await self.link('B',0)).status_code,409)
        self.assertEqual((await self.client.post('/entries',json=self.item(barcode_bls_version=2))).status_code,409)
        doc,_=backups.unpack(backups.build(main.db,main.DATA,'1.44.0'),main.db)
        self.assertEqual(doc['tables']['barcode_bls_links'][0]['code'],'A')
        self.assertEqual((await self.client.delete('/barcode-bls/0123456789012?version=2')).status_code,409)
        deleted=(await self.client.delete('/barcode-bls/0123456789012?version=1')).json()
        self.assertFalse(deleted['linked']);self.assertEqual(deleted['version'],2)
        self.assertEqual((await self.link('B',0)).status_code,409)
        self.assertEqual((await self.link('B',2)).status_code,200)
        await self.life.__aexit__(None,None,None);self.life=main.lifespan(main.app);await self.life.__aenter__()
        self.assertEqual((await self.client.get('/barcode-bls/0123456789012')).json()['bls_code'],'B')

    async def test_validation_missing_bls_unknown_quantity_and_auth(self):
        self.seed()
        self.assertEqual((await self.link('missing')).status_code,422)
        self.assertEqual((await self.client.get('/barcode-bls/not-a-code')).status_code,422)
        self.assertEqual((await self.client.get('/barcode-bls/0123456789012',headers={'Authorization':'bad'})).status_code,401)
        self.assertEqual((await self.client.put('/barcode-bls/0123456789012',json={'version':0,'bls_code':'A'},headers={'Authorization':'bad'})).status_code,401)
        await self.link()
        body=self.item();body['quantity']=None
        r=await self.client.post('/entries',json=body)
        self.assertEqual(r.status_code,201);self.assertEqual(r.json()['status'],'needs_review');self.assertEqual(r.json()['bls_code'],'A')
        body=self.item();body['barcode']=None
        self.assertEqual((await self.client.post('/entries',json=body)).status_code,422)
        with main.db() as c:c.execute("DELETE FROM foods WHERE code='A'")
        self.assertFalse((await self.client.get('/barcode-bls/0123456789012')).json()['linked'])
        self.assertEqual((await self.client.post('/entries',json=self.item())).status_code,409)
