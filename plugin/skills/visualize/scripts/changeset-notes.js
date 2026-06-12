(function(){'use strict';
var ARTIFACT_PATH='__ARTIFACT_PATH__';
var ARTIFACT_OWNER='andthen:explain-changes';
var ARTIFACT_SHA1='__ARTIFACT_SHA1__';
var $=function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s));};

/* ---- state (render-shell.md Notes State Shape) ---- */
var tabUuid='';
try{
  tabUuid=sessionStorage.getItem('andthen-visualize-tab-uuid')||'';
  if(!tabUuid){
    tabUuid=(window.crypto&&crypto.randomUUID)?crypto.randomUUID():('t-'+Date.now()+'-'+Math.floor(Math.random()*1e9));
    sessionStorage.setItem('andthen-visualize-tab-uuid',tabUuid);
  }
}catch(e){tabUuid='t-volatile';}
var state={
  artifactPath:ARTIFACT_PATH,
  artifactOwner:ARTIFACT_OWNER,
  artifactSha1:ARTIFACT_SHA1,
  tabUuid:tabUuid,
  notes:[],
  notesDirty:false
};

/* ---- payload formatters (render-shell.md, verbatim) ---- */
function buildSectionBlock(headingVerbatim, notesForSection) {
  var lines = ['## Section: ' + headingVerbatim.trim(), ''];
  notesForSection.forEach(function (n) {
    lines.push('- ' + n.text.replace(/\n/g, '\n  '));
  });
  return lines.join('\n');
}
function buildPayload(notes, artifactPath, artifactOwner) {
  var header = '# ' + artifactOwner + ' visual review notes for ' + artifactPath + '\n';
  var groups = [];
  var byAnchor = Object.create(null);
  notes.forEach(function (n) {
    if (!byAnchor[n.sectionAnchor]) {
      byAnchor[n.sectionAnchor] = { heading: n.headingVerbatim, items: [] };
      groups.push(byAnchor[n.sectionAnchor]);
    }
    byAnchor[n.sectionAnchor].items.push(n);
  });
  return header + '\n' + groups.map(function (g) {
    return buildSectionBlock(g.heading, g.items);
  }).join('\n\n') + '\n';
}

/* ---- LocalStorage (render-shell.md) ---- */
function lsKey(){return 'andthen:visualize:'+state.artifactSha1+':'+state.tabUuid;}
function saveToLocalStorage(){
  try{
    localStorage.setItem(lsKey(),JSON.stringify({
      artifactPath:state.artifactPath,
      artifactOwner:state.artifactOwner,
      tabUuid:state.tabUuid,
      notes:state.notes,
      updatedAt:new Date().toISOString()
    }));
  }catch(e){}
}

/* ---- pulseAnchor (js-helpers.md, verbatim) ---- */
function pulseAnchor(targetEl) {
  if (!targetEl) return;
  targetEl.style.transition = 'box-shadow 180ms ease';
  targetEl.style.boxShadow = '0 0 0 3px rgba(217, 119, 87, 0.4)';
  setTimeout(function () { targetEl.style.boxShadow = 'none'; }, 1400);
}

/* ---- copySectionWithNote (js-helpers.md, verbatim) ---- */
async function copySectionWithNote(sectionEl) {
  try {
    var heading = sectionEl.getAttribute('data-heading')
      || (sectionEl.querySelector(':scope > .card-head h2') || {}).textContent || '';
    var anchor = sectionEl.getAttribute('data-anchor') || sectionEl.id;
    var sectionNotes = state.notes.filter(function (n) { return n.sectionAnchor === anchor; });
    var payload = buildSectionBlock(heading, sectionNotes);
    await navigator.clipboard.writeText(payload);
    return true;
  } catch (err) { return false; }
}

/* NOTE: js-helpers.md's wireModuleMap, snippet toggle, and .risk-map-chip/.toc
   handlers are intentionally omitted — this app's map selection, file blocks,
   and navigation are owned by the app script (a second map click handler would
   compete for the same detail panel). */

