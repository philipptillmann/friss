import json
import unittest
from uuid import uuid4
import test_api as support
import test_recipes
from app import main

class NestedRecipeTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    setup_recipe=test_recipes.RecipeTests.setup_recipe

    async def recipe(self,name='Parent',**extra):
        body={'id':str(uuid4()),'name':name,'servings':2,**extra}
        r=await self.client.post('/recipes',json=body);self.assertEqual(r.status_code,201,r.text)
        return body
    async def nest(self,parent,child,**extra):
        body={'id':str(uuid4()),'recipe_id':child['id'],'timestamp':'2026-11-24T12:00:00+01:00','unit':'portion','amount':2,**extra}
        r=await self.client.post('/recipes/'+parent['id']+'/ingredients/recipe',json=body)
        return r,body

    async def test_portions_without_weight_snapshot_edit_and_intake(self):
        child,i=await self.setup_recipe(weight=None);parent=await self.recipe()
        r,body=await self.nest(parent,child);self.assertEqual(r.status_code,201,r.text);e=r.json()
        self.assertEqual(e['nutrients']['dietaryEnergyConsumed']['value'],300)
        self.assertEqual(e['recipe_id'],parent['id'])
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual((await self.client.get('/health-export/pending')).json(),[])
        again=await self.client.post('/recipes/'+parent['id']+'/ingredients/recipe',json=body);self.assertEqual(again.json(),e)
        # Amount editing scales the frozen child contribution.
        r=await self.client.patch('/entries/'+e['id']+'/amount',json={'revision':1,'quantity':{'value':1,'unit':'portion'}})
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['nutrients']['dietaryEnergyConsumed']['value'],150)
        # Change current child ingredient; parent remains frozen.
        await self.client.patch('/entries/'+i['id']+'/amount',json={'revision':1,'quantity':{'value':600,'unit':'g'}})
        self.assertEqual((await self.client.get('/recipes/'+parent['id'])).json()['nutrients']['dietaryEnergyConsumed']['value'],150)
        logged=await self.client.post('/recipes/'+parent['id']+'/intake',json={'id':str(uuid4()),'timestamp':body['timestamp'],'unit':'portion','amount':1})
        self.assertEqual(logged.status_code,201,logged.text)
        self.assertEqual(logged.json()['nutrients']['dietaryEnergyConsumed']['value'],75)
        self.assertEqual(len((await self.client.get('/entries')).json()),1)

    async def test_fraction_grams_ml_water_caffeine_alcohol(self):
        child,i=await self.setup_recipe();parent=await self.recipe()
        r,_=await self.nest(parent,child,unit='g',amount=150)
        self.assertEqual(r.status_code,201,r.text);self.assertEqual(r.json()['nutrients']['dietaryEnergyConsumed']['value'],150)
        drink=await self.recipe('Drink',category='drink',finished_volume_ml=400,added_water_ml=200,added_caffeine_mg=100,added_ethanol_g=20)
        middle=await self.recipe('Middle')
        r,_=await self.nest(middle,drink,unit='ml',amount=200);self.assertEqual(r.status_code,201,r.text)
        outer=await self.recipe('Outer');r,_=await self.nest(outer,middle,unit='fraction',amount=.5)
        self.assertEqual(r.status_code,201,r.text)
        d=(await self.client.get('/recipes/'+outer['id'])).json()
        self.assertEqual(d['drinking_water_ml'],50);self.assertEqual(d['ethanol_g'],5)
        self.assertEqual(d['nutrients']['dietaryCaffeine']['value'],25)
        no_weight=await self.recipe('No weight',added_water_ml=100)
        self.assertEqual((await self.nest(parent,no_weight,unit='g',amount=10))[0].status_code,422)
        self.assertEqual((await self.nest(parent,child,unit='fraction',amount=1.1))[0].status_code,422)

    async def test_cycles_auth_and_recursive_shopping(self):
        child,i=await self.setup_recipe();parent=await self.recipe();outer=await self.recipe('Outer')
        self.assertEqual((await self.nest(parent,child))[0].status_code,201)
        self.assertEqual((await self.nest(outer,parent,unit='fraction',amount=.5))[0].status_code,201)
        self.assertEqual((await self.nest(child,outer))[0].status_code,422)
        self.assertEqual((await self.nest(parent,parent))[0].status_code,422)
        body={'id':str(uuid4()),'recipe_id':child['id'],'timestamp':'2026-11-24T12:00:00Z','amount':1,'unit':'portion'}
        self.assertEqual((await self.client.post('/recipes/'+parent['id']+'/ingredients/recipe',json=body,headers={'Authorization':'bad'})).status_code,401)
        await self.client.put('/planning/meals/'+str(uuid4()),json={'day':'2026-11-25','recipe_id':outer['id'],'amount':1,'unit':'fraction'})
        shop=(await self.client.get('/planning/shopping',params={'start':'2026-11-25','end':'2026-11-25'})).json()
        self.assertEqual(len(shop['items']),1);self.assertEqual(shop['items'][0]['required'],75)

    async def test_manual_correction_reaches_nested_snapshots(self):
        food={'id':str(uuid4()),'name_de':'Own','version':0,'nutrients':{'dietaryEnergyConsumed':{'value':100,'unit':'kcal'}}}
        saved=(await self.client.post('/manual-ingredients',json=food)).json()
        child=await self.recipe('Child')
        await self.client.post('/entries',json={'id':str(uuid4()),'timestamp':'2026-11-24T12:00:00Z','type':'manual','manual_id':food['id'],'quantity':{'value':100,'unit':'g'},'recipe_id':child['id']})
        parent=await self.recipe();await self.nest(parent,child,unit='fraction',amount=1)
        logged=(await self.client.post('/recipes/'+parent['id']+'/intake',json={'id':str(uuid4()),'timestamp':'2026-11-24T12:00:00Z','amount':1,'unit':'fraction'})).json()
        response=await self.client.put('/manual-ingredients/'+food['id'],json={**saved,'amend_existing':True,'nutrients':{'dietaryEnergyConsumed':{'value':200,'unit':'kcal'}}})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual((await self.client.get('/entries/'+logged['id'])).json()['nutrients']['dietaryEnergyConsumed']['value'],200)

    async def test_depth_limit(self):
        leaf,_=await self.setup_recipe();current=leaf
        for index in range(7):
            parent=await self.recipe('Level '+str(index))
            response,_=await self.nest(parent,current,unit='fraction',amount=1)
            self.assertEqual(response.status_code,201,response.text)
            current=parent
        parent=await self.recipe('Too deep')
        response,_=await self.nest(parent,current,unit='fraction',amount=1)
        self.assertEqual(response.status_code,422)
