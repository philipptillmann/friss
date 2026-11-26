const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('app/static/off-refresh.js','utf8');
function el(){return {disabled:false,attrs:{},setAttribute(k,v){this.attrs[k]=v}}}
let accepted=false,calls=[],refreshed=0,rendered=0;
const context=vm.createContext({words:{de:{},en:{}},Set,document:{createElement:el},t:k=>k,confirm:()=>accepted,$:()=>({hidden:false}),message(){},api:async(path,body)=>{calls.push({path,body:JSON.parse(body.body)});return {changed:true,entry:{off_nutrition_empty:false}}},refresh:async()=>refreshed++,render:()=>rendered++,currentPage:'meals',window:{dispatchEvent(){}},CustomEvent:function(){}});
vm.runInContext(source.slice(0,source.indexOf('(function(){')),context);
const entry={id:'off-entry',revision:4,type:'barcode',barcode:'0123456789012',source:{provider:'Open Food Facts'},off_nutrition_empty:true};context.entry=entry;
const warning=vm.runInContext('offWarningButton(entry)',context);assert.equal(warning.textContent,'!');assert.equal(warning.className,'offNutritionWarning');assert.equal(warning.attrs['aria-label'],'offEmptyWarning');
let stopped=0;warning.onclick({preventDefault(){stopped++},stopPropagation(){stopped++}});assert.equal(stopped,2);assert.equal(calls.length,0,'cancelling must not fetch or navigate');
context.entry={...entry,off_nutrition_empty:false};assert.equal(vm.runInContext('offWarningButton(entry)',context),null);
context.entry={...entry,type:'barcode_bls',bls_code:'BLS'};assert.equal(vm.runInContext('offWarningButton(entry)',context),null);
(async()=>{accepted=true;context.entry=entry;context.button=warning;await vm.runInContext('refreshOffEntry(entry,button)',context);assert.equal(calls.length,1);assert.equal(calls[0].path,'/entries/off-entry/refresh-off');assert.equal(calls[0].body.revision,4);assert.equal(refreshed,1);assert.equal(rendered,1);assert.equal(warning.disabled,false);console.log('OFF refresh UI: accessible zero warning, confirmation/cancel, BLS exclusion, versioned selected refresh and re-enable passed');})().catch(e=>{console.error(e);process.exit(1)});
