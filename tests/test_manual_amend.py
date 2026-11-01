import json
import unittest
from uuid import uuid4
import test_api as support
from app import main

class ManualAmendTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload

    async def setup_uses(self):
        food={'id':str(uuid4()),'name_de':'Testmilch','name_en':'Milk','nutrients':{'dietaryEnergyConsumed':{'value':60,'unit':'kcal'},'dietaryProtein':{'value':3,'unit':'g'}},'version':0,'basis_unit':'g'}
        await self.client.post('/manual-ingredients',json=food)
        direct=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=food['id'],quantity={'value':100,'unit':'g'}))).json()
        recipe={'id':str(uuid4()),'name':'Frozen drink','category':'drink','servings':2,'finished_weight_g':200,'finished_volume_ml':200,'added_caffeine_mg':40}
        await self.client.post('/recipes',json=recipe)
        component=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=food['id'],recipe_id=recipe['id'],quantity={'value':200,'unit':'g'}))).json()
        logged=(await self.client.post('/recipes/'+recipe['id']+'/intake',json={'id':str(uuid4()),'timestamp':direct['timestamp'],'finished_at':'2026-10-04T16:00:00+02:00','unit':'portion','amount':1})).json()
        return food,direct,recipe,component,logged

    def changed(self,food,**kwargs):
        body={k:v for k,v in food.items() if k!='id'}
        return {**body,'name_de':'Corrected milk','nutrients':{'dietaryEnergyConsumed':{'value':100,'unit':'kcal'},'dietaryProtein':{'value':5,'unit':'g'}},'amend_existing':True,**kwargs}

    async def test_amend_direct_recipe_ingredients_and_frozen_meals(self):
        food,direct,recipe,component,logged=await self.setup_uses()
        # Live recipe changed since logging. Retrospective food correction must keep old recipe settings.
        await self.client.put('/recipes/'+recipe['id'],json={'name':'Current drink','category':'drink','servings':4,'finished_weight_g':400,'finished_volume_ml':400,'added_caffeine_mg':100})
        original=(main.DATA/'originals'/(direct['id']+'.json')).read_bytes()
        r=await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food));self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['amended_entries'],3);self.assertEqual(r.json()['amended_recipe_entries'],1)
        changed=main.load_entry(direct['id']);self.assertEqual(changed['nutrients']['dietaryEnergyConsumed']['value'],100)
        self.assertEqual(changed['timestamp'],direct['timestamp']);self.assertEqual(changed['quantity'],direct['quantity']);self.assertEqual(changed['revision'],2)
        ingredient=main.load_entry(component['id']);self.assertEqual(ingredient['nutrients']['dietaryEnergyConsumed']['value'],200)
        meal=main.load_entry(logged['id']);self.assertEqual(meal['nutrients']['dietaryEnergyConsumed']['value'],100)
        self.assertEqual(meal['nutrients']['dietaryCaffeine']['value'],20)
        self.assertEqual(meal['recipe_snapshot']['name'],'Frozen drink');self.assertEqual(meal['recipe_snapshot']['servings'],2)
        self.assertEqual(meal['timestamp'],logged['timestamp']);self.assertEqual(meal['finished_at'],logged['finished_at']);self.assertEqual(meal['quantity'],logged['quantity'])
        self.assertEqual((main.DATA/'originals'/(direct['id']+'.json')).read_bytes(),original)
        self.assertEqual(json.loads((main.DATA/'originals'/(direct['id']+'-revision-1.json')).read_text()),direct)
        self.assertEqual((await self.client.get('/recipes/'+recipe['id'])).json()['name'],'Current drink')
        self.assertEqual((await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food))).status_code,409)

    async def test_future_only_keeps_all_snapshots(self):
        food,direct,recipe,component,logged=await self.setup_uses()
        r=await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food,amend_existing=False));self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['amended_entries'],0)
        for old in [direct,component,logged]:self.assertEqual(main.load_entry(old['id']),old)
        new=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=food['id'],quantity={'value':100,'unit':'g'}))).json();self.assertEqual(new['nutrients']['dietaryEnergyConsumed']['value'],100)

    async def test_claimed_or_unit_conflict_rolls_back_all(self):
        food,direct,recipe,component,logged=await self.setup_uses()
        # A late conflicting recipe meal must roll back earlier direct preparations too.
        e=main.load_entry(logged['id']);e['health_status']='claimed';main.save_entry(e)
        r=await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food));self.assertEqual(r.status_code,409,r.text)
        self.assertEqual(main.load_entry(direct['id']),direct);self.assertEqual(main.load_entry(component['id']),component)
        self.assertEqual((await self.client.get('/manual-ingredients')).json()[0]['version'],0)
        e['health_status']='pending';main.save_entry(e)
        r=await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food,basis_unit='ml'));self.assertEqual(r.status_code,409)
        self.assertEqual(main.load_entry(direct['id']),direct)
        self.assertEqual((await self.client.get('/manual-ingredients')).json()[0]['basis_unit'],'g')

    async def test_export_records_remain_immutable_and_day_changes(self):
        food,direct,recipe,component,logged=await self.setup_uses()
        batch=(await self.client.post('/health-days/prepare',json={'day':'2026-10-04','timezone':'Europe/Berlin'})).json()
        await self.client.post('/health-days/'+batch['id']+'/ack',json={'export_token':batch['export_token'],'success':True})
        r=await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food));self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(main.load_entry(direct['id'])['health_status'],'synced')
        self.assertEqual((await self.client.get('/health-days/'+batch['id'])).json()['samples'],batch['samples'])
        self.assertTrue((await self.client.get('/health-days',params={'tz':'Europe/Berlin'})).json()[0]['changed'])

    async def test_volume_snapshot_and_unknown_amount(self):
        food={'id':str(uuid4()),'name_de':'Drink','basis_unit':'ml','version':0,'nutrients':{'dietaryEnergyConsumed':{'value':33,'unit':'kcal'}}}
        await self.client.post('/manual-ingredients',json=food)
        direct=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=food['id'],quantity={'value':500,'unit':'ml'}))).json()
        unknown=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=food['id'],quantity=None))).json()
        r=await self.client.put('/manual-ingredients/'+food['id'],json=self.changed(food,basis_unit='ml',nutrients={'dietaryEnergyConsumed':{'value':22,'unit':'kcal'}}))
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['amended_entries'],2)
        self.assertEqual(main.load_entry(direct['id'])['nutrients']['dietaryEnergyConsumed']['value'],110)
        self.assertEqual(main.load_entry(direct['id'])['quantity'],direct['quantity'])
        self.assertIsNone(main.load_entry(unknown['id'])['quantity']);self.assertEqual(main.load_entry(unknown['id'])['status'],'needs_review')
