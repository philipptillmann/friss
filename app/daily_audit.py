"""Per-entry nutrient completeness, independent of optional zero assumptions."""
import json
from datetime import date,datetime,time,timedelta
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from fastapi import Depends,HTTPException,Query
from . import home,nutrient_policy,bls_units
from .statistics import METRICS


def cell(raw,unit,assumed=False):
    if not raw:return {'value':None,'unit':unit,'status':'missing','assumed':assumed}
    value=raw.get('value');source_unit=raw.get('unit');qualifier=raw.get('qualifier')
    if not bls_units.numeric(value):return {'value':None,'unit':source_unit or unit,'qualifier':qualifier,'status':'qualifier' if qualifier is not None else 'missing','assumed':assumed}
    status='known'
    if source_unit is None:status='unverified'
    elif source_unit==unit:pass
    elif source_unit in home.MASS and unit in home.MASS:value=value*home.MASS[source_unit]/home.MASS[unit]
    else:status='incompatible'
    return {'value':value,'unit':unit if status=='known' else source_unit,'status':status,'assumed':assumed or bool(raw.get('assumed'))}


def build(records,day,zone,missing_as_zero=False):
    start=datetime.combine(day,time.min,tzinfo=zone);end=datetime.combine(day+timedelta(days=1),time.min,tzinfo=zone)
    selected=[e for e in records if not e.get('recipe_id') and start<=datetime.fromisoformat(e['timestamp'])<end]
    selected.sort(key=lambda e:(datetime.fromisoformat(e['timestamp']),e['id']))
    units={key:unit for key,unit in METRICS.values()}
    units.update(dietaryCaffeine='mg',drinking_water_ml='ml',ethanol_g='g')
    raw_values=[]
    for e in selected:
        values=home.nutrient_values(e,False)
        # Match Home's separation of food water and separately logged drinks.
        water=home.food_water_values(e,False)
        if water:
            first=water[0];unit=first.get('unit')
            if all(bls_units.numeric(n.get('value')) and n.get('unit')==unit for n in water):values['dietaryWater']={'value':sum(n['value'] for n in water),'unit':unit}
            else:values['dietaryWater']={'value':None,'unit':unit,'qualifier':' / '.join((str(n['value'])+' '+str(n.get('unit') or '?')) if bls_units.numeric(n.get('value')) else str(n.get('qualifier') or 'unknown') for n in water)}
        else:values.pop('dietaryWater',None)
        drinking=e.get('drinking_water_ml')
        if e.get('drink')=='water':drinking=(drinking or 0)+e.get('nutrients',{}).get('dietaryWater',{}).get('value',0)
        if drinking is not None:values['drinking_water_ml']={'value':drinking,'unit':'ml'}
        if e.get('ethanol_g') is not None:values['ethanol_g']={'value':e['ethanol_g'],'unit':'g'}
        raw_values.append(values)
        for key,n in values.items():units.setdefault(key,n.get('unit'))
    rows=[]
    for e,values in zip(selected,raw_values):
        effective=home.nutrient_values(e,True) if missing_as_zero and nutrient_policy.ready(e) else {}
        cells={key:cell(values.get(key),unit,bool(effective.get(key,{}).get('assumed'))) for key,unit in units.items()}
        if bls_units.blocked(e):
            for key,n in cells.items():
                if n['status']=='known':cells[key]={**n,'value':values[key]['value'],'unit':values[key].get('unit'),'status':'unverified'}
        food=e.get('food') or {};snapshot=e.get('recipe_snapshot') or {}
        rows.append({'id':e['id'],'timestamp':e['timestamp'],'quantity':e.get('quantity'),'status':e['status'],'health_status':e['health_status'],'type':e['type'],'manual_id':e.get('manual_id'),'bls_code':e.get('bls_code') or food.get('bls_code'),'barcode':e.get('barcode'),'source':e.get('source'),'recipe_snapshot':{'id':snapshot.get('id'),'category':snapshot.get('category','food')} if snapshot else None,'imported_nutrition':{'estimated':True} if e.get('imported_nutrition') else None,'name_de':food.get('name_de') or food.get('product_name') or e.get('description') or e.get('barcode') or e.get('drink') or e['type'],'name_en':food.get('name_en') or food.get('product_name') or e.get('description') or e.get('barcode') or e.get('drink') or e['type'],'cells':cells,'incomplete':sum(n['status']!='known' or n['assumed'] for n in cells.values())})
    totals={}
    for key,unit in units.items():
        known=[r['cells'][key]['value'] for r in rows if r['cells'][key]['status']=='known' and not r['cells'][key]['assumed']]
        totals[key]={'value':sum(known) if known else None,'unit':unit,'incomplete':sum(r['cells'][key]['status']!='known' or r['cells'][key]['assumed'] for r in rows)}
    return {'day':day.isoformat(),'timezone':str(zone),'start':start.isoformat(),'end':end.isoformat(),'missing_nutrients_as_zero':missing_as_zero,'columns':[{'key':key,'unit':unit} for key,unit in units.items()],'rows':rows,'totals':totals}


def install(app,db,auth):
    @app.get('/statistics/day',dependencies=[Depends(auth)])
    async def audit(day:date,tz:str=Query(default='UTC',max_length=100)):
        try:zone=ZoneInfo(tz)
        except (ZoneInfoNotFoundError,ValueError):raise HTTPException(422,'Unknown timezone')
        with db() as c:records=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM entries')]
        return build(records,day,zone,nutrient_policy.enabled(db))
