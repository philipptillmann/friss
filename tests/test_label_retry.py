import unittest
from app import label_ocr,main
import test_api as support

CUSTOMER_TEXT='''< 4
Nahrwerte N
Durchschnittliche a
Nährwerte = 9
Energie [kj] 1.273 kJ
Energie [kcal] 302 kcal
Fett 6,69
Fett, davon gesättigte Fettsäuren 21g
Kohlenhydrate 50g
Kohlenhydrate, davon Zucker <4,3g
Eiweiß <9,6g
Salz Aquivalent <1,49
Das Produkt kann von verschiedenen Lieferanten
geliefert werden. daher können die
Filiale.'''

class LabelRetryTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=support.ApiTests.asyncSetUp
    asyncTearDown=support.ApiTests.asyncTearDown

    def test_real_text_missing_header_and_confirmed_basis(self):
        result=label_ocr.parse(CUSTOMER_TEXT)
        self.assertEqual(result['nutrients'],{});self.assertIn('reference_required',result['issues'])
        result=label_ocr.parse(CUSTOMER_TEXT,100,'g');n=result['nutrients']
        self.assertEqual(n['dietaryEnergyConsumed']['value'],302)
        self.assertEqual(n['dietaryCarbohydrates']['value'],50)
        self.assertEqual(n['dietaryFatSaturated']['value'],21) # Never infer a missing decimal.
        for key in ['dietaryFatTotal','dietarySugar','dietaryProtein','dietarySodium']:self.assertNotIn(key,n)
        self.assertIn('ambiguous_or_missing_units',result['issues']);self.assertIn('qualifier_values',result['issues'])

    def test_separate_energy_lines_prioritize_kcal(self):
        for text in ['Per 100 g\nEnergy 1273 kJ\nEnergy 302 kcal','Per 100 g\nEnergy 302 kcal\nEnergy 1273 kJ']:
            self.assertEqual(label_ocr.parse(text)['nutrients']['dietaryEnergyConsumed']['value'],302)
        self.assertAlmostEqual(label_ocr.parse('Per 100 g\nEnergy 418.4 kJ')['nutrients']['dietaryEnergyConsumed']['value'],100)
        self.assertIn('reference_conflict',label_ocr.parse('Per 100 g\nProtein 2 g',6,'g')['issues'])
        self.assertIn('us_label',label_ocr.parse('Nutrition Facts\nTotal carbohydrate 10 g',100,'g')['issues'])

    async def test_reparse_api_preview_no_writes_auth(self):
        url='/manual-ingredients/parse-label';payload={'text':CUSTOMER_TEXT,'reference_amount':100,'reference_unit':'g'}
        response=await self.client.post(url,json=payload)
        self.assertEqual(response.status_code,200,response.text);self.assertEqual(response.json()['nutrients']['dietaryEnergyConsumed']['value'],302)
        corrected=CUSTOMER_TEXT.replace('Fett 6,69','Fett 6,6 g').replace('Fettsäuren 21g','Fettsäuren 2,1 g')
        response=await self.client.post(url,json={**payload,'text':corrected})
        self.assertEqual(response.json()['nutrients']['dietaryFatTotal']['value'],6.6)
        self.assertEqual(response.json()['nutrients']['dietaryFatSaturated']['value'],2.1)
        self.assertEqual((await self.client.get('/manual-ingredients')).json(),[])
        self.assertEqual((await self.client.get('/entries')).json(),[])
        self.assertEqual(list((main.DATA/'originals').iterdir()),[])
        self.assertEqual((await self.client.post(url,json=payload,headers={'Authorization':'bad'})).status_code,401)
        self.assertEqual((await self.client.post(url,json={**payload,'reference_amount':0})).status_code,422)
