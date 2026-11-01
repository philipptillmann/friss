import unittest
from pathlib import Path
from unittest.mock import AsyncMock,patch
from uuid import uuid4
import httpx
from fastapi import HTTPException
import test_api as support
from app import fddb_import as importer
URL='https://fddb.info/db/de/lebensmittel/naturprodukt_zimt_gemahlen_1053/index.html?nomobile=1'
HTML=Path('tests/fixtures/fddb-cinnamon.html').read_text()

def page(rows,basis='100 g'):
    return "<h1 id='fddb-headline1'>Test food</h1><h2>Nährwerte für "+basis+'</h2>'+''.join("<div><div class='sidrow'><span>"+n+'</span></div><div>'+v+'</div></div>' for n,v in rows)

class FDDBParserTests(unittest.TestCase):
    def test_real_cinnamon_and_units(self):
        result=importer.parse(HTML,URL);n=result['nutrients']
        self.assertEqual(result['name_de'],'Zimt, gemahlen')
        self.assertEqual(n['dietaryEnergyConsumed'],{'value':272,'unit':'kcal'})
        self.assertEqual(n['dietaryCarbohydrates']['value'],56) # No USDA subtraction.
        self.assertEqual(n['dietaryFiber']['value'],24)
        self.assertEqual(n['dietaryWater'],{'value':8,'unit':'g'})
        self.assertEqual(n['dietaryIodine'],{'value':5,'unit':'mcg'})
        self.assertEqual(n['dietaryCalcium']['value'],1228)
        self.assertNotIn('dietaryVitaminC',n)
        self.assertEqual(result['source']['provider'],'FDDB')
        self.assertIsNone(result['source']['carbohydrate_conversion'])

    def test_decimal_unknown_percent_and_portion_scope(self):
        html=page([('Protein','1,25 g'),('Vitamin B12','2,5 μg'),('Kalzium','1.228,5 mg'),('Wassergehalt','8,5%'),('Fett','k. A.'),('Brennwert','418,4 kJ')])
        html+='<h2>Zusammensetzung</h2>'+page([('Protein','999 g')]).split('</h2>')[1]
        n=importer.parse(html,URL)['nutrients']
        self.assertEqual(n['dietaryProtein']['value'],1.25)
        self.assertEqual(n['dietaryVitaminB12']['value'],2.5)
        self.assertEqual(n['dietaryCalcium']['value'],1228.5)
        self.assertEqual(n['dietaryWater']['value'],8.5)
        self.assertAlmostEqual(n['dietaryEnergyConsumed']['value'],100)
        self.assertNotIn('dietaryFatTotal',n)
        for html in [page([('Protein','k. A.')]),page([('Protein','1 g'),('Protein','2 g')]),page([('Wassergehalt','101%')])]:
            with self.assertRaises(HTTPException):importer.parse(html,URL)

    def test_volume_basis(self):
        result=importer.parse(page([('Protein','1 g')],'100 ml'),URL)
        self.assertEqual(result['basis_unit'],'ml')
        self.assertEqual(result['source']['basis_ml'],100)
        self.assertIsNone(result['source']['basis_g'])

    def test_urls(self):
        self.assertEqual(importer.canonical_url(URL+'&tracking=1#x'),URL)
        for url in ['http://fddb.info/db/de/lebensmittel/x/index.html','https://fddb.info.evil/db/de/lebensmittel/x/index.html','https://user@fddb.info/db/de/lebensmittel/x/index.html','https://fddb.info:8443/db/de/lebensmittel/x/index.html','https://fddb.info/db/de/lebensmittel/%2e%2e/index.html','https://fddb.info/db/de/lexikon/x/index.html']:
            with self.assertRaises(HTTPException):importer.canonical_url(url)

class FDDBApiTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload
    async def test_preview_save_intake_and_provenance(self):
        with patch.object(importer,'fetch',AsyncMock(return_value=HTML)) as fetch:
            self.assertEqual((await self.client.post('/manual-ingredients/import',json={'url':URL},headers={'Authorization':'bad'})).status_code,401)
            fetch.assert_not_awaited()
            r=await self.client.post('/manual-ingredients/import',json={'url':URL});self.assertEqual(r.status_code,200)
            fetch.assert_awaited_once_with(URL)
        self.assertEqual((await self.client.get('/manual-ingredients')).json(),[])
        draft=r.json();body={k:draft[k] for k in ['name_de','name_en','notes','nutrients','ethanol_g_per100','source']}
        body.update(id=str(uuid4()),version=0)
        r=await self.client.post('/manual-ingredients',json=body);self.assertEqual(r.status_code,201)
        self.assertEqual(r.json()['source']['url'],URL)
        entry=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=body['id'],quantity={'value':5,'unit':'g'}))).json()
        self.assertEqual(entry['status'],'processed')
        self.assertAlmostEqual(entry['nutrients']['dietaryEnergyConsumed']['value'],13.6)
        self.assertEqual(entry['manual_snapshot']['source']['provider'],'FDDB')
        self.assertAlmostEqual(entry['nutrients']['dietaryCarbohydrates']['value'],2.8)

    async def test_fetch_rejects_redirect_blocks_and_oversize(self):
        original=httpx.AsyncClient
        for status,headers,content,expected in [(200,{'Content-Type':'text/html'},HTML.encode(),None),(302,{'Location':'http://127.0.0.1'},b'',502),(403,{},b'',502),(404,{},b'',404),(200,{'Content-Type':'application/json'},b'{}',422),(200,{'Content-Type':'text/html'},b'x'*(2*1024*1024+1),422)]:
            transport=httpx.MockTransport(lambda request:httpx.Response(status,headers=headers,content=content))
            with patch.object(importer.httpx,'AsyncClient',lambda **kw:original(transport=transport,**kw)):
                if expected:
                    with self.assertRaises(HTTPException) as ctx:await importer.fetch(URL)
                    self.assertEqual(ctx.exception.status_code,expected)
                else:self.assertIn('fddb-headline1',await importer.fetch(URL))


