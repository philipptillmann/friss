Object.assign(words.en,{offEmptyWarning:'Open Food Facts nutrition is missing or all zero. Check the product data; tap to refresh.',offRefresh:'Refresh from Open Food Facts',offRefreshConfirm:'Fetch current Open Food Facts data and recalculate this entry with its saved amount? Already logged recipe meals keep their snapshots. Previously exported Apple Health values need separate correction.',offRefreshed:'Open Food Facts data refreshed.',offRefreshUnchanged:'Open Food Facts returned the same data.',offRefreshStillEmpty:'The product still has no positive nutritional values. Check/edit it in Open Food Facts, then refresh again.',offRefreshHealth:'Previously exported Health data was not updated. Check the affected export before writing again.',offRefreshing:'Refreshing Open Food Facts …'});
Object.assign(words.de,{offEmptyWarning:'Open-Food-Facts-Nährwerte fehlen oder sind alle null. Produktdaten prüfen; zum Aktualisieren antippen.',offRefresh:'Aus Open Food Facts aktualisieren',offRefreshConfirm:'Aktuelle Open-Food-Facts-Daten laden und diesen Eintrag mit seiner gespeicherten Menge neu berechnen? Bereits gebuchte Rezeptmahlzeiten behalten ihre Momentaufnahme. Schon exportierte Apple-Health-Werte müssen separat korrigiert werden.',offRefreshed:'Open-Food-Facts-Daten aktualisiert.',offRefreshUnchanged:'Open Food Facts liefert dieselben Daten.',offRefreshStillEmpty:'Das Produkt hat weiterhin keine positiven Nährwertangaben. In Open Food Facts prüfen/ergänzen und erneut aktualisieren.',offRefreshHealth:'Bereits exportierte Health-Daten wurden nicht geändert. Betroffenen Export vor einer erneuten Übertragung prüfen.',offRefreshing:'Open Food Facts wird aktualisiert …'});
let offRefreshGeneration=0;
const offRefreshBusy=new Set();
function canRefreshOff(e){return e?.type==='barcode'&&e.source?.provider==='Open Food Facts'&&!!e.barcode&&!e.bls_code;}
function offWarningButton(e){
 if(!canRefreshOff(e)||!e.off_nutrition_empty)return null;
 const b=document.createElement('button');b.type='button';b.className='offNutritionWarning';b.textContent='!';b.title=t('offEmptyWarning');b.setAttribute('aria-label',t('offEmptyWarning'));b.disabled=offRefreshBusy.has(e.id);b.onclick=event=>{event.preventDefault();event.stopPropagation();refreshOffEntry(e,b);};return b;
}
async function refreshOffEntry(e,button){
 if(offRefreshBusy.has(e.id)||!confirm(t('offRefreshConfirm')))return;
 const generation=offRefreshGeneration;offRefreshBusy.add(e.id);if(button)button.disabled=true;message(t('offRefreshing'));
 try{
  const result=await api('/entries/'+e.id+'/refresh-off',{method:'POST',body:JSON.stringify({revision:e.revision||1})});
  if(generation!==offRefreshGeneration||$('dashboard').hidden)return;
  await refresh();
  if(generation!==offRefreshGeneration||$('dashboard').hidden)return;
  if(currentPage==='entry'&&detailEntryId()===e.id)await loadEntryDetails(e.id);
  if(generation!==offRefreshGeneration||$('dashboard').hidden)return;
  message([t(result.changed?'offRefreshed':'offRefreshUnchanged'),result.entry.off_nutrition_empty?t('offRefreshStillEmpty'):'',result.health_correction_required?t('offRefreshHealth'):''].filter(Boolean).join(' '));
  window.dispatchEvent(new CustomEvent('friss-off-refreshed',{detail:e.id}));
 }catch(error){if(generation===offRefreshGeneration&&!$('dashboard').hidden)message(error.message,true);}
 finally{offRefreshBusy.delete(e.id);if(button)button.disabled=false;if(generation===offRefreshGeneration&&!$('dashboard').hidden){render();if(typeof renderEntryDetails==='function')renderEntryDetails(false);}}
}
(function(){
 const b=document.createElement('button');b.id='detailRefreshOff';b.type='button';b.className='secondary';b.hidden=true;b.dataset.i='offRefresh';b.textContent=t('offRefresh');$('detailWarnings').after(b);b.onclick=()=>{if(detailedEntry)refreshOffEntry(detailedEntry,b);};
 const original=renderEntryDetails;renderEntryDetails=function(setTime=false){original(setTime);b.hidden=!canRefreshOff(detailedEntry);b.disabled=!detailedEntry||detailedEntry.health_status==='claimed'||offRefreshBusy.has(detailedEntry.id);};
 window.addEventListener('friss-page',()=>{b.hidden=true;});
 window.addEventListener('friss-logout',()=>{offRefreshGeneration++;offRefreshBusy.clear();b.hidden=true;});
 translate();if(detailedEntry)renderEntryDetails(false);
})();
