"""Recipe planning, stock and unit-safe shopping. Plans are not diary entries."""
from datetime import date,datetime
import hashlib
import json
from typing import Literal
from uuid import UUID,uuid4,uuid5,NAMESPACE_URL
from fastapi import Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field,model_validator

class Settings(BaseModel):
    model_config=ConfigDict(extra='forbid')
    version:int=Field(ge=0)
    planning_enabled:bool=True
    inventory_enabled:bool=True

class Plan(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    version:int=Field(default=0,ge=0)
    day:date
    recipe_id:UUID
    amount:float=Field(gt=0,allow_inf_nan=False)
    unit:Literal['portion','fraction','g','ml']='portion'
    slot:str=Field(default='',max_length=100)
    notes:str=Field(default='',max_length=2000)
    prepared:bool=False

class Stock(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    version:int=Field(default=0,ge=0)
    name:str=Field(min_length=1,max_length=200)
    source:Literal['bls','manual','off','text']='text'
    source_id:str=Field(default='',max_length=100)
    amount:float=Field(ge=0,allow_inf_nan=False)
    unit:Literal['g','ml','piece']='g'
    expires:date|None=None
    notes:str=Field(default='',max_length=2000)
    checked:bool=False
    @model_validator(mode='after')
    def reference(self):
        if self.source!='text' and not self.source_id:raise ValueError('Select a food reference')
        return self

class Eaten(BaseModel):
    timestamp:datetime
    finished_at:datetime|None=None
    @model_validator(mode='after')
    def aware(self):
        if self.timestamp.utcoffset() is None:raise ValueError('Timestamp needs timezone')
        if self.finished_at and (self.finished_at.utcoffset() is None or self.finished_at<self.timestamp):raise ValueError('Invalid finish time')
        return self

class Check(BaseModel):
    checked:bool
    start:date
    end:date

def install(app,db,auth,normalize,load_recipe,details,RecipeIntake,recipe_entry,data_dir):
    def settings(c):
        r=c.execute("SELECT payload FROM planning_records WHERE kind='settings' AND id='settings'").fetchone()
        return json.loads(r['payload']) if r else Settings(version=0).model_dump()
    def enabled(c,kind):
        if not settings(c)[kind+'_enabled']:raise HTTPException(409,kind+' is disabled in Settings')
    def rows(c,kind):return [json.loads(r['payload']) for r in c.execute('SELECT payload FROM planning_records WHERE kind=? ORDER BY rowid',(kind,))]
    def get(c,kind,id):
        r=c.execute('SELECT payload FROM planning_records WHERE kind=? AND id=?',(kind,str(id))).fetchone()
        if not r:raise HTTPException(404,'Record not found')
        return json.loads(r['payload'])
    def write(c,kind,id,value):c.execute('INSERT OR REPLACE INTO planning_records VALUES(?,?,?)',(kind,str(id),json.dumps(value)))
    def save(c,kind,id,body,extra=None):
        try:old=get(c,kind,id)
        except HTTPException:old=None
        value=body.model_dump(mode='json');version=value.pop('version')
        if old:
            if old.get('entry_id'):raise HTTPException(409,'Already eaten; edit the diary entry instead')
            if version!=old['version']:
                if version+1==old['version'] and all(old.get(k)==v for k,v in value.items()):return old
                raise HTTPException(409,'Record changed; reload before saving')
        elif version:raise HTTPException(409,'Record was removed')
        result={**value,'id':str(id),'version':version+1,**(extra or {})}
        write(c,kind,id,result);return result
    def factor(p,r):
        if p['unit']=='fraction':
            if p['amount']>1:raise HTTPException(422,'Fraction must be at most 1')
            return p['amount']
        denominator=r['servings'] if p['unit']=='portion' else r.get('finished_weight_g') if p['unit']=='g' else r.get('finished_volume_ml')
        if not denominator:raise HTTPException(422,'Set finished recipe weight/volume for this unit')
        return p['amount']/denominator
    def identity(e):
        if e.get('bls_code'):return 'bls',e['bls_code']
        if e.get('manual_id'):return 'manual',e['manual_id']
        if e.get('barcode'):return 'off',e['barcode']
        return 'text',normalize(e.get('description') or (e.get('food') or {}).get('name_de') or e.get('drink') or ('entry:'+e['id']))
    def stock_key(s):return (s['source'],s['source_id'] if s['source']!='text' else normalize(s['name']),s['unit'])
    def shopping(c,start,end):
        if end<start or (end-start).days>365:raise HTTPException(422,'Select a range up to 366 days')
        cfg=settings(c);required={};warnings=[]
        if cfg['planning_enabled']:
            for p in rows(c,'plan'):
                if p.get('entry_id') or not start.isoformat()<=p['day']<=end.isoformat():continue
                r=p['snapshot'];scale=factor(p,r)
                for e in r['raw_ingredients']:
                    q=e.get('quantity')
                    if not q:
                        warnings.append(p['name']+': ingredient quantity unknown');continue
                    source,ref=identity(e);key=(source,ref,q['unit'])
                    name=(e.get('food') or {}).get('name_de') or (e.get('food') or {}).get('product_name') or e.get('description') or ref
                    required.setdefault(key,{'name':name,'source':source,'source_id':ref,'unit':q['unit'],'required':0})['required']+=q['value']*scale
                if r.get('added_water_ml'):warnings.append(p['name']+': extra water is not added to shopping')
                if r.get('added_caffeine_mg') or r.get('added_ethanol_g'):warnings.append(p['name']+': pure caffeine/alcohol additions need manual shopping items')
        available={}
        if cfg['inventory_enabled']:
            for s in rows(c,'stock'):
                if s.get('expires') and s['expires']<start.isoformat():continue
                key=stock_key(s);available[key]=available.get(key,0)+s['amount']
        checks={r['id']:r['checked'] for r in rows(c,'check')}
        result=[]
        for key,r in sorted(required.items()):
            have=available.get(key,0);need=max(0,r['required']-have)
            id=hashlib.sha256(json.dumps([key,r['required'],have,start.isoformat(),end.isoformat()]).encode()).hexdigest()
            result.append({**r,'id':id,'available':have,'to_buy':need,'checked':checks.get(id,False),'generated':True})
        manual=[{**s,'to_buy':s['amount'],'generated':False} for s in rows(c,'shopping')]
        return {'start':start,'end':end,'settings':cfg,'items':result+manual,'warnings':sorted(set(warnings))}

    @app.get('/planning/settings',dependencies=[Depends(auth)])
    async def config():
        with db() as c:return settings(c)
    @app.put('/planning/settings',dependencies=[Depends(auth)])
    async def configure(body:Settings):
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if settings(c)['version']!=body.version:raise HTTPException(409,'Settings changed; reload')
            v=body.model_dump();v['version']+=1;write(c,'settings','settings',v);return v
    @app.get('/planning/meals',dependencies=[Depends(auth)])
    async def plans(start:date,end:date):
        with db() as c:
            enabled(c,'planning')
            return sorted([{k:v for k,v in p.items() if k!='snapshot'} for p in rows(c,'plan') if start.isoformat()<=p['day']<=end.isoformat()],key=lambda p:(p['day'],p['slot'],p['id']))
    @app.put('/planning/meals/{id}',dependencies=[Depends(auth)])
    async def plan(id:UUID,body:Plan):
        with db() as c:
            c.execute('BEGIN IMMEDIATE');enabled(c,'planning')
            try:old=get(c,'plan',id)
            except HTTPException:old=None
            # Preserve the planned recipe snapshot when changing scheduling/amount.
            r=old['snapshot'] if old and old['recipe_id']==str(body.recipe_id) else details(load_recipe(body.recipe_id))
            if r['status']!='ready':raise HTTPException(409,'Complete recipe ingredients first')
            factor(body.model_dump(mode='json'),r)
            value=save(c,'plan',id,body,{'snapshot':r,'name':r['name'],'preparation_notes':r.get('notes','')})
            return {k:v for k,v in value.items() if k!='snapshot'}
    @app.post('/planning/meals/{id}/eat',dependencies=[Depends(auth)])
    async def eat(id:UUID,body:Eaten):
        with db() as c:
            c.execute('BEGIN IMMEDIATE');enabled(c,'planning');p=get(c,'plan',id)
            if p.get('entry_id'):
                # Retry never consumes twice, even if the diary entry was deleted.
                return {'entry_id':p['entry_id'],'already_logged':True}
            entry_id=uuid5(NAMESPACE_URL,'friss-plan:'+str(id))
            if c.execute('SELECT id FROM entries WHERE id=?',(str(entry_id),)).fetchone():raise HTTPException(409,'A diary entry already exists for this plan')
            intake=RecipeIntake(id=entry_id,timestamp=body.timestamp,finished_at=body.finished_at,amount=p['amount'],unit=p['unit'])
            e=recipe_entry(p['snapshot'],intake);e['planned_meal_id']=str(id)
            raw={'planned_meal_id':str(id),'recipe':p['recipe_id'],**intake.model_dump(mode='json')}
            path=data_dir()/'originals'/f'{entry_id}.json';text=json.dumps(raw)
            if path.exists() and path.read_text()!=text:raise HTTPException(409,'Original already exists; retry original time')
            if not path.exists():path.write_text(text)
            c.execute('INSERT INTO entries VALUES(?,?,?)',(str(entry_id),hashlib.sha256(text.encode()).hexdigest(),json.dumps(e)))
            p.update(entry_id=str(entry_id),eaten_at=body.timestamp.isoformat(),version=p['version']+1);write(c,'plan',id,p)
            return {'entry_id':str(entry_id),'already_logged':False}
    @app.get('/planning/inventory',dependencies=[Depends(auth)])
    async def inventory():
        with db() as c:enabled(c,'inventory');return rows(c,'stock')
    @app.put('/planning/inventory/{id}',dependencies=[Depends(auth)])
    async def stock(id:UUID,body:Stock):
        with db() as c:
            c.execute('BEGIN IMMEDIATE');enabled(c,'inventory');return save(c,'stock',id,body)
    @app.put('/planning/shopping/{id}',dependencies=[Depends(auth)])
    async def manual(id:UUID,body:Stock):
        with db() as c:c.execute('BEGIN IMMEDIATE');return save(c,'shopping',id,body)
    @app.get('/planning/shopping',dependencies=[Depends(auth)])
    async def groceries(start:date,end:date):
        with db() as c:return shopping(c,start,end)
    @app.put('/planning/check/{id}',dependencies=[Depends(auth)])
    async def check(id:str,body:Check):
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if id not in {r['id'] for r in shopping(c,body.start,body.end)['items'] if r['generated']}:raise HTTPException(409,'Shopping list changed; refresh')
            write(c,'check',id,{'id':id,'checked':body.checked});return {'checked':body.checked}
    @app.delete('/planning/{kind}/{id}',dependencies=[Depends(auth)])
    async def remove(kind:Literal['meals','inventory','shopping'],id:UUID,version:int=Query(ge=1)):
        table={'meals':'plan','inventory':'stock','shopping':'shopping'}[kind]
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if kind!='shopping':enabled(c,'planning' if kind=='meals' else 'inventory')
            old=get(c,table,id)
            if old['version']!=version:raise HTTPException(409,'Record changed; reload')
            c.execute('DELETE FROM planning_records WHERE kind=? AND id=?',(table,str(id)))
        return {'deleted':True}
