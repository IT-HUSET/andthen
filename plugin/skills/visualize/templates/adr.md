# ADR Template

Architecture Decision Record. Detection per SKILL.md: H1 `/^ADR[-\s]?\d/` or H2 set containing `Decision` + (`Consequences` | `Alternatives Considered`). Renderers reuse `templates/tradeoff.md` (`.option` cards, `.recommendation` accent box) — see that file for the shared CSS. This template documents only ADR-specific deltas: inline-metadata parsing, status semantics, KPI cells, and the `## Consequences` three-bucket layout.


## Inline metadata (prologue only)

ADRs declare metadata as bold-key inline pairs in the **prologue** – the source span between the H1 line and the first `## ` heading. The parser consumes `**Status:**` / `**Date:**` / `**Deciders:**` / `**Related:**` lines **only when they appear in that prologue span**. Later occurrences (e.g. a `**Status:** Now stable` aside inside `## Consequences`) render verbatim as prose – they are not consumed into the header. This bound is part of the parse rule, not just prose: a global pattern match would silently drop in-section text.

```markdown
**Status:** Proposed
**Date:** 2026-03-09
**Deciders:** DartClaw team
**Related:** [ADR-012](...), [Research note](...)
```

The emitter consumes these lines into `.doc-header` (SKILL.md *Document header* contract) and marks the source span as consumed so Generic Prose fallback skips them.

- `**Status:**` → drives the status pill class via the kebab table below; also feeds KPI Cell 1.
- `**Date:**` → `updated` meta-pill value.
- `**Deciders:**` → extra `.meta-pill` with `k="deciders"`.
- `**Related:**` → preserved as anchor-bearing markdown inside `.doc-meta-related` (clickable links, not flattened); comma-separated entry count feeds KPI Cell 4.

**Status kebab mapping** (reuses pill classes defined in SKILL.md *Document header*, including `status-deprecated`):

| Status value | CSS class | Color |
|---|---|---|
| Proposed | `status-draft` | warn (amber) |
| Accepted / Approved | `status-approved` | ok (olive) – same as `status-done` |
| Superseded | `status-deferred` | text-faint (gray) |
| Deprecated / Rejected | `status-deprecated` | danger (red) |
| anything else | unmatched → plain `.meta-pill` (no `.filled`) | neutral |

All five classes ship in SKILL.md's base style block – no conditional CSS injection needed when emitting an ADR.


## KPI cells

| Cell | Label | Source |
|---|---|---|
| 1 | Status | Verbatim `**Status:**` value (truncated to 16 chars) |
| 2 | Alternatives | Count of H3 under `## Alternatives Considered` |
| 3 | Consequences | Count of bullets / H3 under `## Consequences` |
| 4 | Related | Count of comma-separated entries in `**Related:**` |

Auto-`.attention`: cell 1 when Status matches `/^(deprecated|rejected|superseded)/i`.


## Section dispatch

| Heading (substring) | Renderer |
|---|---|
| Context | Generic Prose (H3 subsections like "Prior Art" get standard `.l2` sub-anchors) |
| Decision | Reuse `tradeoff.md` `.recommendation` accent box. Code blocks render verbatim inside `<pre><code>` |
| Alternatives Considered | Reuse `tradeoff.md` `.option` card layout, **no radar** (ADRs lack scoring matrices). Emit each alternative as `<section class="option adr-alt" data-anchor-parent="alternatives-considered">`; the extra `.adr-alt` class triggers `.option.adr-alt .option-body { grid-template-columns: 1fr; }` so the absent radar doesn't leave an empty 320 px column. One H3 per alternative |
| Consequences | **Three-bucket layout** when H3s match `/^(positive|negative|neutral|trade.?offs?)/i`; else Generic Prose with semantically colored H3 |
| (anything else) | Generic Prose |

`<details class="analysis">` collapse, Light TL;DR callout, and the per-section affordances apply unchanged per their SKILL.md contracts.


## `## Consequences` three-bucket layout

```html
<div class="adr-consequences">
  <div class="adr-cons-bucket positive"><h3>Positive</h3><ul>…</ul></div>
  <div class="adr-cons-bucket negative"><h3>Negative</h3><ul>…</ul></div>
  <div class="adr-cons-bucket neutral"><h3>Neutral</h3><ul>…</ul></div>
</div>
```

```css
.adr-consequences { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.adr-cons-bucket { background: var(--panel); border-radius: var(--radius-sm); padding: 0.9rem 1rem;
                   border-top: 3px solid var(--border); }
.adr-cons-bucket.positive { border-top-color: var(--ok); }
.adr-cons-bucket.negative { border-top-color: var(--danger); }
.adr-cons-bucket.neutral  { border-top-color: var(--text-muted); }
.adr-cons-bucket h3 { margin-top: 0; font-size: 0.85rem; font-family: var(--mono);
                      text-transform: uppercase; letter-spacing: 0.06em; }
.adr-cons-bucket.positive h3 { color: var(--ok); }
.adr-cons-bucket.negative h3 { color: var(--danger); }
.adr-cons-bucket.neutral  h3 { color: var(--text-muted); }
@media (max-width: 760px) { .adr-consequences { grid-template-columns: 1fr; } }
```

When the bucket regex doesn't match (e.g. consequences as one flat list, or unfamiliar grouping), render Generic Prose with the same semantic colors applied to H3 headings via inline class on heading-text match.


## Edge cases

- **Missing `**Status:**`** → no status pill; KPI Cell 1 shows "—".
- **Status with no kebab match** → fuzzy fallback: contains "review"/"draft" → `status-draft`; "accept"/"approve" → `status-done`; else plain `.meta-pill` (no `.filled`).
- **No `## Alternatives Considered`** → KPI Cell 2 = 0; renderer doesn't fire.
- **No `## Consequences`** → KPI Cell 3 = 0; renderer doesn't fire.
- **Superseded ADR with successor link in `**Related:**`** → link renders inline as usual; no extra "superseded by" callout (status pill carries the signal).
- **Per-alternative Note buttons stay omitted** per SKILL.md anchor scheme (one Note per H2) — same contract as trade-off Options.
