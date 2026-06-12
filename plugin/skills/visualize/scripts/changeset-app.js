(function(){'use strict';
var $=function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s));};
var RM=false;try{RM=window.matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(e){}
var VX={};try{VX=JSON.parse(document.getElementById('vx-data').textContent);}catch(e){}
var tabs=$('.view-tab'),views=$('.view'),steps=$('.tour-step'),dots=$('.tn-dots li'),fdots=$('.fdot'),psegs=$('.pseg');
var cur=0,jIdx=-1;
function flash(el){try{el.style.transition='box-shadow 180ms ease';el.style.boxShadow='0 0 0 3px rgba(217,119,87,0.4)';setTimeout(function(){el.style.boxShadow='';},1200);}catch(e){}}

/* ---- view switching with View Transitions ---- */
/* the page uses CSS scroll-behavior:smooth, so programmatic restores must
   force instant scrolling or every tab switch animates a scroll */
var syncCond=function(){};
function instantScroll(y){
  /* settle the condensed-header state for the target position FIRST, with its
     transitions suppressed (body.snap) and geometry committed via reflow: the
     animated ~80px header collapse would otherwise shift content right after
     the restore (only scroll-anchoring browsers paper over it) */
  document.body.classList.add('snap');
  syncCond(y);
  void document.body.offsetWidth;
  var de=document.documentElement,old=de.style.scrollBehavior;
  de.style.scrollBehavior='auto';
  window.scrollTo(0,y);
  de.style.scrollBehavior=old;
  requestAnimationFrame(function(){document.body.classList.remove('snap');});
}
/* each view keeps its own scroll position; restoring it inside the view
   transition means the crossfade covers the scroll change too — otherwise the
   old position carries into a different-height view, clamps, and flips the
   condensed header: the visible "jump" on tab switch */
var curView=null,viewScroll={};
function applyView(key){
  if(curView&&curView!==key){viewScroll[curView]=window.scrollY||0;}
  tabs.forEach(function(t){t.setAttribute('aria-selected',String(t.dataset.view===key));});
  views.forEach(function(v){v.hidden=(v.dataset.view!==key);});
  if(curView&&curView!==key){instantScroll(viewScroll[key]||0);}
  curView=key;
  try{if(history.replaceState){history.replaceState(null,'','#view-'+key);}}catch(e){}
  updateProgress();
}
/* `after` runs once the target view is visible — scroll work passed here
   would silently no-op if run while the view is still display:none */
function activate(key,after){
  var run=function(){applyView(key);if(after){try{after();}catch(e){}}};
  try{
    if(!RM&&document.startViewTransition){document.startViewTransition(run);}
    else{run();}
  }catch(e){try{run();}catch(e2){}}
}
/* ---- stepper + filmstrip + mini-map sync ---- */
function syncMiniMap(){
  try{
    var c=steps[cur]?steps[cur].getAttribute('data-cluster'):null;
    var mods=(VX.clusterModules&&c&&VX.clusterModules[c])||[];
    var mini=document.getElementById('mini-map');
    var cap=document.getElementById('rail-cap');
    var hue=(VX.hues&&c)?VX.hues[c]:'';
    if(mini){
      if(hue){mini.style.setProperty('--ch',hue);}
      mini.classList.toggle('has-on',mods.length>0);
      $('rect.mn',mini).forEach(function(r){r.classList.toggle('on',mods.indexOf(r.getAttribute('data-k'))>=0);});
    }
    if(cap){
      cap.innerHTML='';
      if(hue){cap.style.setProperty('--ch',hue);}
      var lead=document.createElement('span');
      if(mods.length){
        lead.textContent='touches ';cap.appendChild(lead);
        mods.forEach(function(m,i){
          if(i){cap.appendChild(document.createTextNode(' · '));}
          var s=document.createElement('span');s.className='mod';s.textContent=(VX.moduleNames&&VX.moduleNames[m])||m;cap.appendChild(s);
        });
      }else{lead.textContent='cross-cutting — no single module owns this cluster';cap.appendChild(lead);}
    }
  }catch(e){}
}
function goStep(i,pulse){
  try{
    if(!steps.length){return;}
    cur=Math.max(0,Math.min(steps.length-1,i));
    steps.forEach(function(s,j){s.hidden=(j!==cur);});
    dots.forEach(function(d,j){d.setAttribute('aria-current',String(j===cur));});
    fdots.forEach(function(d,j){d.classList.toggle('cur',j===cur);});
    jIdx=-1;
    syncMiniMap();updateProgress();
    if(pulse){
      var sec=document.getElementById('change-narrative');
      if(sec){
        var r=sec.getBoundingClientRect();
        if(r.top<-10){window.scrollTo({top:window.scrollY+r.top-110,behavior:RM?'auto':'smooth'});}
      }
    }
  }catch(e){}
}
try{
  tabs.forEach(function(t){t.addEventListener('click',function(){activate(t.dataset.view);});});
  var m=(location.hash||'').match(/^#view-([a-z]+)$/);
  var init=(m&&views.some(function(v){return v.dataset.view===m[1];}))?m[1]:'overview';
  applyView(init);goStep(0,false);
}catch(e){}
try{
  $('.tn-prev').forEach(function(b){b.addEventListener('click',function(){goStep(cur-1,true);});});
  $('.tn-next').forEach(function(b){b.addEventListener('click',function(){goStep(cur+1,true);});});
  dots.forEach(function(d,j){d.addEventListener('click',function(){goStep(j,true);});});
  fdots.forEach(function(d,j){d.addEventListener('click',function(){goStep(j,true);});});
}catch(e){}
/* ---- cross-view jumps ---- */
function jumpToId(id){
  var target=document.getElementById(id);
  if(!target){return;}
  activate('tour',function(){
    var step=target.closest?target.closest('.tour-step'):null;
    if(step){goStep(steps.indexOf(step),false);}
    if(target.tagName==='DETAILS'){target.open=true;}
    target.scrollIntoView({block:'center'});
    flash(target);
  });
}
try{
  document.addEventListener('click',function(e){
    var el=e.target.closest?e.target.closest('[data-jump],[data-jump-step]'):null;
    if(!el){return;}
    e.preventDefault();
    if(el.dataset.jumpStep){activate('tour',function(){goStep(parseInt(el.dataset.jumpStep,10)-1,true);});return;}
    jumpToId(el.dataset.jump);
  });
}catch(e){}
/* ---- facet filters with fade ---- */
try{
  var active={risk:{},kind:{},cluster:{},dir:{}};
  var rows=$('.cw-filetable tbody tr'),clearBtn=document.getElementById('fb-clear');
  var shown=document.getElementById('ft-shown');
  function anyOn(f){var k;for(k in active[f]){if(active[f][k]){return true;}}return false;}
  function applyFilters(){
    var n=0;
    rows.forEach(function(r){
      var ok=['risk','kind','cluster'].every(function(f){return !anyOn(f)||active[f][r.dataset[f]];})
        &&(!anyOn('dir')||!!active.dir[r.dataset.dir]||!!active.dir[r.dataset.dir2]);
      if(ok){n++;}
      if(ok===!r.hidden&&!r.classList.contains('fad')){return;}
      if(RM){r.hidden=!ok;r.classList.remove('fad');return;}
      if(!ok){
        r.classList.add('fad');
        setTimeout(function(){if(r.classList.contains('fad')){r.hidden=true;}},150);
      }else{
        r.hidden=false;
        requestAnimationFrame(function(){requestAnimationFrame(function(){r.classList.remove('fad');});});
      }
    });
    if(shown){shown.textContent=String(n);}
    if(clearBtn){clearBtn.hidden=!['risk','kind','cluster','dir'].some(anyOn);}
  }
  $('.fchip[data-facet],.fseg[data-facet]').forEach(function(c){
    c.setAttribute('aria-pressed','false');
    c.addEventListener('click',function(){
      var on=c.getAttribute('aria-pressed')==='true';
      c.setAttribute('aria-pressed',String(!on));
      active[c.dataset.facet][c.dataset.val]=!on;
      applyFilters();
    });
  });
  if(clearBtn){clearBtn.addEventListener('click',function(){
    active={risk:{},kind:{},cluster:{},dir:{}};
    $('.fchip[data-facet],.fseg[data-facet]').forEach(function(c){c.setAttribute('aria-pressed','false');});
    applyFilters();
  });}
}catch(e){}
/* ---- linked model: hover lights all counterparts ---- */
try{
  var litMap={};
  $('[data-cluster],[data-clusters]').forEach(function(el){
    var ids=(el.getAttribute('data-cluster')||el.getAttribute('data-clusters')||'').split(' ');
    ids.forEach(function(id){if(!id){return;}if(!litMap[id]){litMap[id]=[];}litMap[id].push(el);});
  });
  var litCur=null;
  function setLit(id,on){(litMap[id]||[]).forEach(function(el){el.classList.toggle('lit',on);});}
  document.addEventListener('mouseover',function(e){
    var el=e.target.closest?e.target.closest('[data-cluster],[data-clusters]'):null;
    var id=el?(el.getAttribute('data-cluster')||(el.getAttribute('data-clusters')||'').split(' ')[0]):null;
    if(id===litCur){return;}
    if(litCur){setLit(litCur,false);}
    litCur=id;
    if(id){setLit(id,true);}
  });
}catch(e){}
/* ---- reading-progress bar ---- */
function updateProgress(){
  try{
    var tourOn=views.some(function(v){return v.dataset.view==='tour'&&!v.hidden;});
    psegs.forEach(function(seg,j){
      var fill=seg.querySelector('.pfill');if(!fill){return;}
      if(!tourOn){fill.style.width='0%';return;}
      if(j<cur){fill.style.width='100%';}
      else if(j>cur){fill.style.width='0%';}
      else{
        var st=steps[cur];if(!st){fill.style.width='0%';return;}
        var r=st.getBoundingClientRect();
        var vh=window.innerHeight||1;
        var p=Math.max(0,Math.min(1,(vh-r.top)/(r.height+vh)));
        fill.style.width=(p*100).toFixed(1)+'%';
      }
    });
  }catch(e){}
}
try{
  psegs.forEach(function(seg){seg.addEventListener('click',function(){activate('tour',function(){goStep(parseInt(seg.dataset.step,10)-1,true);});});});
  window.addEventListener('scroll',updateProgress,{passive:true});
}catch(e){}
/* ---- header condense ---- */
try{
  var condensed=false;
  syncCond=function(yOpt){
    var y=(typeof yOpt==='number')?yOpt:(window.scrollY||0);
    if(!condensed&&y>90){condensed=true;document.body.classList.add('cond');}
    else if(condensed&&y<40){condensed=false;document.body.classList.remove('cond');}
  };
  window.addEventListener('scroll',function(){syncCond();},{passive:true});
}catch(e){}
/* ---- KPI count-up ---- */
try{
  var counted=false;
  function countUp(){
    if(counted){return;}counted=true;
    $('.cnt').forEach(function(el){
      var n=parseInt(el.getAttribute('data-n'),10)||0;
      if(RM){el.textContent=String(n);return;}
      var t0=null;
      function tick(ts){
        if(t0===null){t0=ts;}
        var x=Math.min(1,(ts-t0)/600);
        el.textContent=String(Math.round(n*(1-Math.pow(1-x,3))));
        if(x<1){requestAnimationFrame(tick);}
      }
      requestAnimationFrame(tick);
    });
  }
  var strip=document.querySelector('.kpi-strip');
  if(strip&&window.IntersectionObserver){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){countUp();io.disconnect();}});});
    io.observe(strip);
  }else{countUp();}
}catch(e){}
/* ---- mosaic settle + anchored tooltip ---- */
try{
  var mosaic=document.querySelector('.mosaic');
  if(mosaic&&!RM){
    var FK='andthen:visualize:settled:'+(VX.sha||'');
    if(!sessionStorage.getItem(FK)){mosaic.classList.add('play');sessionStorage.setItem(FK,'1');}
  }
}catch(e){}
try{
  var tip=document.getElementById('tip');
  function showTip(t){
    if(!tip){return;}
    tip.innerHTML='';
    var p=document.createElement('div');p.className='tp';p.textContent=t.getAttribute('data-path')||'';tip.appendChild(p);
    var d=document.createElement('div');d.className='td';
    var parts=(t.getAttribute('data-delta')||'').split(' ');
    var a=document.createElement('span');a.className='add';a.textContent=parts[0]||'';
    var dd=document.createElement('span');dd.className='del';dd.textContent=parts[1]||'';
    d.appendChild(a);d.appendChild(document.createTextNode(' '));d.appendChild(dd);tip.appendChild(d);
    var r=document.createElement('div');r.className='tr';r.textContent=t.getAttribute('data-role')||'';tip.appendChild(r);
    var hk=t.getAttribute('data-hunks');
    if(hk){
      var lbl=document.createElement('div');lbl.className='txl';lbl.textContent='hunks in tour';tip.appendChild(lbl);
      var tx=document.createElement('div');tx.className='tx';
      hk.split(',').forEach(function(pair){
        var ad=pair.split('/');
        var wa=Math.max(3,Math.min(40,(parseInt(ad[0],10)||0)*3));
        var wd=Math.max(0,Math.min(40,(parseInt(ad[1],10)||0)*3));
        var ia=document.createElement('i');ia.className='a';ia.style.width=wa+'px';tx.appendChild(ia);
        if(wd>0){var id2=document.createElement('i');id2.className='d';id2.style.width=wd+'px';tx.appendChild(id2);}
        tx.appendChild(document.createTextNode(' '));
      });
      tip.appendChild(tx);
    }
    tip.hidden=false;
    var tr=t.getBoundingClientRect(),pr=tip.getBoundingClientRect();
    var top=tr.top-pr.height-9;if(top<8){top=tr.bottom+9;}
    var left=Math.max(8,Math.min(window.innerWidth-pr.width-8,tr.left));
    tip.style.top=top+'px';tip.style.left=left+'px';
  }
  document.addEventListener('mouseover',function(e){
    var t=e.target.closest?e.target.closest('.has-tip[data-path]'):null;
    if(t){showTip(t);}else if(tip&&!tip.hidden){tip.hidden=true;}
  });
  window.addEventListener('scroll',function(){if(tip&&!tip.hidden){tip.hidden=true;}},{passive:true});
}catch(e){}
/* ---- sparkline draw-in ---- */
try{
  if(window.IntersectionObserver){
    var sio=new IntersectionObserver(function(es){es.forEach(function(en){
      if(en.isIntersecting){en.target.classList.add('reveal');sio.unobserve(en.target);}
    });},{threshold:0.4});
    $('.spark').forEach(function(s){sio.observe(s);});
  }else{$('.spark').forEach(function(s){s.classList.add('reveal');});}
}catch(e){}
/* ---- mark reviewed ---- */
try{
  var RK='andthen:visualize:reviewed:'+(VX.sha||'');
  var reviewed=[];
  try{reviewed=JSON.parse(localStorage.getItem(RK)||'[]');}catch(e1){}
  function paintReviewed(){
    steps.forEach(function(st){
      var c=st.getAttribute('data-cluster'),on=reviewed.indexOf(c)>=0;
      st.classList.toggle('reviewed',on);
      var b=st.querySelector('.btn-rev span');if(b){b.textContent=on?'Reviewed':'Mark reviewed';}
    });
    fdots.forEach(function(d){d.classList.toggle('done',reviewed.indexOf(d.getAttribute('data-cluster'))>=0);});
    psegs.forEach(function(s){s.classList.toggle('done',reviewed.indexOf(s.getAttribute('data-cluster'))>=0);});
    $('.cw-filetable tbody tr').forEach(function(r){r.classList.toggle('rev',reviewed.indexOf(r.getAttribute('data-cluster'))>=0);});
    var banner=document.getElementById('done-banner');
    if(banner){banner.hidden=(reviewed.length<steps.length);}
  }
  $('.btn-rev').forEach(function(b){
    b.addEventListener('click',function(){
      var c=b.getAttribute('data-rev'),i=reviewed.indexOf(c);
      if(i>=0){reviewed.splice(i,1);}else{reviewed.push(c);}
      try{localStorage.setItem(RK,JSON.stringify(reviewed));}catch(e2){}
      paintReviewed();
    });
  });
  paintReviewed();
}catch(e){}
/* ---- hunk spotlight ---- */
try{
  if(window.IntersectionObserver){
    var hio=new IntersectionObserver(function(es){
      es.forEach(function(en){en.target.classList.toggle('spot',en.isIntersecting);});
      steps.forEach(function(st){st.classList.toggle('has-spot',!!st.querySelector('.cw-hunk.spot'));});
    },{rootMargin:'-40% 0px -40% 0px'});
    $('.cw-hunk').forEach(function(h){hio.observe(h);});
  }
}catch(e){}
/* ---- copy path ---- */
try{
  document.addEventListener('click',function(e){
    var cp=e.target.closest?e.target.closest('.copy-path'):null;
    if(!cp){return;}
    var path=cp.getAttribute('data-copy')||cp.textContent;
    try{navigator.clipboard.writeText(path);}catch(e1){}
    cp.classList.add('copied');
    var fl=cp.parentNode?cp.parentNode.querySelector('.copy-flash'):null;
    if(fl){fl.classList.add('show');}
    setTimeout(function(){cp.classList.remove('copied');if(fl){fl.classList.remove('show');}},1200);
  });
}catch(e){}
/* ---- architecture: blast radius + play flow ---- */
try{
  var chip=document.getElementById('blast-chip');
  var mainMap=document.getElementById('main-map');
  function nodesByKeys(keys){return $('.node[data-k]',mainMap).filter(function(n){return keys.indexOf(n.getAttribute('data-k'))>=0;});}
  if(mainMap){
    mainMap.addEventListener('mouseover',function(e){
      var n=e.target.closest?e.target.closest('.node[data-k]'):null;
      if(!n){return;}
      var k=n.getAttribute('data-k'),set=(VX.blast&&VX.blast[k])||[];
      nodesByKeys(set).forEach(function(x){x.classList.add('halo');});
      if(chip){chip.hidden=false;chip.textContent=set.length?('affects '+set.length+' module'+(set.length===1?'':'s')):'no dependents';}
    });
    mainMap.addEventListener('mouseout',function(e){
      var n=e.target.closest?e.target.closest('.node[data-k]'):null;
      if(!n){return;}
      $('.node.halo',mainMap).forEach(function(x){x.classList.remove('halo');});
      if(chip){chip.hidden=true;}
    });
  }
  var pf=document.getElementById('play-flow');
  if(pf&&mainMap){
    pf.addEventListener('click',function(){
      var depths=VX.bfs||[];if(!depths.length){return;}
      pf.disabled=true;
      var all=[];depths.forEach(function(d){all=all.concat(d);});
      function clear(){$('.node.pulse',mainMap).forEach(function(x){x.classList.remove('pulse');});pf.disabled=false;}
      if(RM){nodesByKeys(all).forEach(function(x){x.classList.add('pulse');});setTimeout(clear,1500);return;}
      depths.forEach(function(d,i){setTimeout(function(){nodesByKeys(d).forEach(function(x){x.classList.add('pulse');});},i*250);});
      setTimeout(clear,depths.length*250+1400);
    });
  }
}catch(e){}
/* ---- architecture selection: nodes + edges + sticky panel + toggle + matrix ---- */
try{
  var adBody=document.getElementById('ad-body');
  var selMap=document.getElementById('main-map');
  var AD=VX.archDetail||{};
  var AE=VX.archEdges||[];
  function zoneEl(title){var z=document.createElement('div');z.className='ad-zone';var h=document.createElement('h4');h.textContent=title;z.appendChild(h);return z;}
  function linkBtn(label,attr,val,hue){
    var b=document.createElement('button');b.type='button';
    b.className=(attr==='data-jump-step')?'ad-chip':'ad-link';
    b.textContent=label;b.setAttribute(attr,val);
    if(hue){b.style.setProperty('--ch',hue);}
    return b;
  }
  function chipClsFor(st){return st==='new'?'rk-new':st==='removed'?'rk-removed':st==='changed'?'rk-changed':'';}
  function setHead(chipText,chipCls,title,meta,body){
    if(!adBody){return;}
    var c=document.getElementById('ad-chip');
    if(c){c.textContent=chipText;c.className='rel-chip '+(chipCls||'');}
    var t=adBody.querySelector('[data-role="title"]');if(t){t.textContent=title;}
    var m=adBody.querySelector('[data-role="meta"]');if(m){m.textContent=meta;}
    var b=adBody.querySelector('[data-role="body"]');if(b){b.textContent=body;}
  }
  /* node zone markup has a single owner: the build-time zonesHtml(), baked per
     node into VX.archDetail[k].z — swapping innerHTML keeps the initial panel
     and every later selection pixel-identical (no dual-renderer drift) */
  function renderNodeZones(k){
    var d=AD[k];
    var zones=document.getElementById('ad-zones');
    if(!d||!zones){return;}
    zones.innerHTML=d.z||'';
  }
  function withFade(fn){
    if(!adBody||RM){fn();return;}
    adBody.classList.add('fading');
    setTimeout(function(){fn();void adBody.offsetWidth;adBody.classList.remove('fading');},150);
  }
  function clearSel(){if(selMap){$('.sel',selMap).forEach(function(x){x.classList.remove('sel');});}}
  function selectNode(k,skipFade){
    if(!selMap){return;}
    clearSel();
    var n=selMap.querySelector('.node[data-k="'+k+'"]');
    if(n){n.classList.add('sel');}
    var d=AD[k];if(!d){return;}
    var doIt=function(){setHead(d.st||'unchanged',chipClsFor(d.st),d.t,d.m,d.b||'');renderNodeZones(k);};
    if(skipFade){doIt();}else{withFade(doIt);}
  }
  function selectEdge(i){
    if(!selMap){return;}
    var e=AE[i];if(!e){return;}
    clearSel();
    var g=selMap.querySelector('g.eg[data-e="'+i+'"]');
    if(g){g.classList.add('sel');}
    withFade(function(){
      setHead(e.st||(e.kind||'edge'),chipClsFor(e.st),e.fromName+' → '+e.toName,'edge'+(e.kind?(' · '+e.kind):''),e.label||'');
      var zones=document.getElementById('ad-zones');if(!zones){return;}
      zones.innerHTML='';
      var z=zoneEl('endpoints');
      var box=document.createElement('div');box.className='ad-links';
      box.appendChild(linkBtn(e.fromName,'data-selnode',e.fk));
      box.appendChild(linkBtn(e.toName,'data-selnode',e.tk));
      z.appendChild(box);zones.appendChild(z);
      if(e.label){
        var z2=zoneEl('authored relationship');
        var p=document.createElement('p');p.className='ad-blast';p.textContent=e.label;
        z2.appendChild(p);zones.appendChild(z2);
      }
    });
  }
  if(selMap){
    selMap.addEventListener('click',function(ev){
      var n=ev.target.closest?ev.target.closest('.node[data-k]'):null;
      if(n){selectNode(n.getAttribute('data-k'));return;}
      var g=ev.target.closest?ev.target.closest('g.eg[data-e]'):null;
      if(g){selectEdge(parseInt(g.getAttribute('data-e'),10));}
    });
  }
  document.addEventListener('click',function(ev){
    var b=ev.target.closest?ev.target.closest('[data-selnode]'):null;
    if(!b||b.classList.contains('imx-dot')){return;}
    selectNode(b.getAttribute('data-selnode'));
  });
  $('.ba-seg').forEach(function(seg){
    seg.addEventListener('click',function(){
      $('.ba-seg').forEach(function(s2){s2.setAttribute('aria-pressed',String(s2===seg));});
      if(selMap){
        selMap.classList.toggle('st-before',seg.getAttribute('data-st')==='before');
        selMap.classList.toggle('st-after',seg.getAttribute('data-st')!=='before');
      }
    });
  });
  var imx=document.querySelector('.imx');
  var pop=document.getElementById('imx-pop');
  if(imx){
    imx.addEventListener('mouseover',function(ev){
      var c=ev.target.closest?ev.target.closest('[data-col]'):null;
      $('.hi',imx).forEach(function(x){x.classList.remove('hi');});
      if(c){
        var key=c.getAttribute('data-col');
        $('[data-col="'+key+'"]',imx).forEach(function(x){x.classList.add('hi');});
      }
    });
    imx.addEventListener('mouseleave',function(){$('.hi',imx).forEach(function(x){x.classList.remove('hi');});});
    imx.addEventListener('click',function(ev){
      var dot=ev.target.closest?ev.target.closest('.imx-dot'):null;
      if(!dot||!pop){return;}
      var mk=dot.getAttribute('data-mk'),st=dot.getAttribute('data-step');
      selectNode(mk);
      pop.innerHTML='';
      var t=document.createElement('span');t.className='pp-t';t.textContent=((VX.moduleNames||{})[mk]||mk)+' · C'+st;pop.appendChild(t);
      pop.appendChild(linkBtn('module details →','data-selnode',mk));
      pop.appendChild(linkBtn('open C'+st+' in tour →','data-jump-step',st,(VX.hues||{})['c'+st]));
      pop.hidden=false;
      var r=dot.getBoundingClientRect(),pr=pop.getBoundingClientRect();
      pop.style.left=Math.max(8,Math.min(window.innerWidth-pr.width-8,r.left-10))+'px';
      pop.style.top=(r.bottom+8)+'px';
    });
  }
  if(pop){
    document.addEventListener('mousedown',function(ev){
      if(!pop.hidden&&!(ev.target.closest&&ev.target.closest('.imx-pop,.imx-dot'))){pop.hidden=true;}
    });
    pop.addEventListener('click',function(ev){
      if(ev.target.closest&&ev.target.closest('button')){setTimeout(function(){pop.hidden=true;},60);}
    });
  }
}catch(e){}
/* ---- zoom/pan via viewBox + mini-map lightbox ---- */
function wireZoom(svg){
  try{
    var vb0=(svg.getAttribute('viewBox')||'0 0 100 100').split(/\s+/).map(Number);
    var vb=vb0.slice();
    function apply(){svg.setAttribute('viewBox',vb.join(' '));}
    function zoomAt(f,cx,cy){
      var px=vb[0]+cx*vb[2],py=vb[1]+cy*vb[3];
      var w=Math.min(vb0[2]*4,Math.max(vb0[2]/16,vb[2]*f));
      vb[3]=w*vb0[3]/vb0[2];vb[2]=w;
      vb[0]=px-cx*vb[2];vb[1]=py-cy*vb[3];apply();
    }
    function rel(e){var r=svg.getBoundingClientRect();return [(e.clientX-r.left)/Math.max(1,r.width),(e.clientY-r.top)/Math.max(1,r.height)];}
    svg.addEventListener('wheel',function(e){e.preventDefault();var c=rel(e);zoomAt(e.deltaY>0?1.2:1/1.2,c[0],c[1]);},{passive:false});
    svg.addEventListener('dblclick',function(e){e.preventDefault();var c=rel(e);zoomAt(1/1.5,c[0],c[1]);});
    /* pan only after a 4px movement threshold — capturing on pointerdown retargets
       the ensuing click to the svg root and kills node/edge selection */
    var pan=null,moved=false,suppressClick=false;
    svg.addEventListener('pointerdown',function(e){pan=[e.clientX,e.clientY,vb[0],vb[1],e.pointerId];moved=false;});
    svg.addEventListener('pointermove',function(e){
      if(!pan){return;}
      var dx=e.clientX-pan[0],dy=e.clientY-pan[1];
      if(!moved){
        if(Math.abs(dx)<4&&Math.abs(dy)<4){return;}
        moved=true;
        svg.classList.add('panning');
        try{svg.setPointerCapture(pan[4]);}catch(e2){}
      }
      var r=svg.getBoundingClientRect();
      vb[0]=pan[2]-dx*vb[2]/Math.max(1,r.width);
      vb[1]=pan[3]-dy*vb[3]/Math.max(1,r.height);
      apply();
    });
    ['pointerup','pointercancel'].forEach(function(ev){svg.addEventListener(ev,function(){
      if(moved){suppressClick=true;}
      pan=null;moved=false;svg.classList.remove('panning');
    });});
    svg.addEventListener('click',function(e){
      if(suppressClick){suppressClick=false;e.stopPropagation();e.preventDefault();}
    },true);
    return {zoom:function(f){zoomAt(f,0.5,0.5);},reset:function(){vb=vb0.slice();apply();}};
  }catch(e){return null;}
}
try{
  var mm=document.getElementById('main-map');
  if(mm){
    var z=wireZoom(mm);
    var zi=document.getElementById('zoom-in'),zo=document.getElementById('zoom-out'),zr=document.getElementById('zoom-reset');
    if(z&&zi){zi.addEventListener('click',function(){z.zoom(1/1.3);});}
    if(z&&zo){zo.addEventListener('click',function(){z.zoom(1.3);});}
    if(z&&zr){zr.addEventListener('click',function(){z.reset();});}
  }
  var lbEl=document.getElementById('lightbox');
  var miniEl=document.getElementById('mini-map');
  if(lbEl&&miniEl&&mm){
    miniEl.addEventListener('click',function(){
      var card=lbEl.querySelector('.lb-card');
      if(!card){return;}
      card.innerHTML='';
      var x=document.createElement('button');x.className='lb-close';x.textContent='×';x.setAttribute('aria-label','Close');
      x.addEventListener('click',function(){lbEl.hidden=true;});
      card.appendChild(x);
      var clone=mm.cloneNode(true);
      clone.removeAttribute('id');
      card.appendChild(clone);
      lbEl.hidden=false;
      wireZoom(clone);
    });
    lbEl.addEventListener('mousedown',function(e){if(e.target===lbEl){lbEl.hidden=true;}});
  }
}catch(e){}
/* ---- command palette + cheatsheet + j/k ---- */
try{
  var cmdk=document.getElementById('cmdk'),cin=document.getElementById('cmdk-in'),clist=document.getElementById('cmdk-list');
  var keys=document.getElementById('keys-pop');
  var sel=0,results=[];
  function fuzzy(q,s){
    var qi=0,score=0,last=-2;s=s.toLowerCase();
    for(var i=0;i<s.length&&qi<q.length;i++){
      if(s[i]===q[qi]){score+=(i===last+1)?2:1;last=i;qi++;}
    }
    return qi===q.length?score:-1;
  }
  function renderList(){
    if(!clist){return;}
    clist.innerHTML='';
    if(!results.length){
      var li=document.createElement('li');li.className='empty';li.textContent='no matches';clist.appendChild(li);return;
    }
    results.forEach(function(it,i){
      var li=document.createElement('li');if(i===sel){li.className='sel';}
      var ct=document.createElement('span');ct.className='ct t-'+it.t;ct.textContent=it.t;li.appendChild(ct);
      var cl=document.createElement('span');cl.className='cl';cl.textContent=it.label;li.appendChild(cl);
      var cs=document.createElement('span');cs.className='cs';cs.textContent=it.sub||'';li.appendChild(cs);
      li.addEventListener('mousedown',function(ev){ev.preventDefault();go(it);});
      clist.appendChild(li);
    });
  }
  function filter(){
    var q=(cin?cin.value:'').trim().toLowerCase();
    var items=VX.palette||[];
    if(!q){results=items.slice(0,12);}
    else{
      results=items.map(function(it){return {it:it,s:fuzzy(q,it.label)};})
        .filter(function(x){return x.s>=0;})
        .sort(function(a,b){return b.s-a.s;})
        .slice(0,12).map(function(x){return x.it;});
    }
    sel=0;renderList();
  }
  function openK(){if(!cmdk){return;}cmdk.hidden=false;if(cin){cin.value='';cin.focus();}filter();}
  function closeK(){if(cmdk){cmdk.hidden=true;}}
  function go(it){
    closeK();
    if(it.t==='cluster'){activate('tour',function(){goStep(it.n-1,true);});}
    else if(it.t==='file'){jumpToId(it.jump);}
    else if(it.t==='module'){
      activate('arch',function(){
        var n=document.querySelector('#main-map .node[data-k="'+it.key+'"]');
        if(n){
          try{n.dispatchEvent(new MouseEvent('click',{bubbles:true}));}catch(e1){}
          n.scrollIntoView({block:'center'});flash(n);
        }
      });
    }
  }
  if(cin){
    cin.addEventListener('input',filter);
    cin.addEventListener('keydown',function(e){
      if(e.key==='ArrowDown'){sel=Math.min(results.length-1,sel+1);renderList();e.preventDefault();}
      else if(e.key==='ArrowUp'){sel=Math.max(0,sel-1);renderList();e.preventDefault();}
      else if(e.key==='Enter'){if(results[sel]){go(results[sel]);}e.preventDefault();}
      else if(e.key==='Tab'){e.preventDefault();}
      else if(e.key==='Escape'){closeK();e.preventDefault();}
    });
  }
  if(cmdk){cmdk.addEventListener('mousedown',function(e){if(e.target===cmdk){closeK();}});}
  document.addEventListener('keydown',function(e){
    if((e.metaKey||e.ctrlKey)&&(e.key==='k'||e.key==='K')){e.preventDefault();if(cmdk&&cmdk.hidden){openK();}else{closeK();}return;}
    var tag=(e.target&&e.target.tagName)||'';
    if(tag==='TEXTAREA'||tag==='INPUT'){return;}
    if(e.key==='Escape'){
      var lbx=document.getElementById('lightbox');
      if(lbx&&!lbx.hidden){lbx.hidden=true;return;}
      closeK();if(keys){keys.hidden=true;}return;
    }
    if(e.key==='?'){if(keys){keys.hidden=!keys.hidden;}return;}
    var tourOn=views.some(function(v){return v.dataset.view==='tour'&&!v.hidden;});
    if(!tourOn){return;}
    if(e.key==='ArrowLeft'){goStep(cur-1,true);}
    if(e.key==='ArrowRight'){goStep(cur+1,true);}
    if(e.key==='j'||e.key==='k'){
      var files=$('.tour-step .cw-file');
      if(!files.length){return;}
      jIdx=(e.key==='j')?Math.min(files.length-1,jIdx+1):Math.max(0,jIdx-1);
      var f=files[jIdx],st=f.closest('.tour-step');
      if(st&&st.hidden){goStep(steps.indexOf(st),false);}
      f.open=true;f.scrollIntoView({block:'center'});flash(f);
    }
  });
}catch(e){}
/* ---- notes drawer toggle ---- */
try{
  var drawer=document.getElementById('notes-drawer'),toggle=document.getElementById('notes-toggle');
  if(drawer&&toggle){toggle.addEventListener('click',function(){drawer.hidden=!drawer.hidden;});}
}catch(e){}
updateProgress();
})();
