import json
import unittest
from uuid import uuid4
from unittest.mock import patch
import httpx
from fastapi import HTTPException
import test_api as support
from app import main,recipe_import

URL='https://www.chefkoch.de/rezepte/393031127655461/Spaghetti-Bolognese.html'
def page():
    recipe={'@type':['Recipe'],'name':'Test &amp; Rezept','recipeYield':['4','4 Portionen'],'recipeIngredient':['500 g Spaghetti','½ kg Tomaten','200 ml Brühe','1 EL Öl','2 Eier','Salz'],
            'recipeInstructions':[{'@type':'HowToSection','name':'Zubereitung','itemListElement':[{'@type':'HowToStep','text':'<p>Alles &amp; gut kochen.</p>'},{'@type':'HowToStep','text':'Servieren.'}]}]}
    return '<script type="application/ld+json">'+json.dumps({'@graph':[{'@type':'Organization'},recipe]})+'</script>'

class RecipeImportTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown

    def commit_body(self):
        preview=recipe_import.parse(page(),URL)
        return {'id':str(uuid4()),'name':preview['name'],'servings':preview['servings'],'notes':preview['notes'],'finished_weight_g':None,'source':preview['source'],'ingredients':preview['ingredients']}

    async def test_parse_and_quantity_rules(self):
        parsed=recipe_import.parse(page(),URL)
        self.assertEqual(parsed['name'],'Test & Rezept');self.assertEqual(parsed['servings'],4)
        self.assertEqual(parsed['ingredients'][0]['quantity'],{'value':500,'unit':'g'})
        self.assertEqual(parsed['ingredients'][1]['quantity'],{'value':500,'unit':'g'})
        self.assertEqual(parsed['ingredients'][2]['quantity'],{'value':200,'unit':'ml'})
        self.assertIsNone(parsed['ingredients'][3]['quantity']);self.assertEqual(parsed['ingredients'][3]['name'],'Öl')
        self.assertEqual(parsed['ingredients'][4]['original_line'],'2 Eier')
        self.assertIn('Alles & gut kochen.',parsed['notes'])
        for value,expected in [('1,5 kg Mehl',1500),('1 1/2 kg Mehl',1500),('1/2 l Milch',500)]:self.assertEqual(recipe_import.ingredient(value)['quantity']['value'],expected)
        for value in ['1/0 kg Mehl','100–200 ml Milch','etwas Pfeffer']:self.assertIsNone(recipe_import.ingredient(value)['quantity'])
        for html in ['<html>No recipe</html>','<script type="application/ld+json">broken</script>']:
            with self.assertRaises(HTTPException):recipe_import.parse(html,URL)

    async def test_preview_live_shape_auth_and_redirect_restrictions(self):
        original=httpx.AsyncClient;calls=[]
        def handler(req):calls.append(str(req.url));return httpx.Response(200,text=page())
        with patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handler),**kw)):
            r=await self.client.post('/recipe-import/preview',json={'url':URL+'?utm_source=test'})
            self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['source']['url'],URL);self.assertEqual(len(calls),1)
            self.assertIn('matches',r.json()['ingredients'][0])
            self.assertEqual((await self.client.post('/recipe-import/preview',json={'url':URL},headers={'Authorization':'bad'})).status_code,401)
        with main.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM recipes').fetchone()[0],0)
        for url in ['https://evil.test/recipe','https://www.chefkoch.de@127.0.0.1/rezepte/1/a.html','https://www.chefkoch.de:444/rezepte/1/a.html','https://www.chefkoch.de/user/login']:
            with self.assertRaises(HTTPException):recipe_import.canonical_url(url)
        def redirect(req):return httpx.Response(302,headers={'Location':'https://127.0.0.1/secret'})
        with patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(redirect),**kw)):
            self.assertEqual((await self.client.post('/recipe-import/preview',json={'url':URL})).status_code,422)
        def blocked(req):return httpx.Response(403)
        with patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(blocked),**kw)):
            self.assertEqual((await self.client.post('/recipe-import/preview',json={'url':URL})).status_code,502)

    async def test_commit_review_edit_retry_originals_and_no_diary_entries(self):
        food={'bls_code':'PASTA','name_de':'Spaghetti','name_en':'Spaghetti','nutrients':{'dietaryEnergyConsumed':350}}
        with main.db() as c:c.execute('INSERT INTO foods VALUES(?,?,?)',('PASTA',json.dumps(food),'spaghetti'))
        body=self.commit_body();body['name']='Edited recipe';body['ingredients'][0]['bls_code']='PASTA';body['ingredients'][0]['quantity']['value']=250
        r=await self.client.post('/recipe-import/commit',json=body);self.assertEqual(r.status_code,201,r.text)
        recipe=r.json();self.assertEqual(recipe['name'],'Edited recipe');self.assertEqual(recipe['status'],'needs_review');self.assertEqual(len(recipe['ingredients']),6)
        self.assertEqual(recipe['ingredients'][0]['nutrients']['dietaryEnergyConsumed']['value'],875)
        self.assertEqual(recipe['ingredients'][3]['quantity'],None)
        self.assertEqual(recipe['import_source']['ingredient_lines'][0],'500 g Spaghetti')
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual((await self.client.get('/health-export/pending')).json(),[])
        again=await self.client.post('/recipe-import/commit',json=body);self.assertEqual(again.json(),recipe)
        different={**body,'name':'Different'};self.assertEqual((await self.client.post('/recipe-import/commit',json=different)).status_code,409)
        original=json.loads((main.DATA/'originals'/('recipe-import-'+body['id']+'.json')).read_text());self.assertEqual(original['source']['ingredient_lines'][0],'500 g Spaghetti')
        changed=await self.client.put('/recipes/'+body['id'],json={'name':'Later edit','servings':2,'notes':'new notes'})
        self.assertEqual(changed.status_code,200);self.assertEqual(changed.json()['import_source'],recipe['import_source'])
        duplicate=await self.client.post('/recipes/'+body['id']+'/duplicate',json={'id':str(uuid4()),'name':'Duplicate'});self.assertEqual(duplicate.json()['import_source'],recipe['import_source'])

    async def test_validation_before_writes(self):
        body=self.commit_body();body['ingredients'][0]['bls_code']='NOT_REAL'
        self.assertEqual((await self.client.post('/recipe-import/commit',json=body)).status_code,422)
        body=self.commit_body();body['servings']=0
        self.assertEqual((await self.client.post('/recipe-import/commit',json=body)).status_code,422)
        self.assertEqual((await self.client.post('/recipe-import/commit',json=self.commit_body(),headers={'Authorization':'bad'})).status_code,401)
        with main.db() as c:
            self.assertEqual(c.execute('SELECT count(*) FROM recipes').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM entries').fetchone()[0],0)

    async def test_fetch_same_site_redirect_and_size_limit(self):
        original=httpx.AsyncClient;calls=[]
        def handler(req):
            calls.append(str(req.url))
            if len(calls)==1:return httpx.Response(301,headers={'Location':URL})
            return httpx.Response(200,text=page())
        with patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handler),**kw)):
            r=await self.client.post('/recipe-import/preview',json={'url':URL});self.assertEqual(r.status_code,200);self.assertEqual(len(calls),2)
        def large(req):return httpx.Response(200,text=page())
        with patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(large),**kw)),patch.object(recipe_import,'MAX_BYTES',10):
            self.assertEqual((await self.client.post('/recipe-import/preview',json={'url':URL})).status_code,413)
