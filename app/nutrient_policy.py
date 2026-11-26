"""Reversible, opt-in interpretation of blank nutrient values as zero.

Source payloads are never changed. The opt-in includes trace / detection-limit
qualifiers. Unknown food identities, amounts and unverified numeric units remain.
"""
import json
import re
from .bls_units import UNITS

ZERO_UNITS={**UNITS,'dietarySelenium':'mcg','dietaryCaffeine':'mg'}

def enabled(db=None,connection=None):
    if connection is not None:
        row=connection.execute('SELECT payload FROM preferences WHERE id=1').fetchone()
    else:
        with db() as c:row=c.execute('SELECT payload FROM preferences WHERE id=1').fetchone()
    return bool(row and json.loads(row['payload']).get('missing_nutrients_as_zero',False))

def ready(e):
    if e.get('status')=='processed':return True
    # Nutrient data may be absent even though identity and amount were resolved.
    q=e.get('quantity') or {}
    expected=(e.get('manual_snapshot') or {}).get('basis_unit','g') if e.get('source',{}).get('provider')=='Manual' else 'g'
    return e.get('status')=='needs_review' and q.get('unit')==expected and q.get('value',0)>0 and bool(e.get('food')) and e.get('source',{}).get('provider') in ('BLS','Manual','Open Food Facts')

def assumable_qualifier(value):
    if value is None:return True
    if not isinstance(value,str):return False
    value=''.join(value.upper().split())
    if not value:return True
    token=r'(?:TR|TRACE|TRACES|SPUR|SPUREN|(?:<=|<|≤)?(?:LOD|LOQ))'
    return bool(re.fullmatch(token+r'(?:(?:OR|ODER|AND|UND|/|,|;)'+token+r')*',value))


def fill(values,water_unit='g'):
    result={k:dict(v) for k,v in values.items()}
    for key,unit in ZERO_UNITS.items():
        old=result.get(key)
        if old is None or old.get('value') is None and assumable_qualifier(old.get('qualifier')):
            result[key]={'value':0,'unit':water_unit if key=='dietaryWater' else unit,'assumed':True}
    return result

OFF_MAP = {'energy-kcal':('dietaryEnergyConsumed','kcal'), 'carbohydrates':('dietaryCarbohydrates','g'), 'fiber':('dietaryFiber','g'), 'sugars':('dietarySugar','g'), 'fat':('dietaryFatTotal','g'), 'saturated-fat':('dietaryFatSaturated','g'), 'proteins':('dietaryProtein','g'), 'sodium':('dietarySodium','g'), 'caffeine':('dietaryCaffeine','g')}

# OFF's normalized *_100g mass fields are in grams, even when *_unit and
# *_value describe a label entered in mg/µg. Never apply that input unit twice.
OFF_LEGACY=set(OFF_MAP)
OFF_NUTRIENTS_VERSION='off-nutrients-v2'
OFF_MAP.update({
    'monounsaturated-fat':('dietaryFatMonounsaturated','g'),
    'polyunsaturated-fat':('dietaryFatPolyunsaturated','g'),
    'cholesterol':('dietaryCholesterol','g'),
    'vitamin-a':('dietaryVitaminA','g'), 'vitamin-d':('dietaryVitaminD','g'),
    'vitamin-e':('dietaryVitaminE','g'), 'vitamin-k':('dietaryVitaminK','g'),
    'vitamin-c':('dietaryVitaminC','g'), 'vitamin-b1':('dietaryThiamin','g'),
    'vitamin-b2':('dietaryRiboflavin','g'), 'vitamin-pp':('dietaryNiacin','g'),
    'pantothenic-acid':('dietaryPantothenicAcid','g'),
    'vitamin-b6':('dietaryVitaminB6','g'), 'biotin':('dietaryBiotin','g'),
    'vitamin-b12':('dietaryVitaminB12','g'),
    'folates':('dietaryFolate','g'), 'vitamin-b9':('dietaryFolate','g'),
    'calcium':('dietaryCalcium','g'), 'chloride':('dietaryChloride','g'),
    'iron':('dietaryIron','g'), 'magnesium':('dietaryMagnesium','g'),
    'phosphorus':('dietaryPhosphorus','g'), 'potassium':('dietaryPotassium','g'),
    'zinc':('dietaryZinc','g'), 'chromium':('dietaryChromium','g'),
    'copper':('dietaryCopper','g'), 'iodine':('dietaryIodine','g'),
    'manganese':('dietaryManganese','g'), 'molybdenum':('dietaryMolybdenum','g'),
    'selenium':('dietarySelenium','g'), 'water':('dietaryWater','g')
})
OFF_DISPLAY_MG=set(('Cholesterol VitaminE VitaminC Thiamin Riboflavin Niacin PantothenicAcid VitaminB6 Calcium Chloride Iron Magnesium Phosphorus Potassium Zinc Copper Manganese').split())
OFF_DISPLAY_MCG=set(('VitaminA VitaminD VitaminK Biotin VitaminB12 Folate Chromium Iodine Molybdenum Selenium').split())

def off_nutrients(raw,extended=True):
    """Per-100g nutrients with canonical display units; aliases are not summed."""
    if not isinstance(raw,dict):raise ValueError('Invalid OFF nutriments')
    result={}
    for source,(key,unit) in OFF_MAP.items():
        if not extended and source not in OFF_LEGACY:continue
        value=raw.get(source+'_100g')
        # Prefer the primary folate field, including a known zero. Fall back only
        # when absent/null, not by adding folate variants together.
        if key in result and result[key]['value'] is not None:continue
        factor=1
        name=key.removeprefix('dietary')
        if name in OFF_DISPLAY_MG:factor=1000;unit='mg'
        elif name in OFF_DISPLAY_MCG:factor=1_000_000;unit='mcg'
        if isinstance(value,(int,float)) and not isinstance(value,bool):value*=factor
        result[key]={'value':value,'unit':unit}
    return result
