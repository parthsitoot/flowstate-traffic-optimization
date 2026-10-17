const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync(require.resolve('../web/motion.js'),'utf8');

function environment(reduced=false){
  let id=0, now=0;
  const scheduled=new Map();
  const node=()=>({dataset:{},children:[],attributes:{},textContent:'',
    setAttribute(key,value){this.attributes[key]=value;},
    replaceChildren(...children){this.children=children;},
    closest(){return null;}
  });
  const context={document:{createElement:node},matchMedia:()=>({matches:reduced}),
    performance:{now:()=>now},requestAnimationFrame:fn=>{scheduled.set(++id,fn);return id;},
    cancelAnimationFrame:key=>scheduled.delete(key)};
  vm.runInNewContext(source,context);
  return {motion:context.FlowStateMotion,node,scheduled,
    advance(time){now=time;const pending=[...scheduled.values()];scheduled.clear();pending.forEach(fn=>fn(now));}};
}

test('rapid model updates finish on the latest API value without an old frame winning',()=>{
  const env=environment(),element=env.node();
  env.motion.countTo(element,5.61,{decimals:2,unit:'vehicles'});
  env.advance(150);
  env.motion.countTo(element,3.59,{decimals:2,unit:'vehicles'});
  env.advance(1000);
  assert.equal(element.children[0].textContent,'3.59');
  assert.equal(element.children[1].textContent,'vehicles');
  assert.equal(element.children[2].textContent,'3.59 vehicles');
  assert.equal(env.scheduled.size,0);
});

test('reduced motion renders the exact result immediately and skips result transitions',()=>{
  const env=environment(true),element=env.node();
  env.motion.countTo(element,1.7041,{decimals:4,unit:'vehicles'});
  env.motion.stagger([{animate(){assert.fail('Reduced motion must not animate');}}]);
  env.motion.enter({animate(){assert.fail('Reduced motion must not animate');}});
  assert.equal(element.children[0].textContent,'1.7041');
  assert.equal(env.scheduled.size,0);
});
