import json
import unittest
import test_api as support
from app import main

class BLSApiTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown

    def seed(self):
        foods=[('MILK','Vollmilch','Whole milk',{'dietaryEnergyConsumed':64,'dietaryProtein':3.3,'dietaryVitaminC':'TR'}),
               ('SALT','Speisesalz','Table salt',{'dietaryEnergyConsumed':0,'dietarySodium':39000})]
        with main.db() as c:
            for code,de,en,nutrients in foods:
                f={'bls_code':code,'name_de':de,'name_en':en,'nutrients':nutrients}
                c.execute('INSERT INTO foods VALUES(?,?,?)',(code,json.dumps(f),main.normalize(de+' '+en)))

    def meal(self):
        return {'timestamp':'2026-11-03T12:15:00+01:00','title':'Milch mit Salz','original_message':'  Test original  ',
                'items':[{'bls_code':'MILK','grams':150,'notes':'Gewogen'},{'bls_code':'SALT','grams':2}]}

    async def test_lookup_preview_atomic_commit_and_retry(self):
        self.seed()
        r=await self.client.get('/bls/search',params={'q':'Salz','lang':'en'})
        self.assertEqual(r.status_code,200)
        result=r.json();self.assertEqual(result['database_count'],2)
        self.assertEqual(result['results'][0]['name'],'Table salt')
        self.assertEqual(result['results'][0]['bls_code'],'SALT')
        self.assertEqual(result['results'][0]['quantity_unit'],'g')
        before=set((main.DATA/'originals').iterdir())
        body=self.meal()
        preview=await self.client.post('/bls/meals/preview',json=body)
        self.assertEqual(preview.status_code,200,preview.text)
        p=preview.json();self.assertFalse(p['saved']);self.assertEqual(p['count'],2)
        self.assertEqual(p['items'][0]['nutrients']['dietaryEnergyConsumed']['value'],96)
        self.assertTrue(p['items'][0]['warnings'])
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual(set((main.DATA/'originals').iterdir()),before)
        response=await self.client.post('/bls/meals',json=body)
        self.assertEqual(response.status_code,201,response.text)
        saved=response.json();self.assertEqual(saved['count'],2)
        entries=(await self.client.get('/entries')).json()
        self.assertEqual(len(entries),2)
        milk=next(e for e in entries if e['bls_code']=='MILK')
        self.assertEqual(milk['source']['provider'],'BLS')
        self.assertEqual(milk['timestamp'],body['timestamp'])
        self.assertEqual(milk['health_status'],'pending')
        self.assertEqual(milk['import_context']['title'],body['title'])
        self.assertEqual(milk['import_context']['original_message'],body['original_message'])
        self.assertEqual(milk['import_context']['notes'],'Gewogen')
        self.assertTrue((main.DATA/'originals'/f"{milk['id']}.json").exists())
        self.assertEqual((await self.client.post('/bls/meals',json=body)).json(),saved)
        # Committed batches replay even if their BLS records disappear later.
        with main.db() as c:c.execute('DELETE FROM foods')
        self.assertEqual((await self.client.post('/bls/meals',json=body)).json(),saved)
        body['timestamp']='2026-11-04T12:15:00+01:00'
        self.assertEqual((await self.client.post('/bls/meals',json=body)).status_code,422)
        self.assertEqual(len((await self.client.get('/entries')).json()),2)

    async def test_validation_auth_and_no_partial_writes(self):
        self.seed();body=self.meal()
        for url in ['/bls/meals','/bls/meals/preview']:
            self.assertEqual((await self.client.post(url,json=body,headers={'Authorization':'bad'})).status_code,401)
        self.assertEqual((await self.client.get('/bls/search',params={'q':'Salz'},headers={'Authorization':'bad'})).status_code,401)
        for update in [{'timestamp':'2026-11-03T12:00:00'},{'items':[]},{'items':[{'bls_code':'SALT','grams':0}]},
                       {'items':[{'bls_code':'SALT','grams':2,'unit':'ml'}]}, {'nutrients':{}},
                       {'items':[body['items'][0],{'bls_code':'UNKNOWN','grams':20}]}]:
            for url in ['/bls/meals','/bls/meals/preview']:
                response=await self.client.post(url,json={**body,**update})
                self.assertEqual(response.status_code,422,response.text)
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual(list((main.DATA/'originals').iterdir()),[])
        self.assertEqual((await self.client.get('/bls/search',params={'q':' '})).status_code,422)
        self.assertEqual((await self.client.get('/bls/search',params={'q':'Salz','limit':101})).status_code,422)
        self.assertEqual((await self.client.get('/bls/search',params={'q':'notfound'})).json()['results'],[])

    async def test_same_meal_at_different_time_is_new_and_unknown_values_preserved(self):
        self.seed();body=self.meal()
        first=(await self.client.post('/bls/meals',json=body)).json()
        body['timestamp']='2026-11-03T18:00:00+01:00'
        second=(await self.client.post('/bls/meals',json=body)).json()
        self.assertNotEqual(first['id'],second['id'])
        self.assertEqual(len((await self.client.get('/entries')).json()),4)
        milk=(await self.client.get('/entries/'+first['entry_ids'][0])).json()
        self.assertNotIn('dietaryVitaminC',milk['nutrients'])
        self.assertEqual(milk['food']['nutrients']['dietaryVitaminC'],'TR')
        self.assertIn('bls_code',main.app.openapi()['components']['schemas']['BLSItem']['properties'])
