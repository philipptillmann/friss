"""Small AI-facing BLS lookup and atomic diary batches; no generated nutrients."""
import hashlib
import json
from datetime import datetime
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from . import food_search

class BLSItem(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    bls_code:str=Field(min_length=1,max_length=100)
    grams:float=Field(gt=0,allow_inf_nan=False)
    notes:str=Field(default='',max_length=2000)

class BLSMeal(BaseModel):
    model_config=ConfigDict(extra='forbid')
    timestamp:datetime
    title:str=Field(default='',max_length=200)
    original_message:str=Field(default='',max_length=10000)
    items:list[BLSItem]=Field(min_length=1,max_length=100)

    @model_validator(mode='after')
    def aware(self):
        if self.timestamp.utcoffset() is None:raise ValueError('Timestamp needs timezone offset')
        return self

def install(app,db,auth,normalize,Entry,process,commit):
    # Import here to keep the existing JSON importer as the single batch writer.
    from .json_import import Item,Meal,Commit,MAX_BYTES

    @app.get('/bls/search',dependencies=[Depends(auth)])
    async def search(q:str=Query(min_length=1,max_length=200),lang:Literal['de','en']='de',limit:int=Query(default=10,ge=1,le=100)):
        foods=food_search.search(db,normalize,q,lang,limit)
        with db() as c:count=c.execute('SELECT COUNT(*) FROM foods').fetchone()[0]
        return {'query':q,'lang':lang,'database_count':count,'results':[
            {'bls_code':f['bls_code'],'name':f['display_name'],'name_de':f['name_de'],'name_en':f['name_en'],
             'quantity_unit':'g','nutrition_basis':'100g','synonym':f.get('synonym')}
            for f in foods]}

    def batch(body):
        raw=body.model_dump_json()
        if len(raw.encode())>MAX_BYTES:raise HTTPException(413,'BLS meal exceeds 256 KiB')
        digest=hashlib.sha256(json.dumps(body.model_dump(mode='json'),sort_keys=True).encode()).hexdigest()
        return uuid5(NAMESPACE_URL,'friss-bls-request:'+digest)

    def prepare(body):
        items=[]
        with db() as c:
            for item in body.items:
                row=c.execute('SELECT payload FROM foods WHERE code=?',(item.bls_code,)).fetchone()
                if not row:raise HTTPException(422,'Unknown BLS code: '+item.bls_code+'; search /bls/search first')
                food=json.loads(row['payload'])
                items.append(Item(name=food['name_de'],bls_code=item.bls_code,quantity={'value':item.grams,'unit':'g'},notes=item.notes))
        return items

    @app.post('/bls/meals/preview',dependencies=[Depends(auth)])
    async def preview(body:BLSMeal):
        batch(body)
        items=prepare(body);result=[]
        for i in items:
            e=Entry(id=uuid5(NAMESPACE_URL,'friss-bls-preview:'+i.bls_code),type='item',timestamp=body.timestamp,
                    bls_code=i.bls_code,quantity=i.quantity.model_dump(),description=i.name).model_dump(mode='json')
            await process(e)
            result.append({'bls_code':i.bls_code,'name':i.name,'grams':i.quantity.value,'notes':i.notes,
                           'status':e['status'],'reason':e.get('reason'),'nutrients':e['nutrients'],'warnings':e['warnings']})
        return {'title':body.title,'timestamp':body.timestamp.isoformat(),'count':len(result),'items':result,'saved':False}

    @app.post('/bls/meals',status_code=201,dependencies=[Depends(auth)])
    async def create(body:BLSMeal):
        id=batch(body)
        # Finished retries remain safe even when a referenced food was removed.
        with db() as c:old=c.execute('SELECT payload FROM json_import_batches WHERE id=?',(str(id),)).fetchone()
        saved=json.loads(old['payload']) if old else None
        if not saved or saved['status']!='completed':
            items=prepare(body)
            meal=Meal(schema='friss-meal-v1',title=body.title,original_message=body.original_message,items=items)
            saved=await commit(Commit(id=id,raw=meal.model_dump_json(by_alias=True),timestamp=body.timestamp,items=items))
        return {**saved,'title':body.title,'timestamp':body.timestamp.isoformat(),'source':'BLS'}
