const {test} = require('node:test');
const assert = require('node:assert/strict');
const {LatestFrameLoader} = require('../web/async.js');
const deferred = () => { let resolve; const promise = new Promise(r => {resolve = r;}); return {promise, resolve}; };

test('slow camera responses cannot replace the latest timeline frame', async () => {
  const first = deferred();
  const calls = [], displayed = [];
  const loader = new LatestFrameLoader(key => {
    calls.push(key);
    return key === 'old' ? first.promise : Promise.resolve(key);
  }, value => displayed.push(value), assert.fail);
  const finished = loader.request('old');
  loader.request('intermediate');
  loader.request('latest');
  first.resolve('old');
  await finished;
  assert.deepEqual(calls, ['old','latest']);
  assert.deepEqual(displayed, ['latest']);
});

test('frame validity is checked again after slow image decoding', async () => {
  const decoding = deferred();
  const started = deferred();
  const displayed = [];
  const loader = new LatestFrameLoader(key => Promise.resolve(key), async (value,isCurrent) => {
    if (value === 'old') { started.resolve(); await decoding.promise; }
    if (isCurrent()) displayed.push(value);
  }, assert.fail);
  const finished = loader.request('old');
  await started.promise;
  loader.request('latest');
  decoding.resolve();
  await finished;
  assert.deepEqual(displayed, ['latest']);
});

test('repeated visible queues reuse the bounded camera cache', async () => {
  let calls = 0;
  const loader = new LatestFrameLoader(async key => { calls++; return key; }, () => {}, assert.fail, 2);
  await loader.request('A');
  await loader.request('A');
  assert.equal(calls,1);
  await loader.request('B');
  await loader.request('C');
  assert.equal(loader.cache.size,2);
  await loader.request('A');
  assert.equal(calls,4);
});

test('a failed camera request can be retried at the same frame', async () => {
  let fail = true;
  const errors = [], displayed = [];
  const loader = new LatestFrameLoader(async key => {
    if (fail) throw Error('temporarily offline');
    return key;
  }, value => displayed.push(value), error => errors.push(error.message));
  await loader.request('A');
  fail = false;
  await loader.request('A');
  assert.deepEqual(errors,['temporarily offline']);
  assert.deepEqual(displayed,['A']);
});

const {requestJSON} = require('../web/async.js');
test('transient failed-to-fetch recovers automatically on the next attempt', async () => {
  let attempts = 0;
  const result = await requestJSON('/api/predict?counts=6,6,6',{fetcher: async () => {
    attempts++;
    if (attempts === 1) throw TypeError('Failed to fetch');
    return {ok:true,json:async()=>({prediction:5.608})};
  }});
  assert.equal(attempts,2);
  assert.equal(result.prediction,5.608);
});
test('persistent network failure gives connection recovery guidance', async () => {
  await assert.rejects(requestJSON('/api/run',{fetcher:async()=>{throw TypeError('Failed to fetch');}}),/Check your internet connection/);
});

test('direct file opens route to the working hosted app, while servers stay local', () => {
  const source = require('node:fs').readFileSync(require.resolve('../web/entry.js'),'utf8');
  const redirects=[];
  const vm = require('node:vm');
  for (const protocol of ['file:','http:','https:'])
    vm.runInNewContext(source,{location:{protocol,replace:url=>redirects.push({protocol,url})}});
  assert.deepEqual(redirects,[{protocol:'file:',url:'https://flowstate-traffic-optimization.vercel.app/'}]);
});

test('connection help matches the place the user opened the app', () => {
  const {connectionMessage} = require('../web/async.js');
  assert.match(connectionMessage({protocol:'http:',hostname:'localhost'}),/Keep python3 app.py running/);
  assert.match(connectionMessage({protocol:'file:'}),/Open FlowState online/);
  assert.match(connectionMessage({protocol:'https:',hostname:'flowstate-traffic-optimization.vercel.app'}),/internet connection/);
  assert.doesNotMatch(connectionMessage({protocol:'https:',hostname:'flowstate-traffic-optimization.vercel.app'}),/python3/);
});
test('invalid custom model input is not retried', async () => {
  let attempts=0;
  await assert.rejects(requestJSON('/api/predict',{fetcher:async()=>{
    attempts++;
    return {ok:false,status:400,json:async()=>({error:'Enter exactly three arrival counts.'})};
  }}),/exactly three/);
  assert.equal(attempts,1);
});