/* ---- notes DOM layer ---- */
var drawer=document.getElementById('notes-drawer');
var copyBtn=document.getElementById('copy-notes');
function fmtTime(iso){
  try{return new Date(iso).toLocaleString([], {month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});}catch(e){return '';}
}
function jumpToSection(anchor){
  try{
    var sec=document.querySelector('section.card[data-anchor="'+anchor+'"]');
    if(!sec){return;}
    var view=sec.closest('.view');
    if(view&&view.hidden){
      var tab=document.querySelector('.view-tab[data-view="'+view.getAttribute('data-view')+'"]');
      if(tab){tab.click();}
    }
    sec.scrollIntoView({block:'start'});
    pulseAnchor(sec);
  }catch(e){}
}
function renderNotes(){
  try{
    $('section.card').forEach(function(sec){
      var anchor=sec.getAttribute('data-anchor');
      var ns=state.notes.filter(function(n){return n.sectionAnchor===anchor;});
      var badge=sec.querySelector('.note-count[data-role="count"]');
      if(badge){
        badge.textContent=String(ns.length);
        if(ns.length===0){badge.setAttribute('data-empty','1');}else{badge.removeAttribute('data-empty');}
      }
      var list=sec.querySelector('.note-area .note-list');
      if(list){
        list.innerHTML='';
        ns.forEach(function(n){
          var li=document.createElement('li');
          var txt=document.createElement('span');txt.className='nt';txt.textContent=n.text;
          var tm=document.createElement('time');tm.textContent=fmtTime(n.createdAt);
          var del=document.createElement('button');del.className='nx';del.textContent='×';
          del.setAttribute('data-del',String(state.notes.indexOf(n)));
          del.setAttribute('aria-label','Delete note');
          li.appendChild(txt);li.appendChild(tm);li.appendChild(del);
          list.appendChild(li);
        });
      }
    });
    var dl=document.querySelector('.notes-drawer .note-list');
    if(dl){
      dl.innerHTML='';
      state.notes.forEach(function(n,i){
        var li=document.createElement('li');
        var wrap=document.createElement('div');wrap.style.flex='1';wrap.style.minWidth='0';
        var h=document.createElement('span');h.className='nh';h.textContent=n.headingVerbatim;
        h.addEventListener('click',function(){jumpToSection(n.sectionAnchor);});
        var txt=document.createElement('span');txt.className='nt';txt.style.display='block';txt.textContent=n.text;
        var tm=document.createElement('time');tm.textContent=fmtTime(n.createdAt);
        wrap.appendChild(h);wrap.appendChild(txt);wrap.appendChild(tm);
        var del=document.createElement('button');del.className='nx';del.textContent='×';
        del.setAttribute('data-del',String(i));
        del.setAttribute('aria-label','Delete note');
        li.appendChild(wrap);li.appendChild(del);
        dl.appendChild(li);
      });
    }
    $('.note-total').forEach(function(el){el.textContent=String(state.notes.length);});
    if(copyBtn){copyBtn.disabled=(state.notes.length===0);}
  }catch(e){}
}
function addNoteFor(sec,textarea){
  try{
    var text=(textarea.value||'').trim();
    if(!text){return;}
    state.notes.push({
      sectionAnchor:sec.getAttribute('data-anchor'),
      headingVerbatim:sec.getAttribute('data-heading'),
      text:text,
      createdAt:new Date().toISOString()
    });
    state.notesDirty=true;
    textarea.value='';
    saveToLocalStorage();
    renderNotes();
    if(drawer){drawer.hidden=false;}
  }catch(e){}
}
try{
  document.addEventListener('click',function(e){
    var t=e.target;
    if(!t||!t.closest){return;}
    var del=t.closest('button[data-del]');
    if(del){
      var i=parseInt(del.getAttribute('data-del'),10);
      if(!isNaN(i)&&i>=0&&i<state.notes.length){
        state.notes.splice(i,1);
        state.notesDirty=true;
        saveToLocalStorage();
        renderNotes();
      }
      return;
    }
    var addBtn=t.closest('.note-area [data-add]');
    if(addBtn){
      var secA=addBtn.closest('section.card');
      var na=addBtn.closest('.note-area');
      var ta=na?na.querySelector('textarea'):null;
      if(secA&&ta){addNoteFor(secA,ta);}
      return;
    }
    var cancel=t.closest('.note-area [data-cancel]');
    if(cancel){
      var na2=cancel.closest('.note-area');
      if(na2){na2.hidden=true;}
      return;
    }
    var act=t.closest('button[data-act]');
    if(!act){return;}
    var sec=act.closest('section.card');
    if(!sec){return;}
    var kind=act.getAttribute('data-act');
    if(kind==='note'){
      var area=sec.querySelector('.note-area');
      if(area){
        area.hidden=!area.hidden;
        if(!area.hidden){var ta2=area.querySelector('textarea');if(ta2){ta2.focus();}}
      }
    }else if(kind==='src'){
      var sa=sec.querySelector('.src-area');
      if(sa){sa.hidden=!sa.hidden;}
    }else if(kind==='copy-sect'){
      copySectionWithNote(sec).then(function(ok){
        if(ok){
          act.setAttribute('data-copied','1');
          act.textContent='Copied';
          setTimeout(function(){
            act.removeAttribute('data-copied');
            act.textContent='Copy section';
          },1800);
        }
      });
    }
  });
}catch(e){}
try{
  document.addEventListener('keydown',function(e){
    if((e.metaKey||e.ctrlKey)&&e.key==='Enter'){
      var ta=e.target;
      if(ta&&ta.tagName==='TEXTAREA'&&ta.closest&&ta.closest('.note-area')){
        var sec=ta.closest('section.card');
        if(sec){addNoteFor(sec,ta);}
      }
    }
  });
}catch(e){}

