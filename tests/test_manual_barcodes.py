import json
import unittest
from uuid import uuid4
from unittest.mock import patch
from app import main,backups,label_ocr
import test_api as support

class ManualBarcodeTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload
    def food(self,**extra):return {'id':str(uuid4()),'version':0,'name_de':'Own food','barcodes':['0123456789012'],'basis_unit':'g','nutrients':{'dietaryEnergyConsumed':{'value':120,'unit':'kcal'},'dietaryVitaminC':{'value':80,'unit':'mg'}},**extra}
    async def test_local_priority_snapshot_recipe_and_no_network(self):
        food=self.food();r=await self.client.post('/manual-ingredients',json=food);self.assertEqual(r.status_code,201,r.text)
        lookup=(await self.client.get('/barcodes/0123456789012')).json();self.assertEqual(lookup['source'],'manual');self.assertEqual(lookup['food']['id'],food['id'])
        body=self.payload(type='barcode',drink=None,barcode='0123456789012',quantity={'value':50,'unit':'g'})
        with patch('app.main.httpx.AsyncClient',side_effect=AssertionError('OFF must not be called')):r=await self.client.post('/entries',json=body)
        self.assertEqual(r.status_code,201,r.text);e=r.json();self.assertEqual(e['type'],'manual');self.assertEqual(e['source']['provider'],'Manual')
        self.assertEqual(e['barcode'],body['barcode']);self.assertEqual(e['nutrients']['dietaryEnergyConsumed']['value'],60)
        self.assertEqual(e['nutrients']['dietaryVitaminC']['value'],40)
        recipe={'id':str(uuid4()),'name':'Recipe','servings':1};await self.client.post('/recipes',json=recipe)
        with patch('app.main.httpx.AsyncClient',side_effect=AssertionError('OFF must not be called')):
            r=await self.client.post('/entries',json={**body,'id':str(uuid4()),'recipe_id':recipe['id']})
        self.assertEqual(r.status_code,201);self.assertEqual((await self.client.get('/recipes/'+recipe['id'])).json()['nutrients']['dietaryEnergyConsumed']['value'],60)
        await self.client.delete('/manual-ingredients/'+food['id']+'?version=0')
        self.assertEqual((await self.client.get('/barcodes/0123456789012')).json()['source'],'off')
        self.assertEqual((await self.client.post('/entries',json=body)).json()['manual_id'],food['id'])
        r=await self.client.post('/entries/'+e['id']+'/resolve',json={'quantity':{'value':100,'unit':'g'}})
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['nutrients']['dietaryEnergyConsumed']['value'],120)

    async def test_unique_mapping_validation_preserve_omitted_and_backup(self):
        food=self.food();saved=(await self.client.post('/manual-ingredients',json=food)).json()
        self.assertEqual((await self.client.post('/manual-ingredients',json=self.food())).status_code,409)
        other=self.food(barcodes=['1111111111111']);other=(await self.client.post('/manual-ingredients',json=other)).json()
        r=await self.client.put('/manual-ingredients/'+other['id'],json={**other,'barcodes':food['barcodes']})
        self.assertEqual(r.status_code,409)
        for codes in [['bad'],['0123456789012','0123456789012'],['123']]:
            self.assertEqual((await self.client.post('/manual-ingredients',json=self.food(barcodes=codes))).status_code,422)
        old_client={k:v for k,v in saved.items() if k!='barcodes'};r=await self.client.put('/manual-ingredients/'+food['id'],json=old_client)
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['barcodes'],food['barcodes'])
        r=await self.client.get('/barcodes/0123456789012',headers={'Authorization':'bad'});self.assertEqual(r.status_code,401)
        self.assertEqual((await self.client.get('/barcodes/nope')).status_code,422)
        doc,_=backups.unpack(backups.build(main.db,main.DATA,'1.47.0'),main.db)
        self.assertTrue(any(row['id']==food['id'] and json.loads(row['payload'])['barcodes']==food['barcodes'] for row in doc['tables']['manual_ingredients']))

    async def test_ml_basis_and_explicit_bls_stays_separate(self):
        food=self.food(basis_unit='ml');await self.client.post('/manual-ingredients',json=food)
        with main.db() as c:
            f={'bls_code':'A','name_de':'BLS food','name_en':'BLS food','nutrients':{'dietaryEnergyConsumed':200}}
            c.execute('INSERT INTO foods VALUES(?,?,?)',('A',json.dumps(f),'food'))
        await self.client.put('/barcode-bls/0123456789012',json={'version':0,'bls_code':'A'})
        base=self.payload(type='barcode',drink=None,barcode='0123456789012',quantity={'value':200,'unit':'ml'})
        with patch('app.main.httpx.AsyncClient',side_effect=AssertionError('OFF must not be called')):r=await self.client.post('/entries',json=base)
        self.assertEqual(r.status_code,201,r.text);self.assertEqual(r.json()['nutrients']['dietaryEnergyConsumed']['value'],240)
        wrong=await self.client.post('/entries',json={**base,'id':str(uuid4()),'quantity':{'value':200,'unit':'g'}})
        self.assertEqual(wrong.json()['status'],'needs_review')
        bls=await self.client.post('/entries',json={**base,'id':str(uuid4()),'type':'barcode_bls','quantity':{'value':200,'unit':'g'}})
        self.assertEqual(bls.status_code,201,bls.text);self.assertEqual(bls.json()['source']['provider'],'BLS')

    def test_ocr_explicit_tablet_basis_units_and_vitamins(self):
        text='Pro Brausetablette\nVitamin C 80 mg 100%\nBiotin 50 µg 100%\nNiacin 16 mg\nPantothensäure 6 mg\nVitamin B12 2,5 µg\nSalz 0,01 g'
        self.assertEqual(label_ocr.parse(text)['nutrients'],{})
        n=label_ocr.parse(text,6,'g')
        self.assertEqual(n['basis'],'100g');self.assertAlmostEqual(n['nutrients']['dietaryVitaminC']['value'],80/6*100)
        self.assertAlmostEqual(n['nutrients']['dietaryBiotin']['value'],50/6*100)
        self.assertAlmostEqual(n['nutrients']['dietaryVitaminB12']['value'],2.5/6*100)
        self.assertEqual(label_ocr.parse('Pro 100 ml\nProtein 3 g',100,'ml')['basis_unit'],'ml')
        self.assertEqual(label_ocr.parse('Pro 100 g\nProtein 3 g',6,'g')['nutrients'],{})

    async def test_ocr_reference_api_preview_only(self):
        from unittest.mock import AsyncMock
        result=label_ocr.parse('Pro Tablette\nVitamin C 80 mg',6,'g')
        with patch.object(label_ocr,'run_in_threadpool',AsyncMock(return_value=result)) as worker:
            r=await self.client.post('/manual-ingredients/scan-label?reference_amount=6&reference_unit=g',content=b'image')
            worker.assert_awaited_once_with(label_ocr.scan,b'image',6,'g')
        self.assertEqual(r.status_code,200,r.text)
        self.assertAlmostEqual(r.json()['nutrients']['dietaryVitaminC']['value'],80/6*100)
        self.assertEqual(r.json()['reference_amount'],6)
        self.assertEqual((await self.client.get('/manual-ingredients')).json(),[])
        self.assertEqual((await self.client.post('/manual-ingredients/scan-label?reference_amount=0',content=b'image')).status_code,422)

    async def test_existing_off_refresh_does_not_switch_to_new_local_link(self):
        import httpx
        original=httpx.AsyncClient
        def client(**kw):return original(transport=httpx.MockTransport(lambda req:httpx.Response(200,json={'status':1,'product':{'product_name':'OFF','nutriments':{'energy-kcal_100g':10}}})),**kw)
        body=self.payload(type='barcode',drink=None,barcode='0123456789012',quantity={'value':100,'unit':'g'})
        with patch.object(httpx,'AsyncClient',client):old=(await self.client.post('/entries',json=body)).json()
        await self.client.post('/manual-ingredients',json=self.food())
        with patch.object(httpx,'AsyncClient',client):r=await self.client.post('/entries/'+old['id']+'/refresh-off',json={'revision':1})
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['entry']['source']['provider'],'Open Food Facts')
        self.assertEqual(r.json()['entry']['nutrients']['dietaryEnergyConsumed']['value'],10)
