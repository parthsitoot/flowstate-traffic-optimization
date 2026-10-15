const $=id=>document.getElementById(id);let data,model,index=0,playing=true,slideIndex=0;
const names=['North','East','South','West'];
const get = url => FlowStateAsync.requestJSON(url);
const {countTo,enter,busy,reduced}=FlowStateMotion;
const predictionOutput=document.querySelector('.prediction-output');
function view(name){document.querySelectorAll('.view').forEach(v=>v.classList.toggle('hidden',v.id!==name));document.querySelectorAll('.nav').forEach(v=>{const active=v.dataset.view===name;v.classList.toggle('active',active);if(active)v.setAttribute('aria-current','page');else v.removeAttribute('aria-current')});$('breadcrumb').textContent=name==='dashboard'?'Simulation':name==='predict'?'Predict arrivals':name==='research'?'How it works':'Presentation';window.scrollTo(0,0);if(name==='presentation')renderSlide();enter($(name));}
document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>view(b.dataset.view));$('present').onclick=()=>view('presentation');
function roundRect(c,x,y,w,h,r,color){c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill()}
function drawJunction(h,transit=[]){const c=$('junction').getContext('2d');const W=760,H=460;c.clearRect(0,0,W,H);c.fillStyle='#e7eae8';c.fillRect(0,0,W,H);
// Quiet urban blocks, trees, and roads drawn without external assets.
for(const [x,y,w,hh]of [[32,62,212,105],[510,48,205,120],[27,300,220,120],[514,300,214,120]]){roundRect(c,x+5,y+5,w,hh,9,'#d5dcd6');roundRect(c,x,y,w,hh,9,'#e0e5df');for(let j=0;j<3;j++){roundRect(c,x+17+j*59,y+18,44,hh-36,4,'#ced7cd')}}
for(const [x,y]of [[265,75],[490,85],[258,368],[492,370],[70,270],[670,186]]){c.fillStyle='#b8cdb0';c.beginPath();c.arc(x,y,12,0,7);c.fill();c.fillStyle='#9fbd98';c.beginPath();c.arc(x-3,y-3,7,0,7);c.fill()}
c.fillStyle='#aab9ad';c.fillRect(297,0,166,H);c.fillRect(0,170,W,120);c.fillStyle='#495451';c.fillRect(305,0,150,H);c.fillRect(0,178,W,104);
c.strokeStyle='#8c9b8c';c.lineWidth=2;c.setLineDash([12,12]);c.beginPath();c.moveTo(380,0);c.lineTo(380,178);c.moveTo(380,282);c.lineTo(380,H);c.moveTo(0,230);c.lineTo(305,230);c.moveTo(455,230);c.lineTo(W,230);c.stroke();c.setLineDash([]);
c.fillStyle='#d2d8c7';for(let i=0;i<7;i++){c.fillRect(310+i*20,160,11,7);c.fillRect(310+i*20,293,11,7)}for(let i=0;i<4;i++){c.fillRect(287,184+i*25,7,15);c.fillRect(467,184+i*25,7,15)}
c.fillStyle='#b4c3ad';c.font='11px Arial';c.fillText('N',374,28);c.fillText('S',375,444);c.fillText('W',13,224);c.fillText('E',735,224);
const positions=[[326,139],[479,245],[410,314],[269,196]];
for(let d=0;d<4;d++){let [x,y]=positions[d];for(let n=0;n<Math.min(h.queues[d],18);n++){let row=Math.floor(n/2),lane=n%2;let xx=x,yy=y;if(d===0){xx+=lane*27;yy-=row*23}if(d===1){xx+=row*30;yy+=lane*15}if(d===2){xx+=lane*24;yy+=row*23}if(d===3){xx-=row*30;yy+=lane*15}const vertical=d%2===0;roundRect(c,xx,yy,vertical?13:23,vertical?19:10,3,d===h.phase&&!h.amber?'#c6edaa':'#d6dfcf');c.fillStyle='#6a8d80';c.fillRect(xx+3,yy+3,vertical?7:5,vertical?5:4)}
const lights=[[286,144],[472,166],[470,299],[286,292]];const [lx,ly]=lights[d];roundRect(c,lx-4,ly-4,16,16,4,'#2d3b34');c.fillStyle=!h.amber&&d===h.phase?'#b9e892':'#cd766a';c.beginPath();c.arc(lx+4,ly+4,4,0,7);c.fill();}
// Illustrative crossings are triggered only by recorded departures in the same green phase.
for(const progress of transit){const d=h.phase;let x,y;if(d===0){x=333;y=155+progress*160}else if(d===1){x=480-progress*210;y=245}else if(d===2){x=415;y=310-progress*170}else{x=268+progress*215;y=200}c.globalAlpha=Math.min(1,progress*8,(1-progress)*8);roundRect(c,x,y,d%2===0?13:22,d%2===0?21:11,3,'#c6edaa');c.globalAlpha=1}
roundRect(c,344,208,72,42,6,'#526b5b');c.fillStyle='#dbe9d3';c.textAlign='center';c.font='9px Arial';c.fillText('FLOWSTATE',380,226);c.font='8px Arial';c.fillText('JUNCTION 01',380,240);c.textAlign='left';$('phase-label').dataset.state=h.amber?'clearance':'green';$('phase-label').textContent=h.amber?'ALL-RED TRANSITION · 3s':`${names[h.phase].toUpperCase()} · GREEN`;
}
function drawChart(){if(!data)return;const c=$('chart').getContext('2d'),w=850,h=220,p=35;c.clearRect(0,0,w,h);const max=Math.max(10,...data.fixed.history.map(x=>x.queues.reduce((a,b)=>a+b,0)),...data.smart.history.map(x=>x.queues.reduce((a,b)=>a+b,0)),...data.reactive.history.map(x=>x.queues.reduce((a,b)=>a+b,0)));c.font='10px Arial';c.lineWidth=1;for(let i=0;i<4;i++){const y=15+i*53;c.strokeStyle='#e8e8ed';c.beginPath();c.moveTo(p,y);c.lineTo(w-15,y);c.stroke();c.fillStyle='#7a7a80';c.fillText(Math.round(max*(1-i/3)),3,y+3)}for(const [key,color]of [['fixed','#969ba2'],['reactive','#bd8b42'],['smart','#0071e3']]){c.strokeStyle=color;c.lineWidth=2.5;c.beginPath();data[key].history.forEach((q,i)=>{const x=p+i/(data[key].history.length-1)*(w-p-15),y=174-q.queues.reduce((a,b)=>a+b,0)/max*159;i?c.lineTo(x,y):c.moveTo(x,y)});c.stroke()}c.fillStyle='#7a7a80';[0,150,300,450,600].forEach((v,i)=>c.fillText(v,p+i*(w-p-25)/4,202));const x=p+index/(data.smart.history.length-1)*(w-p-15);c.strokeStyle='#7d8b9d';c.setLineDash([3,4]);c.beginPath();c.moveTo(x,12);c.lineTo(x,180);c.stroke();c.setLineDash([])}
const cameraFrames = new FlowStateAsync.LatestFrameLoader(
  key => get('/api/vision?q=' + key),
  async (result, isCurrent) => {
    const im = new Image();
    im.src = result.image;
    await im.decode();
    if (!isCurrent()) return;
    const c = $('camera').getContext('2d');
    c.drawImage(im, 0, 0);
    c.strokeStyle = '#a1efbf';
    c.lineWidth = 1;
    c.font = '7px monospace';
    result.boxes.forEach((box, i) => {
      c.strokeRect(box.x-2, box.y-2, box.w+4, box.h+4);
      c.fillStyle = '#b6f4d0';
      c.fillText('V'+(i+1), box.x, box.y-4);
    });
    $('counts').textContent = result.counts.map((n,i) => names[i][0]+' '+String(n).padStart(2,'0')).join('   ');
  },
  () => { $('counts').textContent = 'Camera unavailable. Move the timeline to retry.'; }
);
function vision(h) { cameraFrames.request(h.queues.map(n => Math.min(9,n)).join(',')); }
function updatePlayButton() {
  $('play').textContent = playing ? 'Ⅱ' : '▶';
  $('play').setAttribute('aria-label', playing ? 'Pause playback' : 'Resume playback');
}
let junctionFrame=0,previousSnapshot=null;
function render(animate=false){if(!data)return;const h=data.smart.history[index];cancelAnimationFrame(junctionFrame);drawJunction(h);
  if(animate && !reduced.matches && previousSnapshot?.experiment===data && !h.amber && !previousSnapshot.frame.amber && h.phase===previousSnapshot.frame.phase && h.served>previousSnapshot.frame.served){
    const count=Math.min(3,h.served-previousSnapshot.frame.served),started=performance.now();
    const frame=now=>{
      if(!playing || $('dashboard').classList.contains('hidden') || data.smart.history[index]!==h)return;
      const elapsed=now-started;
      const transit=Array.from({length:count},(_,i)=>(elapsed-i*70)/650).filter(p=>p>0&&p<1);
      drawJunction(h,transit);
      if(elapsed<650+(count-1)*70)junctionFrame=requestAnimationFrame(frame);
    };
    junctionFrame=requestAnimationFrame(frame);
  }
  previousSnapshot={experiment:data,frame:h};drawChart();$('timeline').value=index;$('timeline').style.setProperty('--progress',`${index/Math.max(1,data.smart.history.length-1)*100}%`);const t=h.time;$('clock').textContent=`${String(Math.floor(t/60)).padStart(2,'0')}:${String(t%60).padStart(2,'0')} / 10:00`;if(!$('lane-bars').children.length)$('lane-bars').innerHTML=names.map(name=>`<div class="lane"><span>${name}</span><div class="bar"><i style="width:0%"></i></div><b></b></div>`).join('');[...$('lane-bars').children].forEach((lane,i)=>{lane.querySelector('i').style.width=`${Math.min(100,h.forecast[i]/8*100)}%`;lane.querySelector('b').textContent=`${h.queues[i]} queued · ${h.forecast[i]} next`});vision(h)}
