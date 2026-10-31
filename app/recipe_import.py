"""Chefkoch public Recipe JSON-LD import, reviewed before atomic recipe creation."""
import hashlib
import json
import math
import re
from datetime import datetime,timezone
from fractions import Fraction
from html import unescape
from html.parser import HTMLParser
from typing import Literal
from urllib.parse import urljoin,urlsplit
from uuid import UUID,uuid5
import httpx
from fastapi import Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from . import food_search
from .json_import import Quantity,immutable

MAX_BYTES=4*1024*1024

def canonical_url(value):
    try:
        u=urlsplit(value.strip())
        if u.scheme not in ('https','http') or u.hostname not in ('www.chefkoch.de','chefkoch.de') or u.username or u.password or u.port not in (None,443):raise ValueError()
        if not re.fullmatch(r'/rezepte/\d{1,25}/[^/]{1,300}\.html',u.path):raise ValueError()
    except ValueError:raise HTTPException(422,'Bitte einen Chefkoch-Rezeptlink verwenden: https://www.chefkoch.de/rezepte/…/….html')
    return 'https://www.chefkoch.de'+u.path

class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)
    def handle_starttag(self,tag,attrs):
        if tag in ('br','p','li'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('p','li'):self.parts.append('\n')

def clean(value):
    p=Text();p.feed(unescape(str(value)));return '\n'.join(' '.join(line.split()) for line in ''.join(p.parts).splitlines() if line.strip())

class Page(HTMLParser):
    def __init__(self):super().__init__();self.active=False;self.current=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script' and dict(attrs).get('type','').lower()=='application/ld+json':self.active=True;self.current=[]
    def handle_data(self,data):
        if self.active:self.current.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.active:self.scripts.append(''.join(self.current));self.active=False

def nodes(value,depth=0):
    if depth>25:return
    if isinstance(value,list):
        for item in value:yield from nodes(item,depth+1)
    if isinstance(value,dict):
        kind=value.get('@type',[]);kind=[kind] if isinstance(kind,str) else kind
        if isinstance(kind,list) and any(isinstance(k,str) and k.rstrip('/').split('/')[-1]=='Recipe' for k in kind):yield value
        for key in ('@graph','mainEntity','itemListElement'):
            yield from nodes(value.get(key),depth+1)

def instructions(value,depth=0):
    if depth>25:return []
    if isinstance(value,str):return [clean(value)]
    if isinstance(value,list):return [text for v in value for text in instructions(v,depth+1)]
    if isinstance(value,dict):
        result=[]
        if value.get('name') and not value.get('text'):result.append(clean(value['name']))
        if value.get('text'):result.append(clean(value['text']))
        result.extend(instructions(value.get('itemListElement',[]),depth+1));return result
    return []

NUMBER=r'(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?|[¼½¾⅓⅔⅛⅜⅝⅞])'
FRACTIONS={'¼':.25,'½':.5,'¾':.75,'⅓':1/3,'⅔':2/3,'⅛':.125,'⅜':.375,'⅝':.625,'⅞':.875}
def number(value):
    if value in FRACTIONS:return FRACTIONS[value]
    try:return sum(float(Fraction(part.replace(',','.'))) for part in value.split())
    except (ValueError,ZeroDivisionError,OverflowError):return 0

def ingredient(line):
    line=clean(line);name=line;quantity=None
    match=re.match(r'^('+NUMBER+r')\s*(kg|mg|g|ml|cl|dl|l)\b\s*(.+)$',line,re.I)
    if match:
        amount=number(match[1]);unit=match[2].lower();name=match[3]
        scale={'kg':1000,'mg':.001,'g':1,'ml':1,'cl':10,'dl':100,'l':1000}[unit]
        if amount>0 and math.isfinite(amount*scale):quantity={'value':amount*scale,'unit':'g' if unit in ('kg','g','mg') else 'ml'}
    else:
        # Counts/spoons are retained in the original, never guessed as grams.
        name=re.sub(r'^'+NUMBER+r'\s+(?:(?:EL|TL|Stück|Stk\.?|Zehe/n|Dose/n|Pck\.?)\s+)?','',line,flags=re.I) or line
    return {'name':name,'original_line':line,'quantity':quantity}

def parse(html,url):
    page=Page();page.feed(html);recipe=None
    for script in page.scripts:
        try:recipe=next(nodes(json.loads(script)),None)
        except (ValueError,RecursionError):continue
        if recipe:break
    if not recipe:raise HTTPException(422,'Keine strukturierten Rezeptdaten auf dieser Chefkoch-Seite gefunden.')
    title=clean(recipe.get('name',''));lines=recipe.get('recipeIngredient')
    if not title or len(title)>200 or not isinstance(lines,list) or not 1<=len(lines)<=200 or any(not isinstance(s,str) or not s.strip() or len(s)>1000 for s in lines):raise HTTPException(422,'Rezeptname oder Zutatenliste fehlt oder ist zu groß.')
    steps='\n\n'.join(instructions(recipe.get('recipeInstructions',[])))
    if len(steps)>20000:raise HTTPException(422,'Zubereitung ist zu lang für den Import.')
    yields=recipe.get('recipeYield',[]);yields=yields if isinstance(yields,list) else [yields]
    yield_text=' / '.join(str(y) for y in yields);servings=None
    for y in yields:
        match=re.match(r'^\s*('+NUMBER+r')(?=\s|$)',str(y))
        if match:
            value=number(match[1])
            if math.isfinite(value) and value>0:servings=value;break
    source={'provider':'Chefkoch','retrieved_at':datetime.now(timezone.utc).isoformat(),'url':url,'original_title':title,'yield_text':yield_text[:1000],'ingredient_lines':[clean(s) for s in lines],'instructions':steps}
    return {'name':title,'servings':servings,'notes':('Chefkoch: '+url+'\n\n'+steps)[:10000],'source':source,'ingredients':[ingredient(s) for s in lines]}

async def fetch(url):
    url=canonical_url(url)
    try:
        async with httpx.AsyncClient(timeout=20,follow_redirects=False,headers={'User-Agent':'Friss/1.35 (self-hosted recipe importer; https://github.com/philipptillmann/friss)','Accept':'text/html'}) as client:
            for _ in range(4):
                async with client.stream('GET',url) as response:
                    if response.status_code in (301,302,303,307,308):
                        url=canonical_url(urljoin(url,response.headers.get('location','')));continue
                    if response.status_code in (401,403,429):raise HTTPException(502,'Chefkoch blockiert den Abruf oder begrenzt Anfragen. Bitte später erneut versuchen.')
                    response.raise_for_status();content=bytearray()
                    async for chunk in response.aiter_bytes():
                        content.extend(chunk)
                        if len(content)>MAX_BYTES:raise HTTPException(413,'Chefkoch-Seite ist zu groß.')
                    return parse(content.decode('utf-8',errors='replace'),url)
            raise HTTPException(502,'Zu viele Chefkoch-Weiterleitungen.')
    except httpx.HTTPError:raise HTTPException(502,'Chefkoch-Rezept konnte nicht geladen werden. Link prüfen und später erneut versuchen.')

class Link(BaseModel):
    url:str=Field(min_length=1,max_length=2000)
    lang:Literal['de','en']='de'

class Source(BaseModel):
    model_config=ConfigDict(extra='forbid')
    provider:Literal['Chefkoch']='Chefkoch'
    url:str
    retrieved_at:datetime
    original_title:str=Field(min_length=1,max_length=200)
    yield_text:str=Field(default='',max_length=1000)
    ingredient_lines:list[str]=Field(min_length=1,max_length=200)
    instructions:str=Field(default='',max_length=20000)
    @model_validator(mode='after')
    def valid(self):
        self.url=canonical_url(self.url)
        if self.retrieved_at.utcoffset() is None:raise ValueError('Source retrieval time needs timezone')
        if any(len(s)>1000 for s in self.ingredient_lines):raise ValueError('Ingredient line too long')
        return self

class Ingredient(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name:str=Field(min_length=1,max_length=1000)
    original_line:str=Field(default='',max_length=1000)
    quantity:Quantity|None=None
    bls_code:str|None=Field(default=None,max_length=100)
    @model_validator(mode='after')
    def valid(self):
        self.name=self.name.strip()
        if not self.name:raise ValueError('Ingredient name required')
        return self

class Commit(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:UUID
    name:str=Field(min_length=1,max_length=200)
    servings:float=Field(gt=0,allow_inf_nan=False)
    notes:str=Field(default='',max_length=10000)
    finished_weight_g:float|None=Field(default=None,gt=0,allow_inf_nan=False)
    source:Source
    ingredients:list[Ingredient]=Field(min_length=1,max_length=200)
    @model_validator(mode='after')
    def valid(self):
        self.name=self.name.strip()
        if not self.name:raise ValueError('Recipe name required')
        return self

def install(app,db,auth,Entry,process,details,data_dir,normalize):
    @app.post('/recipe-import/preview',dependencies=[Depends(auth)])
    async def preview(body:Link):
        result=await fetch(body.url)
        for row in result['ingredients']:
            query=row['name'].split('(')[0].strip()[:200]
            row['matches']=food_search.search(db,normalize,query,body.lang,6) if query else []
        return result

    @app.post('/recipe-import/commit',status_code=201,dependencies=[Depends(auth)])
    async def commit(body:Commit):
        payload=body.model_dump(mode='json');fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        def existing(c):
            row=c.execute('SELECT payload FROM recipes WHERE id=?',(str(body.id),)).fetchone()
            if row:
                recipe=json.loads(row['payload'])
                if recipe.get('import_request_fingerprint')!=fingerprint:raise HTTPException(409,'Import-ID bereits für andere Daten verwendet.')
                return recipe
        with db() as c:old=existing(c)
        if old:return details(old)
        recipe={'id':str(body.id),'name':body.name,'category':'food','servings':body.servings,'notes':body.notes,'finished_weight_g':body.finished_weight_g,'finished_volume_ml':None,'alcohol_abv':None,'added_water_ml':0,'added_caffeine_mg':0,'added_ethanol_g':0,'import_source':{**body.source.model_dump(mode='json'),'imported_at':datetime.now(timezone.utc).isoformat()},'import_request_fingerprint':fingerprint}
        prepared=[]
        for index,row in enumerate(body.ingredients):
            if row.bls_code:
                with db() as c:found=c.execute('SELECT code FROM foods WHERE code=?',(row.bls_code,)).fetchone()
                if not found:raise HTTPException(422,'Gewählter BLS-Eintrag existiert nicht mehr.')
            native=Entry(id=uuid5(body.id,str(index)),type='item' if row.bls_code else 'text',timestamp=body.source.retrieved_at,recipe_id=body.id,description=row.name,quantity=row.quantity.model_dump() if row.quantity else None,bls_code=row.bls_code,capture_method='recipe_import').model_dump(mode='json')
            entry={**native,'status':'unprocessed','health_status':'pending','revision':1,'import_context':{'title':body.source.original_title,'notes':row.original_line,'source_url':body.source.url}}
            await process(entry);prepared.append((native,entry))
        with db() as c:
            c.execute('BEGIN IMMEDIATE');old=existing(c)
            if old:return details(old)
            immutable(data_dir()/'originals'/f'recipe-import-{body.id}.json',json.dumps(payload,sort_keys=True,ensure_ascii=False))
            for native,entry in prepared:
                if c.execute('SELECT id FROM entries WHERE id=?',(entry['id'],)).fetchone():raise HTTPException(409,'Ingredient ID already in use')
                immutable(data_dir()/'originals'/f"{entry['id']}.json",json.dumps({**native,'import_context':entry['import_context']},sort_keys=True,ensure_ascii=False))
                c.execute('INSERT INTO entries VALUES(?,?,?)',(entry['id'],hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest(),json.dumps(entry)))
            c.execute('INSERT INTO recipes VALUES(?,?)',(recipe['id'],json.dumps(recipe)))
        return details(recipe)
