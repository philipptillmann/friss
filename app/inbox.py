"""Capture text/photos now, explicitly complete a diary meal later."""
from datetime import datetime,timezone
import hashlib
import json
from typing import Literal
from uuid import UUID,uuid5,NAMESPACE_URL
from fastapi import Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field,model_validator
from . import entry_photos

class Capture(BaseModel):
    model_config=ConfigDict(extra='forbid')
    timestamp:datetime
    text:str=Field(default='',max_length=10000)
    title:str=Field(default='',max_length=200)
    @model_validator(mode='after')
    def aware(self):
        if self.timestamp.utcoffset() is None:raise ValueError('Capture timestamp needs timezone')
        return self

class Complete(BaseModel):
    model_config=ConfigDict(extra='forbid')
    source:Literal['bls','manual','off','recipe']
    source_id:str=Field(min_length=1,max_length=100)
    amount:float=Field(gt=0,allow_inf_nan=False)
    unit:Literal['g','ml','portion','fraction']='g'
    timestamp:datetime|None=None
    finished_at:datetime|None=None
    @model_validator(mode='after')
    def aware(self):
        if self.timestamp is not None and self.timestamp.utcoffset() is None:raise ValueError('Timestamp needs timezone')
        if self.finished_at is not None and self.finished_at.utcoffset() is None:raise ValueError('Finish needs timezone')
        return self

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def install(app,db,auth,Entry,process,load_recipe,details,RecipeIntake,recipe_entry,data_dir):
    def load(id,c=None):
        if c is None:
            with db() as connection:return load(id,connection)
        r=c.execute('SELECT payload FROM inbox_records WHERE id=?',(str(id),)).fetchone()
        if not r:raise HTTPException(404,'Inbox item not found')
        value=json.loads(r['payload'])
        if value.get('deleted'):raise HTTPException(404,'Inbox item not found')
        return value
    def expose(value):
        photos=[{**p,'url':p['url'].replace('/entries/','/inbox/',1)} for p in entry_photos.listing(data_dir(),value['id'])]
        return {**{k:v for k,v in value.items() if k not in ('completion_fingerprint','deleted')},'photos':photos,'photo_upload_url':'/inbox/'+value['id']+'/photos'}
    @app.post('/inbox',status_code=201,dependencies=[Depends(auth)])
    async def capture(body:Capture):
        payload=body.model_dump(mode='json');fingerprint=digest(payload);id=str(uuid5(NAMESPACE_URL,'friss-inbox:'+fingerprint))
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT payload FROM inbox_records WHERE id=?',(id,)).fetchone()
            if old:return expose(json.loads(old['payload'])) if not json.loads(old['payload']).get('deleted') else {'id':id,'status':'deleted'}
            value={**payload,'id':id,'created_at':datetime.now(timezone.utc).isoformat(),'status':'pending'}
            path=data_dir()/'originals'/f'inbox-{id}.json';entry_photos.immutable(path,json.dumps({'id':id,**payload},ensure_ascii=False).encode())
            c.execute('INSERT INTO inbox_records VALUES(?,?,?)',(id,fingerprint,json.dumps(value)))
        return expose(value)
    @app.get('/inbox',dependencies=[Depends(auth)])
    async def inbox(status:Literal['pending','completed','all']='pending',limit:int=Query(default=100,ge=1,le=500),offset:int=Query(default=0,ge=0)):
        with db() as c:values=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM inbox_records')]
        values=sorted([v for v in values if not v.get('deleted') and (status=='all' or v['status']==status)],key=lambda v:(datetime.fromisoformat(v['timestamp']),v['id']),reverse=True)
        return {'total':len(values),'items':[expose(v) for v in values[offset:offset+limit]],'offset':offset,'limit':limit}
    @app.get('/inbox/{id}',dependencies=[Depends(auth)])
    async def item(id:UUID):return expose(load(id))
    @app.delete('/inbox/{id}',dependencies=[Depends(auth)])
    async def remove(id:UUID):
        with db() as c:
            c.execute('BEGIN IMMEDIATE');v=load(id,c);v['deleted']=True
            c.execute('UPDATE inbox_records SET payload=? WHERE id=?',(json.dumps(v),str(id)))
        return {'deleted':True,'diary_unchanged':True}
    @app.post('/inbox/{id}/complete',dependencies=[Depends(auth)])
    async def complete(id:UUID,body:Complete):
        v=load(id);fingerprint=digest(body.model_dump(mode='json'))
        def replay(value):
            if value.get('completion_fingerprint')!=fingerprint:raise HTTPException(409,'Already completed with different data; edit the diary entry')
            return {'id':str(id),'status':'completed','entry_id':value['entry_id']}
        if v['status']=='completed':return replay(v)
        timestamp=body.timestamp or datetime.fromisoformat(v['timestamp']);entry_id=uuid5(NAMESPACE_URL,'friss-inbox-entry:'+str(id))
        if body.finished_at and body.finished_at<timestamp:raise HTTPException(422,'Finish precedes start')
        if body.source=='recipe':
            if body.unit=='fraction' and body.amount>1:raise HTTPException(422,'Fraction must be at most 1')
            try:recipe_id=UUID(body.source_id)
            except ValueError:raise HTTPException(422,'Invalid recipe ID')
            intake=RecipeIntake(id=entry_id,timestamp=timestamp,finished_at=body.finished_at,unit=body.unit,amount=body.amount)
            e=recipe_entry(details(load_recipe(recipe_id)),intake)
        else:
            if body.unit not in ('g','ml'):raise HTTPException(422,'Food amount needs g or ml')
            if body.source=='bls':
                with db() as c:
                    if not c.execute('SELECT code FROM foods WHERE code=?',(body.source_id,)).fetchone():raise HTTPException(422,'Unknown BLS code')
            if body.source=='off' and (not body.source_id.isdigit() or len(body.source_id) not in range(8,15)):raise HTTPException(422,'Invalid barcode')
            if body.source=='manual':
                try:UUID(body.source_id)
                except ValueError:raise HTTPException(422,'Invalid own food ID')
            native=Entry(id=entry_id,type={'bls':'item','manual':'manual','off':'barcode'}[body.source],timestamp=timestamp,finished_at=body.finished_at,
                         quantity={'value':body.amount,'unit':body.unit},description=v['text'] or v['title'],
                         bls_code=body.source_id if body.source=='bls' else None,manual_id=body.source_id if body.source=='manual' else None,barcode=body.source_id if body.source=='off' else None)
            e={**native.model_dump(mode='json'),'health_status':'pending','revision':1}
            await process(e)
            if e['status']!='processed':raise HTTPException(409,e.get('reason') or 'Food lookup failed; draft retained')
        e['inbox_id']=str(id);e['import_context']={'original_message':v['text'],'title':v['title'],'captured_at':v['timestamp'],'inbox_id':str(id)}
        original={'inbox':v,'completion':body.model_dump(mode='json')}
        with db() as c:
            c.execute('BEGIN IMMEDIATE');current=load(id,c)
            if current['status']=='completed':return replay(current)
            if c.execute('SELECT id FROM entries WHERE id=?',(str(entry_id),)).fetchone():raise HTTPException(409,'Diary ID already exists')
            entry_photos.copy(data_dir(),id,entry_id)
            entry_photos.immutable(data_dir()/'originals'/f'{entry_id}.json',json.dumps(original,ensure_ascii=False).encode())
            c.execute('INSERT INTO entries VALUES(?,?,?)',(str(entry_id),digest(original),json.dumps(e)))
            current.update(status='completed',entry_id=str(entry_id),completion_fingerprint=fingerprint)
            c.execute('UPDATE inbox_records SET payload=? WHERE id=?',(json.dumps(current),str(id)))
        return {'id':str(id),'status':'completed','entry_id':str(entry_id)}
    def upload_guard(c,id):
        if load(id,c)['status']!='pending':raise HTTPException(409,'Inbox item already completed; attach new photos to the diary entry')
    entry_photos.install(app,db,auth,load,data_dir,prefix='/inbox',record_table='inbox_records',upload_guard=upload_guard)