function populate(){
  const s=data.smart.metrics,f=data.fixed.metrics,r=data.reactive.metrics;
  const change=Math.abs(data.improvement).toFixed(1);
  const better=data.improvement>=0;
  const difference=Math.abs(s.queue_seconds-f.queue_seconds);
  const queueComparison=s.delay_per_arrival===r.delay_per_arrival?
    `ML-assisted and queue-only each recorded ${s.delay_per_arrival.toFixed(2)}s of waiting per arrival.`:
    `ML-assisted recorded ${s.delay_per_arrival.toFixed(2)}s of waiting per arrival versus ${r.delay_per_arrival.toFixed(2)}s for queue-only.`;
  $('result-headline').textContent=better?`ML-assisted signals reduced total waiting by ${change}%`:`ML-assisted signals increased total waiting by ${change}%`;
  $('result-explanation').textContent=`In this ${data.seconds/60}-minute ${scenarioLabel(data.scenario)} run, cars spent ${Math.round(difference/60)} ${better?'fewer':'more'} total vehicle-minutes waiting than with a fixed timer. ${queueComparison} One run does not prove it wins every time.`;
  countTo($('improvement'),Number(change),{decimals:1,unit:'%',prefix:better?'−':'+'});
  $('improvement-help').textContent=better?'Less total waiting than fixed-time':'More total waiting than fixed-time';
  countTo($('delay'),s.delay_per_arrival,{decimals:2,unit:' s'});
  $('fixed-delay').textContent=`Fixed timer: ${f.delay_per_arrival}s per arrival`;
  countTo($('served'),s.served,{unit:` / ${s.arrivals}`});
  $('remaining').textContent=`${s.remaining} still queued · fixed timer crossed ${f.served}`;
  $('experiment-context').textContent=`Showing: ${scenarioLabel(data.scenario)} · run ${data.seed} · ${data.seconds/60} minutes. The playback below shows the ML-assisted run.`;
  $('export').disabled=false;
  $('results-table').innerHTML='<table><thead><tr><th>Signal strategy</th><th>Wait per arrival</th><th>Cars crossed</th><th>Still queued</th></tr></thead><tbody>'+[['fixed','Fixed timer'],['reactive','Queue-only'],['smart','ML-assisted']].map(([k,n])=>`<tr><td>${n}</td><td>${data[k].metrics.delay_per_arrival}s</td><td>${data[k].metrics.served}</td><td>${data[k].metrics.remaining}</td></tr>`).join('')+'</tbody></table>';
}
function scenarioLabel(key){return {rush:'morning rush',balanced:'balanced traffic',surge:'eastbound surge'}[key]||key}
async function loadModel() {
  if (model) return;
  model = await get('/api/model');
  countTo($('mae'),model.mae,{decimals:2,unit:' veh'});
  $('model-details').innerHTML = `<table><tr><td>Model</td><td>Random Forest · ${model.n_estimators} trees · maximum depth 8</td></tr><tr><td>Examples for learning / testing</td><td>${model.training_samples} / ${model.test_samples} · generated traffic</td></tr><tr><td>Average test error (MAE)</td><td>${model.mae.toFixed(2)} cars per 10-second prediction</td></tr><tr><td>Repeating the latest count</td><td>${model.persistence_mae.toFixed(2)} cars average error</td></tr><tr><td>Averaging three counts</td><td>${model.moving_average_mae.toFixed(2)} cars average error</td></tr></table><p class="caption">Lower average error is better. These simple comparison methods show whether training the model helped.</p><details class="technical-detail"><summary>More model statistics</summary><p>RMSE: ${model.rmse.toFixed(3)} cars. This measure puts extra weight on larger errors.</p></details>`;
}
async function run() {
  const button = $('run');
  button.disabled = true;
  button.textContent = 'Running comparison…';
  busy(button,true);busy(document.querySelector('.metrics'),true);
  $('error').textContent = '';
  $('connection-error').hidden = true;
  const previousPlaying = playing;
  playing = false;
  updatePlayButton();
  try {
    const seedText = $('seed').value.trim();
    const seed = Number(seedText);
    if (!seedText || !Number.isInteger(seed) || seed < 0 || seed > 999999)
      throw Error('Choose a whole run number between 0 and 999999.');
    const scenario = $('scenario').value;
    await loadModel();
    const result = await get(`/api/run?scenario=${scenario}&seed=${seed}`);
    data = result;
    index = 0;
    playing = !reduced.matches;
    $('timeline').max = data.smart.history.length-1;
    populate();
    render();
  } catch (error) {
    $('error').textContent = error.message;
    $('connection-error').hidden = false;
    playing = previousPlaying && Boolean(data);
  } finally {
    updatePlayButton();
    button.disabled = false;
    button.textContent = 'Run comparison';
    busy(button,false);busy(document.querySelector('.metrics'),false);
  }
}
$('run').onclick = run;
$('retry').onclick = run;
$('play').onclick = () => {
  if (!data) return;
  if (index === data.smart.history.length-1) index = 0;
  playing = !playing;
  updatePlayButton();
  render();
};
$('timeline').oninput = () => {
  if (!data) return;
  index = Number($('timeline').value);
  playing = false;
  updatePlayButton();
  render();
};
setInterval(() => {
  if (playing && data && !$('dashboard').classList.contains('hidden')) {
    index = Math.min(index + Number($('speed').value), data.smart.history.length-1);
    render(true);
    if (index === data.smart.history.length-1) { playing = false; updatePlayButton(); }
  }
}, 1000);
$('export').onclick = () => {
  if (!data) return;
  const keys = Object.keys(data.fixed.metrics);
  const rows = [['scenario','seed','seconds','policy',...keys]];
  for (const policy of ['fixed','reactive','smart'])
    rows.push([data.scenario,data.seed,data.seconds,policy,...keys.map(k => data[policy].metrics[k])]);
  const csv = rows.map(row => row.join(',')).join('\n') + '\n';
  const url = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url;
  link.download = `flowstate-${data.scenario}-seed-${data.seed}.csv`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
const predictionInputs = ['count-recent','count-previous','count-oldest'];
let predictionRequest=0;
predictionInputs.forEach(id => $(id).addEventListener('input', () => {
  predictionRequest++;
  $('predict-submit').disabled=false;
  busy($('predict-submit'),false);busy(predictionOutput,false);
  document.querySelectorAll('[data-counts]').forEach(button=>button.setAttribute('aria-pressed','false'));
  $('predict-submit').textContent='Generate prediction →';
  if ($('prediction-value').textContent.trim() !== '—')
    $('prediction-status').textContent = 'Inputs changed. Generate a new prediction to update this result.';
}));
document.querySelectorAll('[data-counts]').forEach(button => {
  button.onclick = () => {
    document.querySelectorAll('[data-counts]').forEach(preset=>preset.setAttribute('aria-pressed',String(preset===button)));
    button.dataset.counts.split(',').forEach((value,i) => { $(predictionInputs[i]).value = value; });
    $('predict-form').requestSubmit();
  };
});
$('predict-form').onsubmit = async event => {
  event.preventDefault();
  const button = $('predict-submit');
  const counts = predictionInputs.map(id => Number($(id).value));
  $('predict-error').textContent = '';
  if (predictionInputs.some(id => !$(id).value.trim()) || counts.some(n => !Number.isInteger(n) || n < 0 || n > 100)) {
    $('predict-error').textContent = 'Enter three whole vehicle counts from 0 to 100.';
    return;
  }
  button.disabled = true;
  button.textContent = 'Running the model…';
  busy(button,true);busy(predictionOutput,true);
  const request=++predictionRequest;
  try {
    const result = await get('/api/predict?counts=' + counts.join(','));
    if(request!==predictionRequest)return;
    countTo($('prediction-value'),result.prediction,{decimals:2,unit:'vehicles'});
    $('prediction-description').textContent = `About ${result.rounded_prediction} ${result.rounded_prediction===1?'arrival':'arrivals'} expected during the next ${result.horizon_seconds} seconds.`;
    $('prediction-meaning').textContent = 'A decimal is normal: it is the average expectation from 60 trees, not a partial car.';
    $('prediction-note').textContent = result.note;
    $('prediction-status').textContent = `Result for ${result.inputs.join(' → ')} cars (newest to oldest). Average test error: ${result.test_mae.toFixed(2)} cars.`;
    const values = [...result.inputs.slice().reverse(),result.prediction];
    const labels = ['20–30s ago','10–20s ago','Last 10s','Next 10s'];
    const max = Math.max(1,...values);
    $('prediction-bars').innerHTML = values.map((value,i) => `<div class="prediction-row"><span>${labels[i]}</span><div><i style="width:${value/max*100}%"></i></div><b>${i===3?value.toFixed(2):value}</b></div>`).join('');
  } catch (error) { if(request===predictionRequest)$('predict-error').textContent = error.message; }
  finally { if(request===predictionRequest){button.disabled = false; button.textContent = 'Generate prediction →';busy(button,false);busy(predictionOutput,false);} }
};
const slides=[
['Smarter signals. Less waiting.','Smart Traffic Signal Optimization Using Machine Learning and Computer Vision','Our goal: reduce accumulated waiting at a four-way intersection while responding to uneven traffic demand. This is an academic simulation prototype.'],
['Why fixed timers fall short.','A fixed signal gives every approach the same 25-second green, even when demand is uneven. A busy road waits while an empty road has right of way.','Explain with a morning commute: North and South have many vehicles, but East and West still receive equal green time.'],
['A measurable project objective.','Compare fixed-time, queue-only adaptive, and ML-assisted control using identical generated traffic. Measure delay, vehicles served, and queues remaining.','The primary metric is accumulated queue-seconds divided by arrivals. We count waiting from unfinished vehicles too; departed-only averages can hide congestion.'],
['See → predict → decide.','Vision demonstration: image → segmentation → vehicle counts.<br>Simulation: recent arrivals → random forest forecast → priority score → signal phase.','Be explicit: the synthetic camera is a separate computer vision demonstration. The simulator uses full known queue and arrival counts, not the limited camera view.'],
['The model learns short-term demand.','Random forest regression · 60 trees<br>Inputs: three previous 10-second arrival counts.<br>Output: arrivals in the next 10 seconds.','Training uses 9,900 windows from 300 synthetic episodes. Testing uses 3,300 windows from 100 independent episodes. Compare MAE with persistence, which repeats the most recent count.'],
['A controller with clear rules.','Priority = queue + 0.7 × forecast + 0.08 × time since green.<br>10–45s green · 3s all-red transition · overdue queue priority.','The controller is heuristic, not reinforcement learning. After 90 seconds without green, a waiting approach gets priority at the next eligible decision; this is not a strict 90-second wait guarantee.'],
['Run the experiment.','Choose Morning rush. Run seed 42. Compare delay and throughput. Then try Balanced or Eastbound surge.','Switch to Intersection overview. Point to the signal, queue chart, and segmentation boxes. Show Model & methodology to compare queue-only with ML-assisted control. ML does not have to win every scenario.'],
['What the results mean.','Forecast error and traffic delay are different outcomes. Better prediction does not automatically guarantee better signal decisions.','Use the displayed results for the selected seed. The artifacts folder contains multi-seed evaluations. No real-world percentage reduction is claimed.'],
['The next intersection.','Real video + vehicle tracking.<br>Calibrated traffic simulation and turning lanes.<br>Pedestrian phases and safety validation.<br>Evaluate on real demand patterns.','Conclude: we built a working, reproducible experimental system connecting computer vision concepts, supervised learning, and adaptive control. Field deployment is future work.']];
function renderSlide(){const s=slides[slideIndex];$('slide').innerHTML=`<div class="number">${String(slideIndex+1).padStart(2,'0')} / FLOWSTATE</div><h1>${s[0]}</h1><div class="slide-body">${s[1]}</div><div class="notes"><b>SPEAKER NOTES</b><br>${s[2]}</div>`;enter($('slide'));$('slide-count').textContent=`${slideIndex+1} / ${slides.length}`;$('prev').disabled=slideIndex===0;$('next').disabled=slideIndex===slides.length-1}
$('prev').onclick=()=>{slideIndex=Math.max(0,slideIndex-1);renderSlide()};$('next').onclick=()=>{slideIndex=Math.min(slides.length-1,slideIndex+1);renderSlide()};$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('presentation').requestFullscreen()}catch(e){$('connection-error').hidden=false;$('error').textContent='Fullscreen is unavailable in this browser.';view('dashboard')}};document.addEventListener('keydown',e=>{if(!$('presentation').classList.contains('hidden')){if(e.key==='ArrowRight')$('next').click();if(e.key==='ArrowLeft')$('prev').click()}});
FlowStateMotion.observe();
if (location.protocol !== 'file:') run();
