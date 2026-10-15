/* Small, cancellable transitions. Every animated number finishes at the API value. */
(function (root) {
  const reduced = root.matchMedia('(prefers-reduced-motion: reduce)');
  const frames = new WeakMap();
  function countTo(element, value, {decimals=0, unit='', prefix=''} = {}) {
    if (frames.has(element)) root.cancelAnimationFrame(frames.get(element));
    const startValue=Number(element.dataset.value || 0);
    element.dataset.value=String(value);
    const number=document.createElement('span');
    const suffix=document.createElement('small');
    const accessible=document.createElement('span');
    number.setAttribute('aria-hidden','true');
    suffix.setAttribute('aria-hidden','true');
    accessible.className='sr-only';
    accessible.textContent=`${prefix}${value.toFixed(decimals)} ${unit}`.trim();
    suffix.textContent=unit;
    element.replaceChildren(number,suffix,accessible);
    const write=n => { number.textContent=prefix+n.toFixed(decimals); };
    if (reduced.matches || element.closest('.hidden')) { write(value); return; }
    const started=root.performance.now();
    function step(now) {
      const progress=Math.min(1,(now-started)/650);
      write(startValue+(value-startValue)*(1-Math.pow(1-progress,3)));
      if(progress<1) frames.set(element,root.requestAnimationFrame(step));
      else { write(value); frames.delete(element); }
    }
    frames.set(element,root.requestAnimationFrame(step));
  }
  function enter(element) {
    if(reduced.matches || !element.animate)return;
    element.getAnimations().forEach(animation=>animation.cancel());
    element.animate([{opacity:0,transform:'translateY(10px)'},{opacity:1,transform:'none'}],
      {duration:420,easing:'cubic-bezier(.22,1,.36,1)'});
  }
  function busy(element, value) {
    element.classList.toggle('is-loading',value);
    element.setAttribute('aria-busy',String(value));
  }
  function observe() {
    if(reduced.matches || !('IntersectionObserver' in root))return;
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}
    }),{threshold:.08});
    document.querySelectorAll('.panel,.metrics,.pipeline article').forEach(element=>{
      element.classList.add('reveal-ready');observer.observe(element);
    });
  }
  root.FlowStateMotion={countTo,enter,busy,observe,reduced};
})(globalThis);
