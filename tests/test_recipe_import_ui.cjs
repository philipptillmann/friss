const fs=require('fs'),vm=require('vm'),assert=require('assert');
const els=new Map(),listeners={};function element(tag){return {tag,value:'',hidden:false,disabled:false,children:[],append(...n){this.children.push(...n)},replaceChildren(...n){this.children=n},reset(){},remove(){this.removed=true}}}const $=id=>{if(!els.has(id))els.set(id,element('div'));return els.get(id)};
const preview={name:'Original',servings:4,notes:'Cook it',source:{url:'https://www.chefkoch.de/rezepte/1/a.html',yield_text:'4 Portionen',ingredient_lines:['200 g Tomato']},ingredients:[{name:'Tomato',original_line:'200 g Tomato',quantity:{value:200,unit:'g'},matches:[{bls_code:'TOMATO',display_name:'Tomate'}]}]};
const calls=[];let fail=true,chosen=false;
const ctx=vm.createContext({$,words:{de:{},en:{}},t:k=>k,lang:'de',uuid:()=> 'stable-id',currentPage:'recipes',activeRecipe:null,document:{createElement:element},window:{addEventListener:(n,f)=>listeners[n]=f},confirm:()=>true,translate(){},message(){},refresh:async()=>{},chooseRecipe:()=>{chosen=true},api:async(path,options)=>{const body=options?.body?JSON.parse(options.body):null;calls.push({path,body});if(path.endsWith('preview'))return preview;if(fail){fail=false;throw Error('lost response')}return {id:'new-recipe'}}});$('recipeEditor').scrollIntoView=()=>{};
vm.runInContext(fs.readFileSync('app/static/recipe-import.js','utf8'),ctx);
(async()=>{
 $('chefURL').value=preview.source.url;await $('chefLinkForm').onsubmit({preventDefault(){}});assert.equal($('chefReview').hidden,false);assert.equal(calls.length,1,'preview must not save');assert.equal($('chefName').value,'Original');
 $('chefName').value='Edited';$('chefServings').value=2;
 const card=$('chefRows').children[0],name=card.children[0].children[1],quantities=card.children[2],amount=quantities.children[0].children[1],selection=card.children[3].children[1];name.value='Edited tomato';amount.value=300;selection.value='TOMATO';
 await $('chefReviewForm').onsubmit({preventDefault(){}});assert.equal($('chefReviewFields').disabled,true,'uncertain request must retain a frozen payload');
 $('chefName').value='Should not replace pending payload';await $('chefReviewForm').onsubmit({preventDefault(){}});
 assert.deepEqual(calls[1].body,calls[2].body);assert.equal(calls[1].body.name,'Edited');assert.equal(calls[1].body.servings,2);assert.equal(calls[1].body.ingredients[0].quantity.value,300);assert.equal(calls[1].body.ingredients[0].bls_code,'TOMATO');assert.equal(calls[1].body.ingredients[0].original_line,'200 g Tomato');assert.equal(ctx.activeRecipe,'new-recipe');assert.ok(chosen);assert.equal($('chefReview').hidden,true);
 listeners['friss-logout']();assert.equal($('chefReview').hidden,true);
 console.log('Chefkoch UI: review before save, edited values, original source, stable retries and opening the new recipe passed');
})().catch(e=>{console.error(e);process.exitCode=1});
