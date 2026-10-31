import io,json,zipfile
import unittest
from uuid import uuid4
from unittest.mock import AsyncMock,patch
import test_api as support
from app import main,off_search

class SearchPreferenceTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown

    async def setup_food(self):
        for code,name in [('SUGAR','Haushaltszucker raffiniert'),('MILK','Vollmilch')]:
            food={'bls_code':code,'name_de':name,'name_en':'Refined sugar' if code=='SUGAR' else 'Whole milk','nutrients':{'dietaryEnergyConsumed':400}}
            with main.db() as c:c.execute('INSERT INTO foods VALUES(?,?,?)',(code,json.dumps(food),main.normalize(name+' '+food['name_en'])))

    def alias(self,query='Backwürfel',code='SUGAR',lang='de'):return {'id':str(uuid4()),'query':query,'lang':lang,'bls_code':code,'version':0}

    async def test_non_name_alias_prefix_language_ranking_and_selection_learning(self):
        await self.setup_food();body=self.alias();r=await self.client.post('/food-search/synonyms',json=body);self.assertEqual(r.status_code,201,r.text)
        self.assertEqual((await self.client.post('/food-search/synonyms',json=body)).json(),r.json())
        for query in ['Backwürfel','BACKWÜRFEL','backw']:
            foods=(await self.client.get('/foods',params={'q':query,'lang':'de'})).json();self.assertEqual(foods[0]['bls_code'],'SUGAR')
            shared=(await self.client.get('/search',params={'q':query,'lang':'de','remote':'false'})).json()['results'];self.assertEqual(shared[0]['id'],'SUGAR')
        self.assertEqual((await self.client.get('/foods',params={'q':'Backwürfel','lang':'en'})).json(),[])
        self.assertEqual((await self.client.post('/food-search/selections',json={'id':str(uuid4()),'query':'Backwürfel','lang':'de','bls_code':'SUGAR'})).status_code,200)
        with patch.object(off_search,'search',AsyncMock(return_value=[{'barcode':'4001234567890','display_name':'Backwürfel Produkt','brand':'','package_quantity':''}])):
            search=(await self.client.get('/search',params={'q':'Backwürfel'})).json()
        product=next(x for x in search['results'] if x['source']=='off')
        for _ in range(5):await self.client.post('/search/selections',json={'id':str(uuid4()),'query':'Backwürfel','token':product['selection_token']})
        pinned=(await self.client.get('/search',params={'q':'Backwürfel','remote':'false'})).json()['results'];self.assertEqual(pinned[0]['id'],'SUGAR')
        wildcard=self.alias('%Literal');await self.client.post('/food-search/synonyms',json=wildcard)
        self.assertEqual((await self.client.get('/foods',params={'q':'%'})).json()[0]['bls_code'],'SUGAR')
        self.assertEqual((await self.client.get('/foods',params={'q':'_'})).json(),[])

    async def test_alias_edit_delete_validation_and_auth(self):
        await self.setup_food();body=self.alias();row=(await self.client.post('/food-search/synonyms',json=body)).json();path='/food-search/synonyms/'+row['id']
        self.assertEqual((await self.client.post('/food-search/synonyms',json={**body,'id':str(uuid4())})).status_code,409)
        changed={k:v for k,v in {**body,'query':'Backhilfe','bls_code':'MILK','version':row['version']}.items() if k!='id'}
        r=await self.client.put(path,json=changed);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['version'],2)
        self.assertEqual((await self.client.put(path,json=changed)).status_code,409)
        self.assertEqual((await self.client.get('/foods',params={'q':'Backwürfel'})).json(),[])
        self.assertEqual((await self.client.get('/foods',params={'q':'Backhilfe'})).json()[0]['bls_code'],'MILK')
        self.assertEqual((await self.client.delete(path,params={'version':1})).status_code,409)
        self.assertEqual((await self.client.delete(path,params={'version':2})).status_code,200)
        self.assertEqual((await self.client.get('/foods',params={'q':'Backhilfe'})).json(),[])
        for bad in [self.alias('   '),self.alias(code='MISSING'),{**self.alias(),'lang':'xx'}]:self.assertEqual((await self.client.post('/food-search/synonyms',json=bad)).status_code,422)
        for method,url,payload in [('GET','/food-search/preferences',None),('POST','/food-search/synonyms',self.alias()),('DELETE','/food-search/preferences',{'query':'sugar','lang':'en','source':'bls','target':'SUGAR'})]:
            self.assertEqual((await self.client.request(method,url,json=payload,headers={'Authorization':'bad'})).status_code,401)

    async def test_learned_aggregation_promote_and_delete_both_search_histories(self):
        await self.setup_food();search=(await self.client.get('/search',params={'q':'zucker','remote':'false'})).json()['results'][0]
        await self.client.post('/search/selections',json={'id':str(uuid4()),'query':'zucker','token':search['selection_token']})
        listing=(await self.client.get('/food-search/preferences')).json();self.assertEqual(listing['learned'][0]['count'],1,'same UUID in two tables counts once')
        key={k:listing['learned'][0][k] for k in ['query','lang','source','target']}
        body={**self.alias('Mein Zucker'),'replace_learned':key}
        self.assertEqual((await self.client.post('/food-search/synonyms',json=body)).status_code,201)
        self.assertEqual((await self.client.get('/food-search/preferences')).json()['learned'],[])
        await self.client.post('/search/selections',json={'id':str(uuid4()),'query':'zucker','token':search['selection_token']})
        self.assertEqual((await self.client.request('DELETE','/food-search/preferences',json=key)).status_code,200)
        with main.db() as c:
            self.assertEqual(c.execute('SELECT count(*) FROM food_search_selections').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM search_selections').fetchone()[0],0)
        self.assertEqual((await self.client.get('/food-search/preferences',params={'q':'Vollmilch'})).json()['synonyms'],[])
        self.assertEqual((await self.client.get('/food-search/preferences',params={'q':'Haushaltszucker'})).json()['synonym_count'],1)

    async def test_backup_roundtrip_and_legacy_backup_without_synonym_table(self):
        await self.setup_food();await self.client.post('/food-search/synonyms',json=self.alias())
        archive=(await self.client.get('/backups/export')).content
        with zipfile.ZipFile(io.BytesIO(archive)) as z:files={name:z.read(name) for name in z.namelist()}
        self.assertEqual(len(json.loads(files['backup.json'])['tables']['food_synonyms']),1)
        restored=await self.client.post('/backups/restore',content=archive,headers={'X-Friss-Restore':'replace'});self.assertEqual(restored.status_code,200,restored.text)
        self.assertEqual((await self.client.get('/foods',params={'q':'Backwürfel'})).json()[0]['bls_code'],'SUGAR')
        doc=json.loads(files['backup.json']);doc['tables'].pop('food_synonyms');files['backup.json']=json.dumps(doc).encode();out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:
            for name,data in files.items():z.writestr(name,data)
        restored=await self.client.post('/backups/restore',content=out.getvalue(),headers={'X-Friss-Restore':'replace'});self.assertEqual(restored.status_code,200,restored.text)
        self.assertEqual((await self.client.get('/food-search/preferences')).json()['synonyms'],[])
