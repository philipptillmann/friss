"""Explicit BLS aliases and management of automatically learned search choices."""
import json
import sqlite3
from typing import Literal
from uuid import UUID
from fastapi import Depends,HTTPException,Query
from pydantic import BaseModel,Field,model_validator
from . import food_search

class LearnedKey(BaseModel):
    query:str=Field(min_length=1,max_length=200)
    lang:Literal['de','en']
    source:Literal['bls','off','manual','recipe','favorite']
    target:str=Field(min_length=1,max_length=200)

class AliasEdit(BaseModel):
    query:str=Field(min_length=1,max_length=80)
    lang:Literal['de','en']
    bls_code:str=Field(min_length=1,max_length=100)
    version:int=Field(ge=0)
    replace_learned:LearnedKey|None=None
    @model_validator(mode='after')
    def valid(self):
        self.query=' '.join(self.query.split())
        if not self.query:raise ValueError('Search term required')
        return self

class AliasCreate(AliasEdit):
    id:UUID

def forget(c,key,normalize):
    query=food_search.term(key.query,normalize)
    if key.source=='bls':c.execute('DELETE FROM food_search_selections WHERE query=? AND lang=? AND code=?',(query,key.lang,key.target))
    c.execute('DELETE FROM search_selections WHERE query=? AND lang=? AND source=? AND target=?',(query,key.lang,key.source,key.target))

def view(row,c):
    row=dict(row)
    food=c.execute('SELECT payload FROM foods WHERE code=?',(row['code'],)).fetchone()
    payload=json.loads(food['payload']) if food else {}
    return {'id':row['id'],'query':row['label'],'normalized_query':row['query'],'lang':row['lang'],'bls_code':row['code'],'version':row['version'],'name_de':payload.get('name_de',row['code']),'name_en':payload.get('name_en',row['code']),'missing':food is None}

def install(app,db,auth,normalize):
    @app.get('/food-search/preferences',dependencies=[Depends(auth)])
    async def preferences(q:str=Query(default='',max_length=200)):
        query=food_search.term(q,normalize)
        with db() as c:
            aliases=[view(row,c) for row in c.execute('SELECT * FROM food_synonyms ORDER BY label,lang,code').fetchall()]
            # BLS clicks from shared search exist in both tables under the same UUID.
            raw=c.execute("SELECT id,query,lang,'bls' AS source,code AS target,NULL AS payload FROM food_search_selections UNION ALL SELECT id,query,lang,source,target,payload FROM search_selections").fetchall()
            grouped={};seen=set()
            for row in raw:
                unique=(row['id'],row['query'],row['lang'],row['source'],row['target'])
                if unique in seen:continue
                seen.add(unique);key=(row['query'],row['lang'],row['source'],row['target'])
                if key not in grouped:grouped[key]={'query':row['query'],'lang':row['lang'],'source':row['source'],'target':row['target'],'count':0,'cached':None}
                item=grouped[key];item['count']+=1
                if row['payload']:item['cached']=json.loads(row['payload'])
            learned=[]
            for item in grouped.values():
                table,column={'bls':('foods','code'),'manual':('manual_ingredients','id'),'recipe':('recipes','id'),'favorite':('favorites','id')}.get(item['source'],(None,None))
                stored=c.execute('SELECT payload FROM '+table+' WHERE '+column+'=?',(item['target'],)).fetchone() if table else None
                record=json.loads(stored['payload']) if stored else item['cached'] or {}
                item.update(name_de=record.get('name_de') or record.get('name') or record.get('label') or item['target'],name_en=record.get('name_en') or record.get('name') or record.get('label') or item['target'],category=record.get('category','food'))
                item.pop('cached');learned.append(item)
        def matches(item):return not query or any(query in food_search.term(str(item.get(k,'')),normalize) for k in ('query','name_de','name_en','bls_code','target'))
        aliases=[a for a in aliases if matches(a)];learned=[a for a in learned if matches(a)];learned.sort(key=lambda a:(a['query'],a['lang'],-a['count'],a['source'],a['target']))
        return {'synonyms':aliases[:200],'learned':learned[:200],'synonym_count':len(aliases),'learned_count':len(learned)}

    def save(c,id,body,creating):
        query=food_search.term(body.query,normalize)
        if not query:raise HTTPException(422,'Search term required')
        if not c.execute('SELECT code FROM foods WHERE code=?',(body.bls_code,)).fetchone():raise HTTPException(422,'BLS food no longer exists')
        old=c.execute('SELECT * FROM food_synonyms WHERE id=?',(str(id),)).fetchone()
        if creating and old:
            if (old['label'],old['lang'],old['code'])!=(body.query,body.lang,body.bls_code):raise HTTPException(409,'Synonym ID already used')
            return view(old,c)
        if creating and body.version!=0:raise HTTPException(422,'New synonym version must be 0')
        if not creating and not old:raise HTTPException(404,'Synonym not found')
        if not creating and old['version']!=body.version:raise HTTPException(409,'Synonym changed; reload before editing')
        try:
            if creating:c.execute('INSERT INTO food_synonyms VALUES(?,?,?,?,?,?)',(str(id),query,body.query,body.lang,body.bls_code,1))
            else:c.execute('UPDATE food_synonyms SET query=?,label=?,lang=?,code=?,version=version+1 WHERE id=?',(query,body.query,body.lang,body.bls_code,str(id)))
        except sqlite3.IntegrityError:raise HTTPException(409,'This search term already refers to this BLS food')
        if body.replace_learned:forget(c,body.replace_learned,normalize)
        return view(c.execute('SELECT * FROM food_synonyms WHERE id=?',(str(id),)).fetchone(),c)

    @app.post('/food-search/synonyms',status_code=201,dependencies=[Depends(auth)])
    async def create(body:AliasCreate):
        with db() as c:c.execute('BEGIN IMMEDIATE');return save(c,body.id,body,True)

    @app.put('/food-search/synonyms/{id}',dependencies=[Depends(auth)])
    async def update(id:UUID,body:AliasEdit):
        with db() as c:c.execute('BEGIN IMMEDIATE');return save(c,id,body,False)

    @app.delete('/food-search/synonyms/{id}',dependencies=[Depends(auth)])
    async def delete(id:UUID,version:int=Query(ge=1)):
        with db() as c:
            c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT version FROM food_synonyms WHERE id=?',(str(id),)).fetchone()
            if not row:raise HTTPException(404,'Synonym not found')
            if row['version']!=version:raise HTTPException(409,'Synonym changed; reload before deleting')
            c.execute('DELETE FROM food_synonyms WHERE id=?',(str(id),))
        return {'deleted':True}

    @app.delete('/food-search/preferences',dependencies=[Depends(auth)])
    async def delete_learned(body:LearnedKey):
        with db() as c:c.execute('BEGIN IMMEDIATE');forget(c,body,normalize)
        return {'deleted':True}
