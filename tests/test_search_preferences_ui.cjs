const fs=require('fs'),vm=require('vm'),assert=require('assert');
const els=new Map(),listeners={};function element(){return {value:'',hidden:false,disabled:false,textContent:'',children:[],append(...n){this.children.push(...n)},replaceChildren(...n){this.children=n},reset(){},focus(){},scrollIntoView(){}}}const $=id=>{if(!els.has(id))els.set(id,element());return els.get(id)};
let calls=[],fail=true;
const data={synonyms:[],learned:[{query:'zucker',lang:'de',source:'bls',target:'SUGAR',name_de:'Haushaltszucker',name_en:'Sugar',count:3}],synonym_count:0,learned_count:1};
const ctx=vm.createContext({$,words:{de:{},en:{}},t:k=>k,lang:'de',currentPage:'settings',uuid:()=> 'fixed-id',document:{createElement:element,documentElement:{}},window:{addEventListener:(n,f)=>listeners[n]=f},MutationObserver:class{observe(){}},confirm:()=>true,sourceBadge:()=>element(),translate(){},setTimeout,clearTimeout,api:async(path,options)=>{calls.push({path,body:options?.body?JSON.parse(options.body):null});if(path.startsWith('/food-search/preferences?'))return data;if(path.startsWith('/foods?'))return [{bls_code:'SUGAR',name_de:'Haushaltszucker',name_en:'Sugar',display_name:'Haushaltszucker'}];if(fail){fail=false;throw Error('Lost response')}return {id:'fixed-id'}}});
vm.runInContext(fs.readFileSync('app/static/search-preferences.js','utf8'),ctx);
(async()=>{
 await new Promise(r=>setImmediate(r));assert.equal($('synLearnedList').children.length,1);
 $('synLearnedList').children[0].children[3].children[0].onclick();assert.equal($('synQuery').value,'zucker');assert.equal($('synPromote').hidden,false);
 $('synQuery').value='Backwürfel';await $('synForm').onsubmit({preventDefault(){}});assert.equal($('synFields').disabled,true);
 $('synQuery').value='Changed while pending';await $('synForm').onsubmit({preventDefault(){}});
 const saves=calls.filter(c=>c.path==='/food-search/synonyms');assert.equal(saves.length,2);assert.deepEqual(saves[0].body,saves[1].body);assert.equal(saves[0].body.query,'Backwürfel');assert.equal(saves[0].body.bls_code,'SUGAR');assert.equal(saves[0].body.replace_learned.target,'SUGAR');
 $('synNew').onclick();$('synFoodSearch').value='zucker';await $('synFoodSearch').oninput();assert.equal($('synResults').children.length,1);$('synResults').children[0].onclick();assert.ok($('synSelected').textContent.includes('SUGAR'));
 listeners['friss-logout']();assert.equal($('synList').children.length,0);assert.equal($('synSelected').textContent,'');
 console.log('Search settings UI: learned mapping edit, explicit synonym, stable retry, BLS selection and logout clearing passed');
})().catch(e=>{console.error(e);process.exitCode=1});
