import json
from pathlib import Path
import unittest
from unittest.mock import patch
import httpx
import test_api as support
from app import main,nutrient_policy,home,bls_units

FIXTURE=json.loads((Path(__file__).parent/'fixtures/off-4316268448871.json').read_text())

class OFFMicronutrientTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload
    def mock(self,product=FIXTURE):
        original=httpx.AsyncClient
        return patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(lambda req:httpx.Response(200,json=product)),**kw))
    async def food(self,grams=100,**extra):
        with self.mock():r=await self.client.post('/entries',json=self.payload(type='barcode',drink=None,barcode='4316268448871',quantity={'value':grams,'unit':'g'},**extra))
        self.assertEqual(r.status_code,201,r.text);return r.json()

    async def test_real_supplement_units_scaling_and_export(self):
        e=await self.food()
        expected={'dietaryVitaminC':(80,'mg'),'dietaryVitaminE':(12,'mg'),'dietaryNiacin':(16,'mg'),'dietaryPantothenicAcid':(6,'mg'),'dietaryBiotin':(50,'mcg'),'dietaryCalcium':(200,'mg'),'dietaryMagnesium':(112.5,'mg'),'dietaryPhosphorus':(105,'mg'),'dietaryPotassium':(300,'mg')}
        for key,(value,unit) in expected.items():
            self.assertAlmostEqual(e['nutrients'][key]['value'],value,places=8)
            self.assertEqual(e['nutrients'][key]['unit'],unit)
            self.assertEqual(bls_units.exportable(e)[key]['unit'],unit)
        small=await self.food(2)
        self.assertAlmostEqual(small['nutrients']['dietaryVitaminC']['value'],1.6)
        self.assertAlmostEqual(small['nutrients']['dietaryBiotin']['value'],1)
        self.assertNotIn('dietaryVitaminD',e['nutrients'])
        self.assertEqual(e['nutrients']['dietaryFatTotal']['value'],0)
        self.assertEqual(e['source']['nutrients_version'],nutrient_policy.OFF_NUTRIENTS_VERSION)
        self.assertFalse((await self.client.get('/entries/'+e['id'])).json()['off_nutrition_empty'])

    def test_normalized_grams_not_label_units_aliases_and_unknowns(self):
        raw={'vitamin-c_100g':.08,'vitamin-c_unit':'mg','vitamin-c_value':80,
             'biotin_100g':.00005,'biotin_unit':'µg','biotin_value':50,
             'folates_100g':.0002,'vitamin-b9_100g':.0001,
             'vitamin-d_100g':0,'vitamin-b12_100g':None,'iron_100g':'TR',
             'monounsaturated-fat_100g':3,'cholesterol_100g':.02}
        n=nutrient_policy.off_nutrients(raw)
        self.assertAlmostEqual(n['dietaryVitaminC']['value'],80)
        self.assertEqual(n['dietaryBiotin'],{'value':50,'unit':'mcg'})
        self.assertEqual(n['dietaryFolate'],{'value':200,'unit':'mcg'})
        self.assertEqual(n['dietaryVitaminD']['value'],0)
        self.assertIsNone(n['dietaryVitaminB12']['value'])
        self.assertEqual(n['dietaryIron']['value'],'TR')
        self.assertEqual(n['dietaryFatMonounsaturated']['value'],3)
        self.assertEqual(n['dietaryCholesterol'],{'value':20,'unit':'mg'})
        raw.pop('folates_100g');self.assertEqual(nutrient_policy.off_nutrients(raw)['dietaryFolate']['value'],100)
        raw['folates_100g']=0;self.assertEqual(nutrient_policy.off_nutrients(raw)['dietaryFolate']['value'],0)
        self.assertIsNone(nutrient_policy.off_nutrients({'vitamin-c_serving':80})['dietaryVitaminC']['value'])

    async def test_legacy_snapshot_unchanged_until_refresh_and_recipe_totals(self):
        e=await self.food()
        # Emulate a stored v1.46.0 entry retaining the complete upstream product
        # but only its old mapped nutrients. Reading must not amend old exports.
        legacy={**e,'nutrients':{k:v for k,v in e['nutrients'].items() if k in {t for s,(t,u) in nutrient_policy.OFF_MAP.items() if s in nutrient_policy.OFF_LEGACY}}}
        legacy['source']={k:v for k,v in e['source'].items() if k!='nutrients_version'}
        main.save_entry(legacy)
        self.assertNotIn('dietaryVitaminC',home.nutrient_values(main.load_entry(e['id'])))
        with self.mock():r=await self.client.post('/entries/'+e['id']+'/refresh-off',json={'revision':1})
        self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['changed'])
        self.assertEqual(r.json()['entry']['nutrients']['dietaryVitaminC']['value'],80)
        self.assertTrue((main.DATA/'originals'/f"{e['id']}-revision-1.json").exists())
        from uuid import uuid4
        recipe={'id':str(uuid4()),'name':'Supplement mix','servings':2}
        await self.client.post('/recipes',json=recipe)
        await self.food(2,recipe_id=recipe['id'])
        summary=(await self.client.get('/recipes/'+recipe['id'])).json()
        self.assertAlmostEqual(summary['nutrients']['dietaryMagnesium']['value'],2.25)
        portion=await self.client.post('/recipes/'+recipe['id']+'/intake',json={'id':str(uuid4()),'timestamp':'2026-11-26T12:00:00Z','amount':1,'unit':'portion'})
        self.assertEqual(portion.status_code,201,portion.text)
        self.assertAlmostEqual(portion.json()['nutrients']['dietaryVitaminC']['value'],.8)