MOBILE_URL='https://fddb.mobi/de/bitburger_bitburger_0_0prozent_alkoholfrei.html'
MOBILE_HTML=Path('tests/fixtures/fddb-bitburger-mobile.html').read_text()

class FDDBMobileTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload

    async def test_mobile_import_save_volume_intake_recipe_and_favorite(self):
        self.assertEqual(importer.canonical_url(MOBILE_URL+'?tracking=1#info'),MOBILE_URL)
        with patch.object(importer,'fetch',AsyncMock(return_value=MOBILE_HTML)):
            r=await self.client.post('/manual-ingredients/import',json={'url':MOBILE_URL})
        self.assertEqual(r.status_code,200,r.text);draft=r.json()
        self.assertEqual(draft['name_de'],'Bitburger, 0,0%, alkoholfrei');self.assertEqual(draft['basis_unit'],'ml')
        self.assertEqual(draft['nutrients']['dietaryEnergyConsumed']['value'],33)
        self.assertEqual(draft['nutrients']['dietaryChloride']['value'],25)
        self.assertEqual(draft['source']['basis_ml'],100);self.assertIsNone(draft['source']['basis_g'])
        body={k:draft[k] for k in ['name_de','name_en','notes','nutrients','ethanol_g_per100','source','basis_unit']};body.update(id=str(uuid4()),version=0)
        saved=await self.client.post('/manual-ingredients',json=body);self.assertEqual(saved.status_code,201,saved.text)
        entry=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=body['id'],quantity={'value':500,'unit':'ml'}))).json()
        self.assertEqual(entry['status'],'processed');self.assertEqual(entry['nutrients']['dietaryEnergyConsumed']['value'],165)
        self.assertEqual(entry['nutrients']['dietaryCarbohydrates']['value'],39)
        self.assertEqual(entry['manual_snapshot']['basis_unit'],'ml')
        wrong=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=body['id'],quantity={'value':500,'unit':'g'}))).json();self.assertEqual(wrong['status'],'needs_review')
        settings=(await self.client.get('/settings')).json();settings['missing_nutrients_as_zero']=True
        await self.client.put('/settings',json=settings)
        self.assertEqual((await self.client.get('/entries/'+wrong['id'])).json()['status'],'needs_review','zero policy must not accept wrong quantity basis')
        favorite={'id':str(uuid4()),'label':'Beer','entry':{'type':'manual','manual_id':body['id'],'quantity':{'value':500,'unit':'ml'}},'version':0}
        self.assertEqual((await self.client.post('/favorites',json=favorite)).status_code,201)
        results=(await self.client.get('/search',params={'q':'Bitburger','remote':'false'})).json()['results'];self.assertEqual(results[0]['basis_unit'],'ml')
        recipe={'id':str(uuid4()),'name':'Beer recipe','category':'drink','servings':1};await self.client.post('/recipes',json=recipe)
        ingredient=self.payload(type='manual',drink=None,manual_id=body['id'],recipe_id=recipe['id'],quantity={'value':500,'unit':'ml'});await self.client.post('/entries',json=ingredient)
        recipes=(await self.client.get('/recipes')).json();self.assertEqual(recipes[0]['nutrients']['dietaryEnergyConsumed']['value'],165)
        # Existing saved snapshots retain ml even if the food definition changes later.
        changed={**body,'basis_unit':'g','version':saved.json()['version']};changed.pop('id')
        self.assertEqual((await self.client.put('/manual-ingredients/'+body['id'],json=changed)).status_code,200)
        from app import main
        e=main.load_entry(entry['id']);await main.process(e);self.assertEqual(e['nutrients']['dietaryEnergyConsumed']['value'],165)

    async def test_mobile_salt_and_redirect_rules(self):
        result=importer.parse(page([('Kalorien','20 kcal'),('Salz','1 g')],'100 ml'),MOBILE_URL)
        self.assertEqual(result['nutrients']['dietarySodium'],{'value':400,'unit':'mg'})
        original=httpx.AsyncClient;calls=[]
        def handler(req):
            calls.append(str(req.url))
            if len(calls)==1:return httpx.Response(301,headers={'Location':MOBILE_URL})
            return httpx.Response(200,headers={'Content-Type':'text/html'},text=MOBILE_HTML)
        with patch.object(importer.httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handler),**kw)):
            self.assertIn('Bitburger',await importer.fetch(URL));self.assertEqual(len(calls),2)
        for url in ['https://fddb.mobi.evil/de/a.html','https://user@fddb.mobi/de/a.html','https://fddb.mobi/de/%2e%2e.html','https://fddb.mobi:444/de/a.html','https://fddb.mobi/account/']:
            with self.assertRaises(HTTPException):importer.canonical_url(url)
