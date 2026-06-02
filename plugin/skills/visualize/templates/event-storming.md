# Event Storming Template

Use when the source is an architecture **event-storming** report from the `andthen:architecture` skill in `--mode event-storming`. Detection: H1 or H2 contains "Event Storming" / "Event-Storming" (case-insensitive); OR H2 set contains BOTH "Event Timeline" AND ("Hotspots" OR "Commands and Actors").

Event-storming reports surface a Brandolini-style sticky-note board as a textual artifact. The visualization makes the **sticky-note color vocabulary load-bearing** – orange events, blue commands, yellow actors, lilac policies, green read models, purple hotspots, plus pink/red external systems on Big Picture boards. The reviewer's eye learns the palette within seconds.


## Contents

- Layout
- Document Header
- Sticky-Note Color Tokens
- KPI Cells
- Section Renderers
- Where-to-Focus Inputs
- Edge Cases
- Example Use Cases


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Event Storming · <basename>    [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + level pill + status pill row           |
| [ KPI band: Events · Hotspots · Pivotal · Candidates ]      |
| [ Where-to-focus band (hotspots + unattributed commands)    |
+-------------------------------------------------------------+
| ## Executive Summary  /  ## How to Read This Report         |
| [ Color-legend strip + prose ]                 [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Event Timeline                                           |
| [ Horizontal timeline with pivotal-event highlights ]       |
|                                                [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Commands and Actors                                      |
| [ Sticky-note grid: command → actor pairs ]    [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Policies and Read Models  (Process Modeling / Design)    |
| [ Two-column grid: policies | read models ]    [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Hotspots                                                 |
| [ Purple hotspot cards (sticky-note styled) ]  [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Subdomain Candidates  /  Workflow Boundaries  /  Aggregates |
| [ Candidate cards anchored on pivotal events ] [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Recommended Next Steps                                   |
| [ Hand-off chips (mode/skill chips) ]          [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## Document Header

The Brandolini level is the report's defining axis. Parse the Executive Summary for "Big Picture" / "Process Modeling" / "Design Level"; surface as the eyebrow and as an extra `.meta-pill` with `k="level"`:

| Level | Eyebrow text |
|---|---|
| Big Picture | `EVENT STORMING · BIG PICTURE` |
| Process Modeling | `EVENT STORMING · PROCESS MODELING` |
| Design Level | `EVENT STORMING · DESIGN LEVEL` |
| unparseable | `EVENT STORMING` |

Status pill stays generic (`review` by default; `draft` when the source explicitly says "draft / WIP"); the level pill carries the discovery-state signal.


## Sticky-Note Color Tokens

These tokens are **sticky-note specific** – they layer on top of the render-shell.md palette without replacing it. Define once in the page-level `<style>` block.

```css
:root {
  /* Sticky-note palette – warm-light theme calibrated for AA contrast. */
  --es-orange:  #E8B16A;   /* events */
  --es-blue:    #6B8FB5;   /* commands */
  --es-yellow:  #E0C66B;   /* actors */
  --es-lilac:   #B59BCB;   /* policies */
  --es-green:   #9DB87A;   /* read models */
  --es-purple:  #8C6BB8;   /* hotspots */
  --es-pink:    #D88AA0;   /* external systems (Big Picture only) */
  /* Card-on-sticky text always reads on the saturated swatch above; muted variants for backgrounds. */
  --es-orange-soft: rgba(232, 177, 106, 0.16);
  --es-blue-soft:   rgba(107, 143, 181, 0.16);
  --es-yellow-soft: rgba(224, 198, 107, 0.16);
  --es-lilac-soft:  rgba(181, 155, 203, 0.16);
  --es-green-soft:  rgba(157, 184, 122, 0.16);
  --es-purple-soft: rgba(140, 107, 184, 0.16);
  --es-pink-soft:   rgba(216, 138, 160, 0.16);
}
.es-sticky {
  background: var(--es-orange-soft); border: 1px solid var(--es-orange);
  border-radius: var(--radius-sm); padding: 0.45rem 0.65rem;
  font-family: var(--ui); font-size: 0.88rem; color: var(--text);
  position: relative;
}
.es-sticky::before {
  content: ''; position: absolute; top: 0; left: 0;
  width: 6px; height: 100%; background: var(--es-orange);
  border-top-left-radius: var(--radius-sm); border-bottom-left-radius: var(--radius-sm);
}
.es-sticky.kind-event    { background: var(--es-orange-soft); border-color: var(--es-orange); }
.es-sticky.kind-event::before    { background: var(--es-orange); }
.es-sticky.kind-command  { background: var(--es-blue-soft); border-color: var(--es-blue); }
.es-sticky.kind-command::before  { background: var(--es-blue); }
.es-sticky.kind-actor    { background: var(--es-yellow-soft); border-color: var(--es-yellow); }
.es-sticky.kind-actor::before    { background: var(--es-yellow); }
.es-sticky.kind-policy   { background: var(--es-lilac-soft); border-color: var(--es-lilac); }
.es-sticky.kind-policy::before   { background: var(--es-lilac); }
.es-sticky.kind-readmodel{ background: var(--es-green-soft); border-color: var(--es-green); }
.es-sticky.kind-readmodel::before{ background: var(--es-green); }
.es-sticky.kind-hotspot  { background: var(--es-purple-soft); border-color: var(--es-purple); }
.es-sticky.kind-hotspot::before  { background: var(--es-purple); }
.es-sticky.kind-external { background: var(--es-pink-soft); border-color: var(--es-pink); }
.es-sticky.kind-external::before { background: var(--es-pink); }
.es-sticky.pivotal { box-shadow: 0 0 0 2px var(--accent); }
```


## KPI Cells

| Cell | Label | Source |
|---|---|---|
| 1 | Events | Count of bullets / list items under `## Event Timeline` |
| 2 | Hotspots | Count of bullets / cards under `## Hotspots` |
| 3 | Pivotal | Count of events explicitly marked pivotal in source (typical markers: `★`, `**pivotal**`, `(pivotal)` substring) |
| 4 | Candidates | Count of cards under the level-appropriate output section (`Subdomain Candidates` / `Workflow Boundaries` / `Aggregate Candidates`) |

Auto-`.attention`: cell 2 when count > 0.


## Section Renderers

### Executive Summary → Color-legend strip + prose

Always include a compact sticky-note legend at the top of this section so the reviewer can orient. Render the legend even when the source's `## How to Read This Report` section is absent (the legend is part of the visualization contract; the source's prose stays separate).

```html
<div class="es-legend">
  <span class="es-legend-item"><span class="es-swatch es-orange"></span> event</span>
  <span class="es-legend-item"><span class="es-swatch es-blue"></span> command</span>
  <span class="es-legend-item"><span class="es-swatch es-yellow"></span> actor</span>
  <span class="es-legend-item"><span class="es-swatch es-lilac"></span> policy</span>
  <span class="es-legend-item"><span class="es-swatch es-green"></span> read model</span>
  <span class="es-legend-item"><span class="es-swatch es-purple"></span> hotspot</span>
  <span class="es-legend-item"><span class="es-swatch es-pink"></span> external</span>
</div>
```

```css
.es-legend { display: flex; flex-wrap: wrap; gap: 0.85rem; margin-bottom: 0.7rem;
             padding: 0.5rem 0.7rem; background: var(--panel-2);
             border-radius: var(--radius-sm); font-size: 0.85rem; color: var(--text-muted); }
.es-legend-item { display: inline-flex; align-items: center; gap: 0.35rem; }
.es-swatch { width: 12px; height: 12px; border-radius: 3px; border: 1px solid var(--border); }
.es-swatch.es-orange   { background: var(--es-orange); }
.es-swatch.es-blue     { background: var(--es-blue); }
.es-swatch.es-yellow   { background: var(--es-yellow); }
.es-swatch.es-lilac    { background: var(--es-lilac); }
.es-swatch.es-green    { background: var(--es-green); }
.es-swatch.es-purple   { background: var(--es-purple); }
.es-swatch.es-pink     { background: var(--es-pink); }
```

For **Big Picture** level, include the `pink` (external) swatch; for **Process Modeling** and **Design Level**, omit it (those levels surface external systems via actors and policies per the mode reference).

### Event Timeline → Horizontal timeline with pivotal-event highlights

The event timeline is the centerpiece. Render as a horizontal scrollable strip of sticky-notes, in source order. Pivotal events get the `.pivotal` accent halo.

```html
<div class="es-timeline">
  <article class="es-sticky kind-event" id="event-timeline-orderplaced" data-anchor-parent="event-timeline">
    <span class="es-event-marker">★</span>
    OrderPlaced
  </article>
  <article class="es-sticky kind-event pivotal" id="event-timeline-paymentdeclined">
    PaymentDeclined
  </article>
  <!-- more event stickies ... -->
</div>
```

```css
.es-timeline { display: flex; flex-wrap: wrap; gap: 0.55rem; padding: 0.6rem 0;
               position: relative; }
.es-timeline > .es-sticky { min-width: 140px; }
.es-event-marker { color: var(--accent); margin-right: 0.3rem; font-weight: 700; }
```

When the source structures events as a numbered list (one event per line), each list item becomes one sticky. When the source uses a table with columns like `| Event | Description | Pivotal? |`, parse the table and emit stickies with the description as tooltip via `<title>`. Mixed shapes (some bullets, some tables) → emit stickies for both, in source order.

### Commands and Actors → Sticky-note grid: command → actor pairs

The source typically pairs commands (blue) with actors (yellow) via tables or prose like `Customer issues PlaceOrder`. Render as a grid where each command sticky points to its actor sticky.

```html
<div class="es-ca-grid">
  <div class="es-ca-pair">
    <article class="es-sticky kind-command">PlaceOrder</article>
    <span class="es-ca-arrow">↑ issued by</span>
    <article class="es-sticky kind-actor">Customer</article>
  </div>
  <!-- more pairs -->
</div>
```

```css
.es-ca-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.7rem; }
.es-ca-pair { display: grid; grid-template-rows: auto auto auto; gap: 0.3rem;
              background: var(--panel); border: 1px solid var(--border-soft);
              border-radius: var(--radius-sm); padding: 0.7rem; }
.es-ca-arrow { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted);
               text-align: center; }
```

**Unattributed commands** (no actor named) – emit the command sticky but render a hotspot-colored "❓ no actor" pseudo-sticky in the actor slot. This visually surfaces the gap the mode reference says to flag.

```css
.es-ca-pair[data-missing-actor="1"] .es-sticky.kind-actor.missing {
  background: var(--es-purple-soft); border-color: var(--es-purple); color: var(--es-purple); font-style: italic;
}
```

### Policies and Read Models → Two-column grid (Process Modeling / Design Level only)

Two columns: lilac policies on the left, green read models on the right. Each card carries its triggering event as a backlink to the timeline.

```html
<div class="es-pr-grid">
  <section class="es-pr-col policies">
    <h3>Policies <span class="es-swatch es-lilac"></span></h3>
    <article class="es-sticky kind-policy">
      Whenever <a href="#event-timeline-paymentdeclined">PaymentDeclined</a>, retry once after 60s
    </article>
  </section>
  <section class="es-pr-col readmodels">
    <h3>Read Models <span class="es-swatch es-green"></span></h3>
    <article class="es-sticky kind-readmodel">CustomerCreditBalance</article>
  </section>
</div>
```

```css
.es-pr-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.es-pr-col h3 { margin: 0 0 0.55rem; font-family: var(--mono); font-size: 0.78rem;
                text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
.es-pr-col > .es-sticky { display: block; margin-bottom: 0.45rem; }
@media (max-width: 720px) { .es-pr-grid { grid-template-columns: 1fr; } }
```

Section is **omitted on Big Picture level** (the mode reference says external systems surface via actors and policies on Process Modeling and Design Level, not Big Picture).

### Hotspots → Purple hotspot cards

Each hotspot is a card – the headline is the question or conflict, the body is the surrounding context. Hotspots are *unresolved* by definition; the visualization emphasizes that with the purple sticky + a "needs answer" muted footer.

```html
<article class="es-sticky kind-hotspot es-hotspot-card" id="hotspots-order-vocab-conflict">
  <h3>"Order" means two different things across Sales and Fulfillment</h3>
  <p>Sales uses "Order" for purchase intent; Fulfillment uses "Order" for shipping commitment. Pivotal events differ.</p>
  <footer><span class="es-hotspot-route">→ surface in <code>andthen:ubiquitous-language</code></span></footer>
</article>
```

```css
.es-hotspot-card { padding: 0.85rem 1rem; }
.es-hotspot-card h3 { margin: 0 0 0.35rem; font-family: var(--serif); font-size: 1rem;
                      font-weight: 600; color: var(--text); }
.es-hotspot-card p { margin: 0; color: var(--text); font-size: 0.9rem; }
.es-hotspot-card footer { margin-top: 0.45rem; font-family: var(--mono); font-size: 0.74rem;
                          color: var(--text-muted); }
.es-hotspot-route code { color: var(--accent); }
```

When the hotspot is **vocabulary-conflict-shaped** (text contains `mean different things`, `vocabulary`, `conflict`, `two definitions`), surface the `andthen:ubiquitous-language` route hint in the footer per the mode reference's Step 7 hand-off catalog.

### Subdomain Candidates / Workflow Boundaries / Aggregate Candidates → Candidate cards

The level-appropriate output section. Render each candidate as a card anchored on its pivotal-event cluster.

```html
<article class="es-candidate" id="subdomain-candidates-order-fulfillment">
  <header class="es-cand-head">
    <h3>Order Fulfillment</h3>
    <span class="es-cand-type">core</span>
  </header>
  <p class="es-cand-rationale">{{one-line rationale}}</p>
  <p class="es-cand-anchors">Anchored on: <a href="#event-timeline-orderpacked">OrderPacked</a>, <a href="#event-timeline-ordershipped">OrderShipped</a></p>
</article>
```

```css
.es-candidates { display: flex; flex-direction: column; gap: 0.55rem; }
.es-candidate { background: var(--panel); border: 1px solid var(--border-soft);
                border-left: 3px solid var(--accent); border-radius: var(--radius-sm);
                padding: 0.7rem 0.9rem; }
.es-cand-head { display: flex; align-items: baseline; gap: 0.55rem; margin-bottom: 0.35rem; }
.es-cand-head h3 { flex: 1; margin: 0; font-family: var(--ui); font-size: 0.98rem; font-weight: 600; }
.es-cand-type { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
                padding: 0.1rem 0.5rem; border-radius: 999px; background: var(--accent); color: #FAF9F5; }
.es-cand-type.t-core       { background: var(--accent); }
.es-cand-type.t-supporting { background: var(--warn); }
.es-cand-type.t-generic    { background: var(--text-faint); color: var(--text); }
.es-cand-rationale { margin: 0 0 0.3rem; color: var(--text-muted); font-size: 0.88rem; }
.es-cand-anchors { margin: 0; font-family: var(--mono); font-size: 0.78rem; color: var(--text-faint); }
.es-cand-anchors a { color: var(--accent); }
```

For **Design Level** aggregate candidates, replace the rationale with the invariants list (one bullet per invariant); same card shape otherwise.

### Recommended Next Steps → Hand-off chips

The mode reference's Step 7 hand-off catalog suggests:
- Big Picture → `andthen:architecture --mode strategic-design`
- Design Level → `andthen:architecture --mode decompose`
- Vocabulary hotspots → `andthen:ubiquitous-language`
- Visual board → `andthen:excalidraw-diagram`

Render each recommended next step as a clickable-looking "mode chip" with a one-line trigger condition.

```html
<nav class="es-handoffs" aria-label="Recommended next steps">
  <a class="es-handoff" href="#">
    <code>andthen:architecture --mode strategic-design</code>
    <span class="es-handoff-trigger">Big Picture subdomain candidates ready</span>
  </a>
</nav>
```

```css
.es-handoffs { display: flex; flex-direction: column; gap: 0.5rem; }
.es-handoff { display: grid; grid-template-columns: minmax(0, auto) 1fr; gap: 0.7rem;
              align-items: baseline; padding: 0.55rem 0.85rem;
              background: var(--panel-2); border-left: 3px solid var(--accent);
              border-radius: var(--radius-sm); text-decoration: none; color: var(--text); }
.es-handoff:hover { background: var(--accent-soft); }
.es-handoff code { color: var(--accent); font-family: var(--mono); font-size: 0.85rem; }
.es-handoff-trigger { color: var(--text-muted); font-size: 0.86rem; }
```

These are visual chips, not action links – clicking does not run the next skill. They orient the reviewer to *what to invoke next*. The `href="#"` reads as no-op; the visual affordance is the message.


## Where-to-Focus Inputs

1. **Hotspots** (any unresolved purple sticky) → "Hotspot: <hotspot title>" anchored at the hotspot card. Cap 3.
2. **Unattributed commands** (commands with `data-missing-actor="1"`) → "Command without actor: <command name>".
3. **Pivotal events without subdomain mapping** – a pivotal event whose label appears in `## Event Timeline` but doesn't appear in any `## Subdomain Candidates` rationale or `Anchored on:` list → "Unmapped pivotal: <event>".
4. **Vocabulary-conflict hotspots** → "UL conflict: <hotspot> – route to `andthen:ubiquitous-language`".


## Edge Cases

- **Big Picture level only** – `## Policies and Read Models` section is omitted; KPI cells still count what's present.
- **No pivotal events explicitly marked** – KPI cell 3 = 0; the timeline renders without halos. Do not infer pivotal status from prose.
- **Hotspots embedded inside other sections** (e.g. a "this is contested" callout under Commands and Actors) – do not auto-extract; only the explicit `## Hotspots` section's bullets count toward KPI cell 2.
- **Mixed-level source** (e.g. the report runs both Big Picture and Design Level) – the level pill shows the *first* level declared in the Executive Summary; both sets of candidates render under their respective H2 sections.
- **External-system stickies on Process Modeling level** – the mode reference says external systems surface via actors/policies there. Render any explicit pink stickies anyway (the source authored them); flag with `<!-- event-storming: external sticky on non-Big-Picture level -->` in `View source` so the gap surfaces.


## Example Use Cases

- **Domain modeler** – run a Big Picture session, visualize, then hand off to `andthen:architecture --mode strategic-design` for subdomain formalization.
- **Tech lead resolving a contested aggregate boundary** – run a Design Level session, visualize, then hand off to `andthen:architecture --mode decompose` to score the boundary.
- **Discovery team** – use the Hotspots Where-to-Focus list to schedule follow-up questions before the next session.
