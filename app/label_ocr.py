"""Local nutrition-label OCR. Suggestions only; saving remains explicit."""
import io
import math
import re
import subprocess
import warnings
from fastapi import Depends,HTTPException,Request,Query
from typing import Literal
from pydantic import BaseModel,Field
from PIL import Image,ImageOps,UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

MAX_BYTES=10*1024*1024
# Match longer names first; do not confuse total fat with saturated fat.
LABELS=[
 (r'(?:davon\s+)?gesättigte\s+fettsäuren|saturated\s+(?:fat|fatty acids)','dietaryFatSaturated','g'),
 (r'einfach\s+ungesättigte\s+fettsäuren|monounsaturated\s+fat','dietaryFatMonounsaturated','g'),
 (r'mehrfach\s+ungesättigte\s+fettsäuren|polyunsaturated\s+fat','dietaryFatPolyunsaturated','g'),
 (r'kohlenhydrate|carbohydrates?','dietaryCarbohydrates','g'),
 (r'(?:davon\s+)?zucker|(?:total\s+)?sugars?','dietarySugar','g'),
 (r'ballaststoffe|(?:dietary\s+)?fib(?:re|er)','dietaryFiber','g'),
 (r'eiweiß|eiweiss|protein','dietaryProtein','g'),
 (r'(?:gesamt)?fett|(?:total\s+)?fat','dietaryFatTotal','g'),
 (r'natrium|sodium','dietarySodium','mg'),
 (r'cholesterin|cholesterol','dietaryCholesterol','mg'),
 (r'koffein|caffeine','dietaryCaffeine','mg'),
 (r'kalzium|calcium','dietaryCalcium','mg'),
 (r'magnesium','dietaryMagnesium','mg'),
 (r'eisen|iron','dietaryIron','mg'),
 (r'zink|zinc','dietaryZinc','mg'),
 (r'kalium|potassium','dietaryPotassium','mg'),
 (r'vitamin\s+a','dietaryVitaminA','mcg'),
 (r'vitamin\s+b1|thiamin','dietaryThiamin','mg'),
 (r'vitamin\s+b2|riboflavin','dietaryRiboflavin','mg'),
 (r'vitamin\s+b3|niacin','dietaryNiacin','mg'),
 (r'vitamin\s+b5|pantothens[aä]ure|pantothenic\s+acid','dietaryPantothenicAcid','mg'),
 (r'vitamin\s+b7|biotin','dietaryBiotin','mcg'),
 (r'fols[aä]ure|folic\s+acid|folate|folat','dietaryFolate','mcg'),
 (r'phosphor|phosphorus','dietaryPhosphorus','mg'),
 (r'chlorid|chloride','dietaryChloride','mg'),
 (r'kupfer|copper','dietaryCopper','mg'),
 (r'jod|iodine','dietaryIodine','mcg'),
 (r'selen|selenium','dietarySelenium','mcg'),
 (r'mangan|manganese','dietaryManganese','mg'),
 (r'chrom|chromium','dietaryChromium','mcg'),
 (r'molybd[aä]n|molybdenum','dietaryMolybdenum','mcg'),
 (r'vitamin\s+b12','dietaryVitaminB12','mcg'),
 (r'vitamin\s+b6','dietaryVitaminB6','mg'),
 (r'vitamin\s+c','dietaryVitaminC','mg'),
 (r'vitamin\s+d','dietaryVitaminD','mcg'),
 (r'vitamin\s+e','dietaryVitaminE','mg'),
 (r'vitamin\s+k','dietaryVitaminK','mcg'),
]
MASS={'g':1,'mg':.001,'mcg':.000001,'µg':.000001,'μg':.000001,'ug':.000001}
VALUE=r'(?<![\d.,])([0-9]+(?:[.,][0-9]+)?)\s*(kcal|kj|mcg|mg|µg|μg|ug|g)\b'

