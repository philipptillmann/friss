"""Frozen recipe ingredients with conservative cycle and depth protection."""
import hashlib
import json
from uuid import UUID
from fastapi import Depends,HTTPException
from .json_import import immutable

MAX_DEPTH=8

def snapshot_ids(snapshot,depth=1):
    if depth>MAX_DEPTH:raise HTTPException(422,'Recipe nesting is limited to 8 levels')
    found={snapshot['id']}
    for e in snapshot.get('ingredients',[]):
        if e.get('recipe_snapshot'):found.update(snapshot_ids(e['recipe_snapshot'],depth+1))
    return found

def guard(c,parent,child,snapshot):
    ids=snapshot_ids(snapshot,2)
    if parent in ids:raise HTTPException(422,'A recipe cannot contain itself, directly or indirectly')
    graph={}
    for row in c.execute('SELECT payload FROM entries'):
        e=json.loads(row['payload'])
        if e.get('recipe_id') and e.get('recipe_snapshot'):
            graph.setdefault(e['recipe_id'],set()).update(snapshot_ids(e['recipe_snapshot']))
    pending=[child];seen=set()
    while pending:
        current=pending.pop()
        if current==parent:raise HTTPException(422,'Recipe dependency would create a cycle')
        if current not in seen:seen.add(current);pending.extend(graph.get(current,()))
    # Check the resulting ancestors too: adding a child can deepen an existing chain.
    graph.setdefault(parent,set()).add(child)
    def depth(node,path):
        if node in path:raise HTTPException(422,'Recipe dependency would create a cycle')
        if len(path)>=MAX_DEPTH:raise HTTPException(422,'Recipe nesting is limited to 8 levels')
        for next_id in graph.get(node,()):depth(next_id,path+(node,))
    for node in graph:depth(node,())

def install(app,db,auth,RecipeIntake,load_recipe,details,make_entry,data_dir):
    class Ingredient(RecipeIntake):
        recipe_id:UUID

    @app.post('/recipes/{parent}/ingredients/recipe',status_code=201,dependencies=[Depends(auth)])
    async def add(parent:UUID,body:Ingredient):
        original={'parent_recipe':str(parent),**body.model_dump(mode='json')};fingerprint=hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest()
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT fingerprint,payload FROM entries WHERE id=?',(str(body.id),)).fetchone()
            if old:
                if old['fingerprint']!=fingerprint:raise HTTPException(409,'Ingredient ID already used with different content')
                return json.loads(old['payload'])
            load_recipe(parent)
            r=details(load_recipe(body.recipe_id));guard(c,str(parent),str(body.recipe_id),r)
            e=make_entry(r,body);e['recipe_id']=str(parent)
            immutable(data_dir()/'originals'/f'{body.id}.json',json.dumps(original,ensure_ascii=False))
            c.execute('INSERT INTO entries VALUES(?,?,?)',(str(body.id),fingerprint,json.dumps(e)))
        return e