/* ---- copy notes (render-shell.md clipboard write with fallback) ---- */
function flashCopy(msg){
  if(!copyBtn){return;}
  var old='Copy notes';
  copyBtn.textContent=msg;
  setTimeout(function(){copyBtn.textContent=old;},2200);
}
function revealTextareaFallback(payload){
  try{
    if(drawer){drawer.hidden=false;}
    var ta=document.getElementById('clipboard-fallback');
    if(!ta){
      var p=document.createElement('p');
      p.className='nd-hint';
      p.textContent='Clipboard write blocked. Copy the payload below manually.';
      ta=document.createElement('textarea');
      ta.id='clipboard-fallback';
      ta.rows=10;
      ta.style.width='100%';
      ta.style.font='inherit';
      var host=drawer||document.body;
      host.insertBefore(ta,host.firstChild);
      host.insertBefore(p,ta);
    }
    ta.value=payload;
    ta.focus();
    ta.select();
  }catch(e){}
}
function copyNotes(){
  if(state.notes.length===0){flashCopy('No notes to copy');return;}
  var payload=buildPayload(state.notes,state.artifactPath,state.artifactOwner);
  try{
    navigator.clipboard.writeText(payload).then(
      function(){state.notesDirty=false;flashCopy('Copied · '+state.notes.length+' notes');},
      function(){revealTextareaFallback(payload);}
    );
  }catch(e){revealTextareaFallback(payload);}
}
if(copyBtn){copyBtn.addEventListener('click',copyNotes);}

/* ---- restore from LocalStorage (render-shell.md) ---- */
try{
  var test='andthen:visualize:ls-test';
  localStorage.setItem(test,'1');
  localStorage.removeItem(test);
  try{
    var own=JSON.parse(localStorage.getItem(lsKey())||'null');
    if(own&&own.notes&&own.notes.length){state.notes=own.notes;}
  }catch(e1){}
  var prefix='andthen:visualize:'+state.artifactSha1+':';
  var found=null;
  for(var i=0;i<localStorage.length;i++){
    var k=localStorage.key(i);
    if(k&&k.indexOf(prefix)===0&&k!==lsKey()){
      try{
        var data=JSON.parse(localStorage.getItem(k)||'null');
        if(data&&data.notes&&data.notes.length){found=data;break;}
      }catch(e2){}
    }
  }
  if(found&&window.confirm('Restore previous notes for this artifact from another session?')){
    state.notes=state.notes.concat(found.notes);
    state.notesDirty=true;
    saveToLocalStorage();
  }
}catch(e){
  try{
    var warn=document.createElement('div');
    warn.textContent='Note persistence disabled (private browsing?). Notes won’t survive refresh.';
    warn.style.cssText='background:rgba(176,126,43,.12);color:#B07E2B;padding:0.4rem 1.2rem;font-size:0.8rem;';
    document.body.insertBefore(warn,document.body.firstChild);
  }catch(e3){}
}
renderNotes();

/* ---- beforeunload (render-shell.md, verbatim) ---- */
window.addEventListener('beforeunload', function (e) {
  if (state.notes.length > 0 && state.notesDirty) {
    e.preventDefault();
    e.returnValue = '';
  }
});
})();