def parse(text,reference_amount=None,reference_unit="g"):
    if reference_amount is None:reference_unit="g"
    text=text[:30000]
    normalized=text.casefold().replace('\u00a0',' ')
    # Default to an explicit 100g column. A caller may confirm another serving
    # basis, but cannot override a conflicting fixed column or US carbs.
    basis=bool(re.search(r'\b100\s*g\b',normalized))
    unsafe=bool(re.search(r'\b100\s*ml\b|nutrition\s+facts|total\s+carbohydrate|(?:per|pro|je)\s+(?:portion|serving)',normalized))
    override=reference_amount is not None
    if override:
        if not math.isfinite(reference_amount) or reference_amount<=0 or reference_unit not in ('g','ml'):raise HTTPException(422,'Invalid label reference amount')
        declared=re.findall(r'\b100\s*(ml|g)\b',normalized)
        # Never override a conflicting fixed column or reinterpret US carbs.
        unsafe=bool(re.search(r'nutrition\s+facts|total\s+carbohydrate',normalized)) or any(reference_amount!=100 or unit!=reference_unit for unit in declared)
        basis=True
    if not basis or unsafe:
        issue='us_label' if re.search(r'nutrition\s+facts|total\s+carbohydrate',normalized) else 'reference_conflict' if override else 'reference_required'
        return {'text':text,'nutrients':{},'basis':'unconfirmed','issues':[issue],'warnings':['Confirm the label reference amount or correct the recognized text; conflicting columns and US total carbohydrates require manual review.']}

    nutrients={};problems=[];salt=None;issues=[]
    def add(key,value,unit):
        if not math.isfinite(value) or value<0:return
        if key in nutrients and nutrients[key]!={'value':value,'unit':unit}:
            nutrients.pop(key);problems.append(key);issues.append("conflicting_values")
        elif key not in problems:nutrients[key]={'value':value,'unit':unit}
    lines=[s.strip() for s in normalized.splitlines() if s.strip()]
    energy_pattern=r'\b(?:energie|energy|brennwert|kalorien|calories)\b'
    # Explicit kcal takes priority across the whole table, not just within a
    # single line. Separate kJ and kcal declarations are not conflicting samples.
    explicit_kcal=any(re.search(energy_pattern,line) and any(m[2]=='kcal' for m in re.finditer(VALUE,line)) and not re.search(r'[<>≤≥]',line) for line in lines)
    for index,line in enumerate(lines):
        # Explicit tables with multiple quantity columns are ambiguous after OCR.
        # Do not choose a column based on visual position lost in plain text.
        found=list(re.finditer(VALUE,line))
        if not found and index+1<len(lines) and not re.search(r'[<>≤≥]',line):
            found=list(re.finditer(VALUE,lines[index+1])) if re.match(r'^\d',lines[index+1]) else []
        supported=bool(re.search(energy_pattern,line) or re.search(r'\b(?:salz|salt)\b',line) or any(re.search(r'\b(?:'+pattern+r')\b',line) for pattern,key,target in LABELS))
        if re.search(r'[<>≤≥]',line):
            if supported:issues.append('qualifier_values')
            continue
        if re.search(energy_pattern,line):
            kcal=[m for m in found if m[2]=='kcal'];kj=[m for m in found if m[2]=='kj']
            if len(kcal)==1:add('dietaryEnergyConsumed',float(kcal[0][1].replace(',','.')),'kcal')
            elif not explicit_kcal and not kcal and len(kj)==1:add('dietaryEnergyConsumed',float(kj[0][1].replace(',','.'))/4.184,'kcal')
            continue
        if len(found)!=1:
            if supported:issues.append('ambiguous_or_missing_units')
            continue
        m=found[0];value=float(m[1].replace(',','.'));unit=m[2]
        if unit not in MASS:continue
        if re.search(r'\b(?:salz|salt)\b',line):
            salt=value*MASS[unit];continue
        for pattern,key,target in LABELS:
            if re.search(r'\b(?:'+pattern+r')\b',line):
                amount=value*MASS[unit]/MASS[target]
                # A macronutrient cannot exceed the entire 100g sample.
                if target=='g' and reference_unit=='g' and amount>(reference_amount or 100):
                    issues.append('implausible_mass');break
                add(key,amount,target);break
    if salt is not None and 'dietarySodium' not in nutrients:
        add('dietarySodium',salt/2.5*1000,'mg')
    factor=100/reference_amount if override else 1
    if override:
        for n in nutrients.values():
            n['value']*=factor
            if not math.isfinite(n['value']):raise HTTPException(422,'Label reference amount is too small')
    if not nutrients:issues.append('no_supported_values')
    return {'text':text,'issues':list(dict.fromkeys(issues)),'basis':'100'+reference_unit,'basis_unit':reference_unit,'reference_amount':reference_amount or 100,'nutrients':nutrients,'warnings':['OCR suggestions must be checked against the package. Missing, ambiguous columns and less-than values are left blank. Salt is converted to sodium using salt / 2.5.']}

def scan(data,reference_amount=None,reference_unit="g"):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in ('JPEG','PNG','WEBP'):raise HTTPException(422,'Use JPEG, PNG or WebP')
                if source.width*source.height>16000000:raise HTTPException(422,'Image exceeds 16 megapixels')
                image=ImageOps.autocontrast(ImageOps.exif_transpose(source).convert('L'))
                scale=min(2,2400/max(image.size))
                image=image.resize((max(1,int(image.width*scale)),max(1,int(image.height*scale))))
                out=io.BytesIO();image.save(out,format='PNG')
    except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError,Image.DecompressionBombWarning):raise HTTPException(422,'Invalid image')
    try:
        result=subprocess.run(['tesseract','stdin','stdout','-l','deu+eng','--psm','6'],input=out.getvalue(),capture_output=True,timeout=25,check=False)
    except FileNotFoundError:raise HTTPException(503,'OCR is not installed. Rebuild the Docker image with update.sh.')
    except subprocess.TimeoutExpired:raise HTTPException(422,'OCR timed out. Try a closer crop of the nutrition label.')
    if result.returncode:raise HTTPException(422,'OCR could not read this image')
    text=result.stdout.decode('utf-8',errors='replace').strip()
    if not text:raise HTTPException(422,'No label text recognized. Try a sharper photo.')
    return parse(text,reference_amount,reference_unit)

class TextPreview(BaseModel):
    text:str=Field(min_length=1,max_length=30000)
    reference_amount:float|None=Field(default=None,gt=0,le=100000,allow_inf_nan=False)
    reference_unit:Literal['g','ml']='g'

def install(app,auth):
    @app.post('/manual-ingredients/parse-label',dependencies=[Depends(auth)])
    async def text_preview(body:TextPreview):
        return parse(body.text,body.reference_amount,body.reference_unit)
    @app.post('/manual-ingredients/scan-label',dependencies=[Depends(auth)])
    async def preview(request:Request,reference_amount:float|None=Query(default=None,gt=0,le=100000,allow_inf_nan=False),reference_unit:Literal['g','ml']='g'):
        data=bytearray()
        async for chunk in request.stream():
            data.extend(chunk)
            if len(data)>MAX_BYTES:raise HTTPException(413,'Image exceeds 10 MiB')
        return await run_in_threadpool(scan,bytes(data),reference_amount,reference_unit)
