"""Explicit personal barcode-to-BLS links; no remote lookup or guessed mapping."""
import json
from datetime import datetime,timezone
from fastapi import Depends,HTTPException,Query
from pydantic import BaseModel,Field,ConfigDict
from typing import Literal

class Link(BaseModel):
    model_config=ConfigDict(extra='forbid')
    version:int=Field(ge=0)
    bls_code:str=Field(min_length=1,max_length=100)

def validate(code):
    if not code.isascii() or not code.isdigit() or not 8<=len(code)<=14:raise HTTPException(422,'Barcode must contain 8–14 digits')

def lookup(c,barcode,required=False,lang='de'):
    validate(barcode)
    row=c.execute('SELECT * FROM barcode_bls_links WHERE barcode=?',(barcode,)).fetchone()
    code=row['code'] if row else None
    food=c.execute('SELECT payload FROM foods WHERE code=?',(code,)).fetchone() if code else None
    result={'barcode':barcode,'version':row['version'] if row else 0,'linked':bool(food),'bls_code':code,'food':None}
    if food:
        f=json.loads(food['payload']);result['food']={k:f[k] for k in ('bls_code','name_de','name_en')};result['food']['display_name']=f['name_'+lang]
    if required and not food:raise HTTPException(409,'Link this barcode to an available BLS food first')
    return result

def install(app,db,auth):
    @app.get('/barcode-bls/{barcode}',dependencies=[Depends(auth)])
    async def get(barcode:str,lang:Literal['de','en']='de'):
        with db() as c:return lookup(c,barcode,lang=lang)
    @app.put('/barcode-bls/{barcode}',dependencies=[Depends(auth)])
    async def save(barcode:str,body:Link):
        validate(barcode)
        with db() as c:
            c.execute('BEGIN IMMEDIATE');old=lookup(c,barcode)
            if not c.execute('SELECT code FROM foods WHERE code=?',(body.bls_code,)).fetchone():raise HTTPException(422,'BLS food not found')
            if old['version']!=body.version:
                if old['version']==body.version+1 and old['bls_code']==body.bls_code:return old
                raise HTTPException(409,'Barcode link changed; reload before saving')
            c.execute('INSERT OR REPLACE INTO barcode_bls_links VALUES(?,?,?,?)',(barcode,body.bls_code,body.version+1,datetime.now(timezone.utc).isoformat()))
            return lookup(c,barcode)
    @app.delete('/barcode-bls/{barcode}',dependencies=[Depends(auth)])
    async def remove(barcode:str,version:int=Query(ge=1)):
        with db() as c:
            c.execute('BEGIN IMMEDIATE');old=lookup(c,barcode)
            if old['version']!=version:raise HTTPException(409,'Barcode link changed; reload')
            c.execute('UPDATE barcode_bls_links SET code=NULL,version=version+1,updated_at=? WHERE barcode=?',(datetime.now(timezone.utc).isoformat(),barcode))
            return lookup(c,barcode)
