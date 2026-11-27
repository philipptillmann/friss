Object.assign(words.de,{labelUpload:'Etikettbild hochladen',labelScan:'Nährwertetikett fotografieren',labelScanText:'Erkannter Text',labelScanWorking:'Etikett wird auf deinem Server gelesen …',labelScanDone:'Vorschläge pro 100 g übernommen. Namen eintragen, alle Werte mit dem Etikett vergleichen und speichern. Salz wurde gegebenenfalls in Natrium umgerechnet.',labelScanUnknown:'Keine eindeutigen Werte pro 100 g erkannt. Bitte nur die 100-g-Spalte fotografieren oder Werte manuell eingeben. Portionsangaben, US-Labels und 100-ml-Angaben werden nicht automatisch umgerechnet.',labelScanError:'Etikett konnte nicht gelesen werden.',labelScanReady:'Bitte warten, bis die Zutatenmaske geladen ist.'});
Object.assign(words.en,{labelUpload:'Upload label image',labelScan:'Photograph nutrition label',labelScanText:'Recognized text',labelScanWorking:'Reading label on your server …',labelScanDone:'Per-100-g suggestions filled in. Enter a name, check every value against the label, then save. Salt was converted to sodium where applicable.',labelScanUnknown:'No unambiguous per-100-g values found. Photograph only the 100-g column or enter values manually. Per-serving, US and per-100-ml labels are not automatically converted.',labelScanError:'Could not read the label.',labelScanReady:'Please wait for the ingredient form to load.'});
(function(){
 let sequence=0;
 function choose(input){if(!manualFieldsReady){$('labelScanStatus').textContent=t('labelScanReady');return;}if(!manualImportPending)$(input).click();}
 $('labelScanButton').onclick=()=>choose('labelScanFile');$('labelUploadButton').onclick=()=>choose('labelUploadFile');
 async function scan(input){
 const file=input.files[0];input.value='';if(!file||manualImportPending||!manualFieldsReady)return;
 if(manualHasDraft()&&!confirm(t('manualImportReplace')))return;
 const context={item:manualEditing?.id?manualEditing:null,name_de:$('manualNameDe').value||'',name_en:$('manualNameEn').value||'',barcodes:typeof readManualBarcodes==='function'?readManualBarcodes():[],notes:$('manualNotes').value||''};
 let reference='';try{reference=typeof labelReferenceQuery==='function'?labelReferenceQuery():'';}catch(e){$('labelScanStatus').textContent=e.message;return;}
 const mine=++sequence,generation=++manualImportGeneration;manualImportPending=true;$('labelScanButton').disabled=true;$('labelUploadButton').disabled=true;$('manualImportButton').disabled=true;$('labelScanStatus').textContent=t('labelScanWorking');$('labelScanReview').hidden=true;
 try{
 const image=await barcodeImage(file);const result=await api('/manual-ingredients/scan-label'+reference,{method:'POST',body:image});
 if(mine!==sequence||generation!==manualImportGeneration||$('dashboard').hidden)return;
 $('labelScanText').textContent=result.text;$('labelScanReview').hidden=false;
 if(!Object.keys(result.nutrients).length){$('labelScanStatus').textContent=t('labelScanUnknown');return;}
 editManual({...context.item,name_de:context.name_de,name_en:context.name_en,barcodes:context.barcodes,basis_unit:result.basis_unit||'g',notes:(context.notes+'\nNutrition label OCR (review required)\nReference: '+(result.reference_amount||100)+' '+(result.basis_unit||'g')+'\n'+result.warnings.join('\n')+'\n\n'+result.text.slice(0,8000)).slice(0,10000),nutrients:result.nutrients});
 manualEditing=context.item;manualSource=null;manualDraft=null;$('manualEditorTitle').textContent=t(context.item?'editManual':'newManual');$('manualAmend').hidden=!context.item;$('manualSaveHint').hidden=!context.item;$('manualSave').textContent=t(context.item?'saveFuture':'save');$('labelScanStatus').textContent=t('labelScanDone');$('manualForm').scrollIntoView({behavior:'smooth',block:'start'});
 }catch(e){if(mine===sequence&&generation===manualImportGeneration)$('labelScanStatus').textContent=t('labelScanError')+' '+e.message;}
 finally{if(mine===sequence){manualImportPending=false;$('labelScanButton').disabled=false;$('labelUploadButton').disabled=false;$('manualImportButton').disabled=!manualFieldsReady;}}
 }
 $('labelScanFile').onchange=()=>scan($('labelScanFile'));$('labelUploadFile').onchange=()=>scan($('labelUploadFile'));
 window.addEventListener('friss-logout',()=>{sequence++;$('labelScanFile').value='';$('labelUploadFile').value='';$('labelScanText').textContent='';$('labelScanStatus').textContent='';$('labelScanReview').hidden=true;$('labelScanButton').disabled=false;$('labelUploadButton').disabled=false;});
 translate();
})();
