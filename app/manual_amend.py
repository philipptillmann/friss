"""Explicit corrections of manual-food snapshots, including frozen recipe meals."""
import json
from fastapi import HTTPException
from .json_import import immutable

async def amend(c,food,process,recipe_details,recipe_entry,RecipeIntake,data):
    food_id=food['id'];changed=[];direct=0;recipes=0
    async def ingredient(old):
        if old.get('type')!='manual' or old.get('manual_id')!=food_id:return old,False
        if old.get('health_status')=='claimed':raise HTTPException(409,'Health export in progress; finish it before correcting entries')
        q=old.get('quantity')
        if q and q['unit']!=food.get('basis_unit','g'):raise HTTPException(409,'Existing amounts use '+q['unit']+'; changing the reference unit cannot amend history without density conversion')
        entry={**old,'manual_snapshot':food,'revision':old.get('revision',1)+1}
        await process(entry)
        return entry,True
    for row in c.execute('SELECT payload FROM entries').fetchall():
        old=json.loads(row['payload']);entry,updated=await ingredient(old)
        if updated:direct+=1
        if old.get('type')=='recipe' and old.get('recipe_snapshot'):
            snapshot=old['recipe_snapshot'];ingredients=[];affected=False
            for item in snapshot.get('ingredients',[]):
                replacement,touched=await ingredient(item);ingredients.append(replacement);affected|=touched
            if affected:
                if old['health_status']=='claimed':raise HTTPException(409,'Health export in progress; finish it before correcting entries')
                details=recipe_details(snapshot,ingredients=ingredients)
                if details['status']!='ready':raise HTTPException(409,'Recipe snapshot cannot be recalculated; resolve missing ingredient data first')
                q=old['quantity'];replacement=recipe_entry(details,RecipeIntake(id=old['id'],timestamp=old['timestamp'],finished_at=old.get('finished_at'),amount=q['value'],unit=q['unit']))
                keys=('description','source','recipe_snapshot','nutrients','warnings','reason','status','drinking_water_ml','ethanol_g')
                entry={**old,'revision':old.get('revision',1)+1}
                for key in keys:
                    if key in replacement:entry[key]=replacement[key]
                    else:entry.pop(key,None)
                recipes+=1;updated=True
        if updated:changed.append((old,entry))
    for old,entry in changed:
        immutable(data/'originals'/f"{old['id']}-revision-{old.get('revision',1)}.json",json.dumps(old,ensure_ascii=False))
        c.execute('UPDATE entries SET payload=? WHERE id=?',(json.dumps(entry),entry['id']))
    return {'amended_entries':len(changed),'amended_direct_entries':direct,'amended_recipe_entries':recipes}
