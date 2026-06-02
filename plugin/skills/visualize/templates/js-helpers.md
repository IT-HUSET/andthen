# IIFE Helper Library

Code-level companion to render-shell.md *JavaScript Authoring Discipline*. Every helper below lives inside the single page-level IIFE alongside `state`, `copyNotes`, `flashInline`, `saveToLocalStorage`, and the `beforeunload` handler. Each is wrapped in `try/catch` so one handler failure cannot disable any other.

The helpers are the *only* sanctioned way to add interactivity to the rendered page – emitters wire static affordances (per the render-shell.md *Section Block* contract) and these helpers attach behavior. Do not invent parallel handlers; compose from what's here.


## Contents

- `pulseAnchor(targetEl)` – chip click + TOC click feedback
- `copySectionWithNote(sectionEl)` – per-section export
- Walkthrough one-at-a-time snippet toggle
- `wireModuleMap(svgEl)` – interactive context-map binding


## `pulseAnchor(targetEl)` – chip click + TOC click feedback

Fires a brief clay box-shadow on the navigated-to element. Bound via delegated click handler so both `.risk-map-chip[href^="#"]` and `.toc a[href^="#"]` trigger the same pulse.

```javascript
function pulseAnchor(targetEl) {
  if (!targetEl) return;
  targetEl.style.transition = 'box-shadow 180ms ease';
  targetEl.style.boxShadow = '0 0 0 3px rgba(193, 95, 60, 0.35)';  // clay – matches --accent rgb
  setTimeout(function () { targetEl.style.boxShadow = 'none'; }, 1400);
}
document.addEventListener('click', function (ev) {
  try {
    var a = ev.target.closest('.risk-map-chip[href^="#"], .toc a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    pulseAnchor(document.getElementById(id));
  } catch (err) { /* swallow per JS Authoring Discipline */ }
});
```


## `copySectionWithNote(sectionEl)` – per-section export

Builds a markdown payload for a single section by **calling `buildSectionBlock`** (defined in render-shell.md *Notes Payload Formatters*) so the per-section shape is byte-identical to one block of the primary `copyNotes()` payload. Reads from `state.notes` (the source of truth) — **not** from the DOM, because the rendered `.note-list li` flattens internal newlines and would silently drop multi-line note text.

```javascript
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
// Bound from the `.btn-copy-sect` click handler in the main IIFE wiring:
//   btn.addEventListener('click', async function () {
//     var sec = btn.closest('section.card'); if (!sec) return;
//     if (await copySectionWithNote(sec)) {
//       btn.setAttribute('data-copied', '1');
//       btn.textContent = 'Copied';
//       setTimeout(function () {
//         btn.removeAttribute('data-copied');
//         btn.textContent = 'Copy section';
//       }, 1800);
//     }
//   });
```

Empty-notes case copies just the `## Section: <heading>` line (no bullets). Payload shape matches the primary `copyNotes()` per-section block exactly so downstream consumers see one consistent format from both copy paths. Feedback: button text flips to `Copied` for 1.8s with the `[data-copied="1"]` style applied (olive).


## Walkthrough one-at-a-time snippet toggle

For walkthrough renderers (numbered step list per `diagrams.md#walkthrough`): when a `<details class="snippet">` inside `.walk` opens, close any other open snippet in the same `.walk` container. Scoped to `.walk details.snippet` – **never** bare `details` – so it cannot interfere with the per-section `View source` panels.

```javascript
try {
  document.querySelectorAll('.walk').forEach(function (walk) {
    walk.addEventListener('toggle', function (e) {
      if (!(e.target instanceof HTMLDetailsElement)) return;
      if (!e.target.matches('details.snippet')) return;
      if (!e.target.open) return;
      walk.querySelectorAll('details.snippet[open]').forEach(function (d) {
        if (d !== e.target) d.open = false;
      });
    }, true);  // capture phase – toggle event does not bubble
  });
} catch (err) { /* swallow */ }
```


## `wireModuleMap(svgEl)` – interactive context-map binding

Each emitted `svg.diagram-module-map` is paired with an `aside.map-detail` containing a `script[type="application/json"][data-role="nodes"]` JSON dictionary (`{nodeKey: {title, meta, body}}`). Clicking an SVG node activates that node and updates the detail panel. Treat title, meta, and body as text, not HTML: artifact-derived detail content must never flow into `innerHTML`.

```javascript
function wireModuleMap(svgEl) {
  try {
    var section = svgEl.closest('section.card');
    if (!section) return;
    var panel = section.querySelector(':scope .map-detail');
    if (!panel) return;
    var dataEl = panel.querySelector('script[type="application/json"][data-role="nodes"]');
    var dataByKey = JSON.parse((dataEl && dataEl.textContent) || '{}');
    function activate(k) {
      try {
        svgEl.querySelectorAll('.node.active').forEach(function (n) { n.classList.remove('active'); });
        var node = null;
        svgEl.querySelectorAll('.node[data-k]').forEach(function (n) {
          if (n.getAttribute('data-k') === k) node = n;
        });
        if (node) node.classList.add('active');
        var d = dataByKey[k];
        if (!d) return;
        var t = panel.querySelector('[data-role="title"]'); if (t) t.textContent = d.title || k;
        var m = panel.querySelector('[data-role="meta"]');  if (m) m.textContent  = d.meta  || '';
        var b = panel.querySelector('[data-role="body"]');  if (b) b.textContent  = d.body  || '';
      } catch (err) { /* swallow */ }
    }
    svgEl.querySelectorAll('.node[data-k]').forEach(function (n) {
      n.addEventListener('click', function () { activate(n.getAttribute('data-k')); });
    });
    var defaultK = panel.getAttribute('data-default-node');
    if (defaultK) activate(defaultK);
  } catch (err) { /* swallow */ }
}
document.querySelectorAll('svg.diagram-module-map').forEach(wireModuleMap);
```

**JSON script discipline:** the detail dictionary is emitted via `JSON.stringify` inside the inert application/json script block. Escape `<` as `\u003c` in that JSON text so a value containing `</script>` cannot terminate the block. Multi-line body text remains JSON `\n` data. **Name-mismatch handling:** a node whose `data-k` has no entry in `dataByKey` simply early-returns; the panel keeps the previous selection. The renderer emits `<!-- module-map: no detail for node "X" -->` for each unpaired node so the gap surfaces in `View source`. **Security:** if richer formatting is needed later, add a strict sanitizer first; until then, title, meta, and body text are assigned with `textContent`, and body line breaks are preserved with CSS.
