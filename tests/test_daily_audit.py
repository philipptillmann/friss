import json
import unittest
from datetime import date
from uuid import uuid4
from zoneinfo import ZoneInfo
import test_api as support
from app import main,daily_audit

class DailyAuditTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown
    payload=support.ApiTests.payload

    async def test_all_entries_columns_zero_missing_and_assumptions(self):
        own={'id':str(uuid4()),'name_de':'Own food','version':0,'nutrients':{'dietaryEnergyConsumed':{'value':100,'unit':'kcal'},'dietaryProtein':{'value':0,'unit':'g'},'dietarySodium':{'value':.4,'unit':'g'}}}
        await self.client.post('/manual-ingredients',json=own)
        entry=(await self.client.post('/entries',json=self.payload(type='manual',drink=None,manual_id=own['id'],quantity={'value':100,'unit':'g'}))).json()
        recipe={'id':str(uuid4()),'name':'Recipe','servings':1};await self.client.post('/recipes',json=recipe)
        await self.client.post('/entries',json=self.payload(recipe_id=recipe['id']))
        settings=(await self.client.get('/settings')).json();settings['missing_nutrients_as_zero']=True;await self.client.put('/settings',json=settings)
        r=await self.client.get('/statistics/day',params={'day':'2026-10-04','tz':'Europe/Berlin'});self.assertEqual(r.status_code,200,r.text)
        data=r.json();self.assertEqual(len(data['rows']),1);self.assertGreaterEqual(len(data['columns']),40)
        row=data['rows'][0];self.assertEqual(row['id'],entry['id'])
        self.assertEqual(row['cells']['dietaryProtein']['status'],'known');self.assertEqual(row['cells']['dietaryProtein']['value'],0)
        self.assertEqual(row['cells']['dietarySodium']['value'],400);self.assertEqual(row['cells']['dietarySodium']['unit'],'mg')
        self.assertEqual(row['cells']['dietaryFiber']['status'],'missing');self.assertIsNone(row['cells']['dietaryFiber']['value']);self.assertTrue(row['cells']['dietaryFiber']['assumed'])
        self.assertGreater(row['incomplete'],0);self.assertIsNone(data['totals']['dietaryFiber']['value']);self.assertEqual(data['totals']['dietaryProtein']['value'],0)
        self.assertEqual((await self.client.get('/statistics/day',params={'day':'2026-10-04'},headers={'Authorization':'bad'})).status_code,401)
        self.assertEqual((await self.client.get('/statistics/day',params={'day':'2026-10-04','tz':'invalid'})).status_code,422)
        empty=(await self.client.get('/statistics/day',params={'day':'2026-10-06'})).json();self.assertEqual(empty['rows'],[])

    async def test_qualifiers_unverified_units_and_no_volume_mass_guess(self):
        p=self.payload();e=(await self.client.post('/entries',json=p)).json()
        e['source']={'provider':'Manual'};e['nutrients']={'dietaryVitaminC':{'value':None,'unit':'mg','qualifier':'<LOQ'},'dietaryCalcium':{'value':2,'unit':None},'dietaryWater':{'value':20,'unit':'ml'}};e['drink']=None
        main.save_entry(e)
        data=(await self.client.get('/statistics/day',params={'day':'2026-10-04'})).json();cells=data['rows'][0]['cells']
        self.assertEqual(cells['dietaryVitaminC']['status'],'qualifier');self.assertEqual(cells['dietaryVitaminC']['qualifier'],'<LOQ')
        self.assertEqual(cells['dietaryCalcium']['status'],'unverified');self.assertEqual(cells['dietaryWater']['status'],'incompatible')
        e['source']={'provider':'BLS'};e['nutrients']={'dietaryVitaminA':{'value':5,'unit':'g'}};main.save_entry(e)
        cells=(await self.client.get('/statistics/day',params={'day':'2026-10-04'})).json()['rows'][0]['cells']
        self.assertEqual(cells['dietaryVitaminA']['status'],'unverified');self.assertEqual(cells['dietaryVitaminA']['value'],5)

    async def test_timezone_dst_boundaries_and_order(self):
        records=[]
        for stamp in ['2026-03-28T23:30:00+00:00','2026-03-29T21:59:00+00:00','2026-03-29T22:00:00+00:00']:
            records.append({'id':str(uuid4()),'type':'drink','drink':'water','status':'processed','health_status':'pending','timestamp':stamp,'nutrients':{'dietaryWater':{'value':250,'unit':'ml'}}})
        data=daily_audit.build(records,date(2026,3,29),ZoneInfo('Europe/Berlin'))
        self.assertEqual(len(data['rows']),2);self.assertEqual(data['rows'][0]['timestamp'],records[0]['timestamp'])
        self.assertEqual(data['totals']['drinking_water_ml']['value'],500)
        self.assertEqual(data['totals']['dietaryWater']['value'],0)
        self.assertEqual(data['start'],'2026-03-29T00:00:00+01:00');self.assertEqual(data['end'],'2026-03-30T00:00:00+02:00')
