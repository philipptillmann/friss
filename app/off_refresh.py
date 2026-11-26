"""Detect empty OFF profiles and explicitly refresh a single retained snapshot."""
import copy
import json
import math
from uuid import UUID
from fastapi import Depends,HTTPException
from pydantic import BaseModel,Field

# Actual nutrient fields only: nutrition scores and other product metadata must
# not hide an otherwise empty nutrition profile. Check original per-100g data.
NUTRIENTS=set(('energy energy-kcal energy-kj fat saturated-fat monounsaturated-fat polyunsaturated-fat trans-fat cholesterol carbohydrates sugars added-sugars starch polyols fiber proteins salt sodium caffeine water alcohol vitamin-a beta-carotene vitamin-d vitamin-e vitamin-k vitamin-c vitamin-b1 vitamin-b2 vitamin-pp vitamin-b6 vitamin-b9 folates vitamin-b12 biotin pantothenic-acid calcium phosphorus iron magnesium potassium chloride zinc copper manganese fluoride selenium chromium molybdenum iodine').split())

def is_off(e):return e.get('type')=='barcode' and e.get('source',{}).get('provider')=='Open Food Facts' and bool(e.get('barcode')) and not e.get('bls_code')

def empty(e):
    if not is_off(e):return False
    raw=(e.get('food') or {}).get('nutriments') or {}
    if not isinstance(raw,dict):return True
    for key in NUTRIENTS:
        value=raw.get(key+'_100g')
        if isinstance(value,bool) or value is None:continue
        try:number=float(value)
        except (TypeError,ValueError):continue
        if math.isfinite(number) and number>0:return False
    return True

def annotate(e):return {**e,'off_nutrition_empty':empty(e)} if is_off(e) else e

class Refresh(BaseModel):
    revision:int=Field(ge=1)

def install(app,db,auth,load,process,data_dir):
    from .json_import import immutable
    def export_state(c,id,e):
        batches=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM health_days')]
        relevant=[b for b in batches if id in b['entry_ids']]
        if e.get('health_status')=='claimed' or any(b['status']=='prepared' for b in relevant):raise HTTPException(409,'Health export in progress; finish or review it before refreshing')
        return e.get('health_status','pending')!='pending' or bool(relevant)
    @app.post('/entries/{id}/refresh-off',dependencies=[Depends(auth)])
    async def refresh(id:UUID,body:Refresh):
        old=load(id)
        if not is_off(old):raise HTTPException(422,'Only direct Open Food Facts entries can be refreshed')
        if old.get('revision',1)!=body.revision:raise HTTPException(409,'Entry changed; reload before refreshing')
        with db() as c:export_state(c,str(id),old)
        e=copy.deepcopy(old);e.pop('food',None);e.pop('source',None)
        try:await process(e,reuse_off=False)
        except (TypeError,ValueError,KeyError,AttributeError):raise HTTPException(502,'Invalid Open Food Facts response; saved entry unchanged')
        if e.get('status')=='failed' or not is_off(e) or not isinstance(e.get('food'),dict) or not e['food']:
            raise HTTPException(502,'Open Food Facts unavailable or product not found; saved entry unchanged')
        # Missing quantity may remain unresolved; updating the product is still useful.
        keys=('food','source','nutrients','status','reason','warnings','ethanol_g')
        changed=any(old.get(k)!=e.get(k) for k in keys)
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            current=c.execute('SELECT payload FROM entries WHERE id=?',(str(id),)).fetchone()
            if not current:raise HTTPException(404,'Entry no longer exists')
            current=json.loads(current['payload'])
            if current!=old:raise HTTPException(409,'Entry changed during refresh; reload before retrying')
            health=export_state(c,str(id),current)
            if changed:
                immutable(data_dir()/'originals'/f"{id}-revision-{old.get('revision',1)}.json",json.dumps(old,ensure_ascii=False))
                e['revision']=old.get('revision',1)+1
                c.execute('UPDATE entries SET payload=? WHERE id=?',(json.dumps(e),str(id)))
        return {'entry':annotate(e if changed else old),'changed':changed,'health_correction_required':health and changed}
