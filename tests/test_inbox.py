import io
import json
import unittest
from PIL import Image
from app import main,backups
import test_api as support
import test_recipes

class InboxTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    setup_recipe=test_recipes.RecipeTests.setup_recipe
    def image(self):
        out=io.BytesIO();Image.new('RGB',(12,10),'red').save(out,format='PNG');return out.getvalue()
    async def capture(self,**extra):
        body={'timestamp':'2026-11-10T12:00:00+01:00','text':'  My lunch\nwith photo  ',**extra}
        r=await self.client.post('/inbox',json=body);self.assertEqual(r.status_code,201,r.text)
        return r.json(),body

    async def test_capture_photos_no_nutrition_and_complete_once(self):
        recipe,ingredient=await self.setup_recipe();v,body=await self.capture()
        self.assertEqual((await self.client.post('/inbox',json=body)).json()['id'],v['id'])
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual((await self.client.get('/health-export/pending')).json(),[])
        url=v['photo_upload_url'];raw=self.image()
        image=await self.client.put(url,content=raw,headers={'Content-Type':'image/png'})
        self.assertEqual(image.status_code,200,image.text);photo=image.json()
        self.assertTrue(photo['url'].startswith('/inbox/'))
        self.assertEqual((await self.client.get(photo['url'])).content,raw)
        self.assertEqual((await self.client.put(url,content=raw)).json(),photo)
        self.assertEqual(len((await self.client.get('/inbox/'+v['id'])).json()['photos']),1)
        item=(await self.client.get('/inbox')).json()['items'][0];self.assertEqual(item['text'],body['text'])
        complete={'source':'bls','source_id':'RECIPE_TEST','amount':100,'unit':'g'}
        result=await self.client.post('/inbox/'+v['id']+'/complete',json=complete)
        self.assertEqual(result.status_code,200,result.text);saved=result.json()
        self.assertEqual((await self.client.post('/inbox/'+v['id']+'/complete',json=complete)).json(),saved)
        entry=(await self.client.get('/entries/'+saved['entry_id'])).json()
        self.assertEqual(entry['timestamp'],body['timestamp']);self.assertEqual(entry['import_context']['original_message'],body['text'])
        self.assertEqual(entry['nutrients']['dietaryEnergyConsumed']['value'],200)
        self.assertEqual(entry['health_status'],'pending')
        photos=(await self.client.get('/entries/'+saved['entry_id']+'/photos')).json()
        self.assertEqual((await self.client.get(photos[0]['url'])).content,raw)
        self.assertEqual((await self.client.put(url,content=raw)).status_code,409)
        self.assertEqual((await self.client.get('/inbox')).json()['total'],0)
        self.assertEqual((await self.client.get('/inbox',params={'status':'completed'})).json()['total'],1)
        self.assertEqual((await self.client.post('/inbox/'+v['id']+'/complete',json={**complete,'amount':200})).status_code,409)
        self.assertEqual(len((await self.client.get('/entries')).json()),1)
        await self.client.delete('/inbox/'+v['id'])
        self.assertEqual((await self.client.get(photo['url'])).status_code,404)
        self.assertEqual((await self.client.get('/entries/'+saved['entry_id'])).status_code,200)
        self.assertTrue((main.DATA/'originals'/('inbox-'+v['id']+'.json')).exists())

    async def test_sorting_timezone_pagination_photo_only_and_backup(self):
        a,_=await self.capture(timestamp='2026-11-10T13:00:00+02:00',text='')
        b,_=await self.capture(timestamp='2026-11-10T12:30:00+01:00',text='Later')
        r=(await self.client.get('/inbox',params={'limit':1})).json()
        self.assertEqual(r['total'],2);self.assertEqual(r['items'][0]['id'],b['id'])
        self.assertEqual((await self.client.get('/inbox',params={'offset':1})).json()['items'][0]['id'],a['id'])
        await self.client.put(a['photo_upload_url'],content=self.image())
        doc,files=backups.unpack(backups.build(main.db,main.DATA,'1.43.0'),main.db)
        self.assertEqual(len(doc['tables']['inbox_records']),2)
        self.assertTrue(any('-photo-' in k for k in files))

    async def test_validation_auth_and_pending_after_failure(self):
        recipe,_=await self.setup_recipe();v,_=await self.capture()
        url='/inbox/'+v['id']+'/complete'
        for value in [{'source':'bls','source_id':'missing','amount':10},
                      {'source':'manual','source_id':'notuuid','amount':10},
                      {'source':'recipe','source_id':recipe['id'],'amount':2,'unit':'fraction'},
                      {'source':'bls','source_id':'RECIPE_TEST','amount':0},
                      {'source':'bls','source_id':'RECIPE_TEST','amount':10,'timestamp':'2026-11-10T12:00:00'}]:
            response=await self.client.post(url,json=value);self.assertEqual(response.status_code,422,response.text)
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual((await self.client.get('/inbox')).json()['total'],1)
        self.assertEqual((await self.client.post('/inbox',json={'timestamp':'2026-11-10T12:00:00'})).status_code,422)
        for path in ['/inbox','/inbox/'+v['id'],v['photo_upload_url']]:
            self.assertEqual((await self.client.get(path,headers={'Authorization':'bad'})).status_code,401)
        self.assertEqual((await self.client.put(v['photo_upload_url'],content=b'bad')).status_code,422)
        self.assertEqual((await self.client.post('/inbox',json={'timestamp':'2026-11-10T12:00:00Z'},headers={'Authorization':'bad'})).status_code,401)
        await self.client.delete('/inbox/'+v['id'])
        self.assertEqual((await self.client.put(v['photo_upload_url'],content=self.image())).status_code,404)

    async def test_recipe_completion_actual_time_and_deleted_diary_not_recreated(self):
        recipe,_=await self.setup_recipe();v,_=await self.capture()
        body={'source':'recipe','source_id':recipe['id'],'amount':1,'unit':'portion','timestamp':'2026-11-11T18:00:00+01:00'}
        saved=await self.client.post('/inbox/'+v['id']+'/complete',json=body)
        self.assertEqual(saved.status_code,200,saved.text);saved=saved.json()
        entry=(await self.client.get('/entries/'+saved['entry_id'])).json()
        self.assertEqual(entry['nutrients']['dietaryEnergyConsumed']['value'],150)
        self.assertEqual(entry['timestamp'],body['timestamp'])
        self.assertNotEqual(entry['timestamp'],entry['import_context']['captured_at'])
        await self.client.delete('/entries/'+saved['entry_id'])
        self.assertEqual((await self.client.post('/inbox/'+v['id']+'/complete',json=body)).json(),saved)
        self.assertEqual((await self.client.get('/entries')).json(),[])
