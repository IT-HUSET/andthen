# Review Report Template

Use when the source is a **review report** produced by the `andthen:review` skill (any lens – code / doc / gap / security / mixed / council) or by the `andthen:architecture` skill in `--mode review`. Detection: H1 contains "Review" (case-insensitive, as a standalone word); AND H2 set contains "Executive Summary"; AND H2 set contains at least one of "Findings", "Verdict", "Readiness Assessment", "Metrics Dashboard".

Review reports are *evidence + verdict*. The visualization optimizes for triage – severity at a glance, jump to a finding, confirm the verdict – not narrative reading. Findings are the load-bearing surface.


## Layout

```
+-------------------------------------------------------------+
| andthen:visualize · Review · <basename>            [ Copy ] |
+-------------------------------------------------------------+
| eyebrow + serif H1 + status pill row                        |
| [ KPI band: Critical · High · Medium · Low ]                |
| [ Where-to-focus band (CRITICAL/HIGH first, then verdict) ] |
+-------------------------------------------------------------+
| ## Executive Summary  (or  ## Summary)                      |
| [ Verdict block + summary prose ]              [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Verdict  (gap mode)  /  ## Readiness Assessment          |
| [ Verdict table (dimension/score/threshold/status) ]        |
|                                                [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Findings  (or  ## Findings Filter / ## <Category> )      |
| [ Risk-map chips above + Finding cards below ][ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Metrics Dashboard  (architecture review only)            |
| [ Per-package metrics table ]                  [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Dependency Graph  (architecture review only)             |
| [ Generic prose – DAG description ]            [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Proposed Fitness Functions  (architecture review only)   |
| [ Per-level cards – see fitness.md ]           [ Note ] [ <> ]|
+-------------------------------------------------------------+
| ## Recommendations  /  ## Critic Coverage  /  ## Next Steps |
| [ Generic prose ]                              [ Note ] [ <> ]|
+-------------------------------------------------------------+
```


## Document Header

Review reports typically carry inline metadata in the Executive Summary's first few prose lines or as bold-key pairs:

| Source key | Header consumption |
|---|---|
| `Review target:` / `Review mode used:` lines | Extra `.meta-pill` with `k="target"` (basename only) and `k="mode"` |
| Filename suffix `-{lens}-review-{agent}-YYYY-MM-DD` | If present, surface `lens` (`code` / `doc` / `gap` / `security` / `mixed` / `council` / `architecture`) as the eyebrow subtype; surface `agent` (`claude` / `codex` / etc.) and the date as meta pills |

Filename parsing is advisory only – content always overrides. When the report body explicitly names a different `Review mode used:`, prefer that.

**Status pill** (derived – maps the verdict/readiness to the SKILL.md status kebab):

| Source verdict / readiness | Status class |
|---|---|
| `PASS` (gap) / `Ready` (any lens) | `status-approved` (olive) |
| `Needs Minor Updates` (doc) | `status-draft` (warn amber) |
| `Needs Fixes` (code/security) | `status-review` (clay coral) |
| `Needs Significant Rework` (doc) | `status-review` (clay coral) |
| `FAIL` (gap) / `Blocked` (code/security) / `Not Ready` (doc) | `status-deprecated` (rust) |
| anything else / unparseable | plain `.meta-pill` (no `.filled`) |

Mixed-mode reports use the **worst** readiness per the SKILL.md verdict ladder.


## KPI Cells

The four-cell `.kpi-band` sits between `.doc-header` and the first section. Review-report cells in source order:

| Cell | Label | Source |
|---|---|---|
| 1 | Critical | Count of findings with severity `CRITICAL` (case-insensitive). Parse from finding headers (e.g. `### Finding 1 - HIGH - …`, `### ARCH-001: …` with `**Severity**: CRITICAL`, or council-mode structured-finding `severity:` fields). |
| 2 | High | Count of findings with severity `HIGH` |
| 3 | Medium | Count of findings with severity `MEDIUM` |
| 4 | Low | Count of findings with severity `LOW` (INFO findings are reported in the Findings section but **not** counted in the KPI – they are diagnostic, not actionable) |

Auto-`.attention`: cell 1 when count > 0; cell 2 when count > 0.


## Section Renderers

Each H2 dispatches to **one** renderer; Generic Prose is the fallback. Section Block wrapper (id + data-anchor + static affordances) is universal.

### Executive Summary → Verdict block + summary prose

Always renders. If the section body contains a `## Verdict` table (gap mode's canonical PASS/FAIL block) or `**Overall readiness:**` / `**Overall: PASS|FAIL**` line, surface it as the section's `.tldr-light` callout (SKILL.md contract). The remaining prose renders below.

```html
<div class="tldr-light review-tldr-{{verdict-kebab}}">
  <span class="k">Verdict</span>
  <span class="v">{{Overall: PASS / Overall: Ready / etc.}}</span>
</div>
```

```css
.review-tldr-pass, .review-tldr-ready { border-left-color: var(--ok); }
.review-tldr-pass .k, .review-tldr-ready .k { color: var(--ok); }
.review-tldr-fail, .review-tldr-blocked, .review-tldr-not-ready { border-left-color: var(--danger); }
.review-tldr-fail .k, .review-tldr-blocked .k, .review-tldr-not-ready .k { color: var(--danger); }
.review-tldr-needs-fixes, .review-tldr-needs-significant-rework { border-left-color: var(--accent); }
.review-tldr-needs-fixes .k, .review-tldr-needs-significant-rework .k { color: var(--accent); }
.review-tldr-needs-minor-updates { border-left-color: var(--warn); }
.review-tldr-needs-minor-updates .k { color: var(--warn); }
```

When the canonical PASS/FAIL gap block is present, render the full dimensions table verbatim inside the section body below the TL;DR callout. Use the verdict-table CSS below.

### Verdict / Readiness Assessment → Verdict table

The canonical gap-mode block has dimensions/score/threshold/status columns:

```html
<table class="review-verdict-table">
  <thead><tr><th>Dimension</th><th>Score</th><th>Threshold</th><th>Status</th></tr></thead>
  <tbody>
    <tr class="dim-pass"><td>Functionality</td><td><code>9/10</code></td><td><code>&gt;= 7</code></td><td><span class="dim-status pass">PASS</span></td></tr>
    <tr class="dim-fail"><td>Completeness</td><td><code>6/10</code></td><td><code>&gt;= 9</code></td><td><span class="dim-status fail">FAIL</span></td></tr>
  </tbody>
  <tfoot><tr><td colspan="4"><strong>Overall: FAIL</strong></td></tr></tfoot>
</table>
```

```css
.review-verdict-table { width: 100%; border-collapse: collapse;
                        background: var(--panel); border: 1px solid var(--border-soft);
                        border-radius: var(--radius-sm); overflow: hidden; }
.review-verdict-table th { background: var(--panel-2); text-align: left;
                           padding: 0.5rem 0.7rem; font-family: var(--mono);
                           font-size: 0.74rem; color: var(--text-muted);
                           border-bottom: 1px solid var(--border); }
.review-verdict-table td { padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--border-soft); }
.review-verdict-table tfoot td { background: var(--panel-2); font-family: var(--mono); }
.dim-pass { background: rgba(107, 128, 73, 0.04); }
.dim-fail { background: rgba(181, 72, 43, 0.06); }
.dim-status { font-family: var(--mono); font-size: 0.74rem; font-weight: 700;
              padding: 0.1rem 0.5rem; border-radius: var(--radius-sm); }
.dim-status.pass { background: var(--ok); color: #FAF9F5; }
.dim-status.fail { background: var(--danger); color: #FAF9F5; }
```

For non-gap modes, the readiness label (`Ready` / `Needs Fixes` / etc.) renders as a single labeled chip, sized like the TL;DR callout.

### Findings → Risk-map chips + Finding cards

The headline section. Two source shapes are common:

1. **`### Finding N - SEVERITY - Title`** with structured-finding fields as paragraphs (Reviewer / Severity / Confidence / Location / Scope relation / Finding / Threatened assumption / Evidence / Impact / Suggested fix / Verification needed).
2. **`### ARCH-NNN: Title`** with bold-key inline metadata (`**Severity**:` / `**Dimension**:` / `**C4 Level**:` / `**Evidence**:` / `**Impact**:` / `**Recommendation**:` / `**Fitness Function**:` / `**Fix Prompt**:`).

Both render to the same card shape; the parser dispatches by H3 header pattern (`/^Finding \d+ - /i` for review-skill shape vs `/^[A-Z]{3,5}-\d+:/` for architecture shape – e.g. `ARCH-001:`, `DEP-12:`). Council-mode reports may nest findings under per-lens or per-reviewer H3s – treat each leaf finding as a card regardless of nesting depth.

**Above the H3 card list**, emit a `<nav class="risk-map">` summary row (SKILL.md *Risk-map chips* contract) – one chip per finding, color-coded by severity:

| Severity | Chip class |
|---|---|
| CRITICAL | `.attention` (clay coral) |
| HIGH | `.attention` (clay coral) |
| MEDIUM | `.medium` (warn amber) |
| LOW | `.safe` (olive) |
| INFO | `.neutral` (gray) |

Each chip's `href` points at the finding's sub-anchor (`#findings-finding-1`, `#findings-arch-001`); click pulses via the delegated `pulseAnchor` handler.

```html
<article class="review-finding" id="findings-finding-1" data-anchor-parent="findings" data-severity="high">
  <header class="rf-head">
    <span class="rf-id">F1</span>
    <span class="rf-severity sev-high">HIGH</span>
    <h3 class="rf-title">Acceptance Scenarios has incompatible canonical shapes</h3>
    <span class="rf-confidence">conf 100</span>
  </header>
  <div class="rf-meta">
    <span><span class="k">reviewer</span> Doc lens + Critic</span>
    <span><span class="k">location</span> <code>docs/specs/fis-format-v2/fis-format-v2.md:20</code></span>
    <span><span class="k">scope</span> primary</span>
  </div>
  <dl class="rf-fields">
    <dt>Finding</dt><dd>…</dd>
    <dt>Threatened assumption</dt><dd>…</dd>
    <dt>Evidence</dt><dd>…</dd>
    <dt>Impact</dt><dd>…</dd>
    <dt>Suggested fix</dt><dd>…</dd>
    <dt>Verification needed</dt><dd>…</dd>
  </dl>
</article>
```

```css
.review-findings-list { display: flex; flex-direction: column; gap: 0.65rem; }
.review-finding { background: var(--panel); border: 1px solid var(--border-soft);
                  border-radius: var(--radius-sm); padding: 0.75rem 0.95rem; }
.review-finding[data-severity="critical"] { border-left: 3px solid var(--danger); }
.review-finding[data-severity="high"]     { border-left: 3px solid var(--accent); }
.review-finding[data-severity="medium"]   { border-left: 3px solid var(--warn); }
.review-finding[data-severity="low"]      { border-left: 3px solid var(--ok); }
.review-finding[data-severity="info"]     { border-left: 3px solid var(--text-faint); }
.rf-head { display: flex; align-items: baseline; gap: 0.55rem; flex-wrap: wrap;
           margin-bottom: 0.45rem; }
.rf-id { font-family: var(--mono); font-size: 0.74rem; font-weight: 700;
         background: var(--panel-3); color: var(--text-muted);
         padding: 0.1rem 0.45rem; border-radius: var(--radius-sm); }
.rf-severity { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
               padding: 0.1rem 0.5rem; border-radius: 999px; color: #FAF9F5; }
.rf-severity.sev-critical { background: var(--danger); }
.rf-severity.sev-high     { background: var(--accent); }
.rf-severity.sev-medium   { background: var(--warn); }
.rf-severity.sev-low      { background: var(--ok); }
.rf-severity.sev-info     { background: var(--text-faint); color: var(--text); }
.rf-title { flex: 1; margin: 0; font-family: var(--serif); font-size: 1.05rem;
            font-weight: 600; color: var(--text); min-width: 0; }
.rf-confidence { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted); }
.rf-meta { display: flex; flex-wrap: wrap; gap: 0.85rem; margin-bottom: 0.55rem;
           font-size: 0.85rem; color: var(--text-muted); }
.rf-meta .k { font-family: var(--mono); font-size: 0.72rem;
              color: var(--text-faint); margin-right: 0.3rem;
              text-transform: uppercase; letter-spacing: 0.05em; }
.rf-meta code { color: var(--accent); }
.rf-fields { margin: 0; }
.rf-fields dt { font-family: var(--mono); font-size: 0.72rem; color: var(--text-muted);
                text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.55rem; }
.rf-fields dd { margin: 0.2rem 0 0; color: var(--text); font-size: 0.92rem; line-height: 1.55; }
```

**Field parsing rules:**

- `Severity:` / `**Severity**:` → drives card color, severity chip, KPI counts. Fallback `INFO` when absent.
- `Confidence:` → integer/percent shown as `conf NN` chip. Omit when absent.
- `Location:` / `**Evidence**:` → render `path:line` patterns as `<code>` and add `<a>` anchors when the path looks like a relative repo path (no `http://`). The link works from `file://` (it's a target the user can copy, not a fetched URL).
- Bold-key inline fields (`**Severity**: HIGH`) parse the same way as paragraph-form fields (`Severity: HIGH`). Both shapes coexist in the wild.
- **Connascence** / **Dimension** / **C4 Level** / **Category** (architecture findings only) – render as additional chips in `.rf-meta`. Use mono font, neutral pill style.
- **Fix Prompt** (architecture) – render the body inside `<pre class="rf-fix-prompt">` because it's copy-pasteable instruction text.

When a finding has secondary analysis blocks (an H4 `Detailed analysis`, `Notes`, `Background`, or a `<!-- analysis -->` marker), wrap them in `<details class="analysis">` per the SKILL.md *Supporting-detail collapse* contract.

**Mixed-mode / council reports** group findings by sub-lens or reviewer. Render the grouping H3 as a section divider inside the `## Findings` body; nest each lens's findings as cards under the divider but keep one risk-map chip row at the top of the H2 covering *all* findings.

### Metrics Dashboard → Per-package metrics table (architecture review only)

Render the source's `| Package | Ca | Ce | I | A | D | Zone | Notes |` table as a styled table. Highlight Zone of Pain rows (`D > 0.7`) with rust accent, Zone of Uselessness rows (`D > 0.7` and `A > 0.7`) with warn accent.

```css
.review-metrics { width: 100%; border-collapse: collapse; }
.review-metrics th { background: var(--panel-2); text-align: left;
                     padding: 0.5rem 0.7rem; font-family: var(--mono);
                     font-size: 0.74rem; color: var(--text-muted);
                     border-bottom: 1px solid var(--border); }
.review-metrics td { padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--border-soft); }
.review-metrics td.metric { font-family: var(--mono); text-align: right; }
.review-metrics tr.zone-pain td.metric { color: var(--danger); }
.review-metrics tr.zone-uselessness td.metric { color: var(--warn); }
.review-metrics td.zone { font-family: var(--mono); font-size: 0.74rem;
                          color: var(--text-muted); }
```

Graph-level metrics (`CCD`, `ACD`, `NCCD`) when present render as a small label/value strip above the table.

### Dependency Graph → Generic Prose

The source is typically a bullet-list description of the condensed DAG (SCCs collapsed). Render as Generic Prose with H3 sub-anchors. No diagram primitive applies here – the graph is described textually in the source.

### Proposed Fitness Functions → Per-level cards

Architecture review reports often include this section. Reuse the **fitness.md** template's `.fitness-card` renderer (load that template's CSS when this section is present). Each fitness-function proposal renders as a card grouped by governance level (1-4).

### Critic Coverage / Stakeholder Alignment / Over-Engineering Analysis → Generic Prose

Short summary sections from council/critic reviews. Render as Generic Prose with a muted leading "lens" label.

### Recommendations / Next Steps / Recommended Next Action → Recommendation accent box

Reuse `tradeoff.md` `.recommendation` styling. When the source has H3 sub-headings (`High:` / `Medium:` / `Low:` priority groupings), render each group as a sub-section inside the accent box with severity-colored bullets.

```css
.review-recs h3 { color: var(--text); font-size: 0.95rem; margin: 0.6rem 0 0.4rem;
                  font-family: var(--mono); text-transform: uppercase;
                  font-size: 0.78rem; letter-spacing: 0.05em; }
.review-recs h3.r-high { color: var(--accent); }
.review-recs h3.r-medium { color: var(--warn); }
.review-recs h3.r-low { color: var(--ok); }
```


## Where-to-Focus Inputs

Per SKILL.md *Where-to-Focus Priority Section* heuristic, in source-relevance order:

1. **Every CRITICAL finding** (cap 2 in this slot) → "CRITICAL: <title>" with anchor link to the finding card.
2. **Every HIGH finding** (cap 3 in this slot) → "HIGH: <title>" with anchor link.
3. **Failed verdict dimensions** (gap mode) → "FAIL · <Dimension>: <score>/<threshold>" with anchor to `#verdict`.
4. **A non-empty `## Critic Coverage` block** stating no attacks landed → "Critic ran but found no surviving issues – consider whether scope was too narrow" with anchor to that section.

The band omits itself when fewer than 2 items would render (per SKILL.md *Omission rule*).


## Pre-population and Source Consumption

1. Parse the canonical PASS/FAIL gap block once, *before* dispatching the first H2. The Executive Summary, Verdict section, and status pill all consume it; flag overlap is intentional (per the SKILL.md section-deduplication rule, the canonical block is rendered once as the section's body; the TL;DR callout is a *summary* of that block, not a duplicate of its rows).
2. Parse finding severities once during a single sweep over H3 headers + first 3 lines of each finding body. Cache as `{anchor, severity}` so the risk-map chips above the H2 know the chip class without re-parsing.
3. Detect lens and mode from the filename suffix when content metadata is missing (e.g. older reports). Filename is advisory.
4. **Architecture vs. review-skill report disambiguation**: both share `## Findings` + `## Executive Summary`. The presence of `## Metrics Dashboard` OR `## Dependency Graph` OR architecture-shaped finding IDs (`/^ARCH-\d+:/`, `/^DEP-\d+:/`) flips the dispatch to include the architecture-only sections (Metrics Dashboard, Dependency Graph, Proposed Fitness Functions). Without those markers, the architecture sections are simply absent and the renderer skips them.


## Edge Cases

- **No findings at all** (a Ready / PASS report) → KPI cells all 0; risk-map row omits; render the H2 body with a muted "No findings – verdict: <readiness>" callout.
- **INFO findings only** (architecture review with all-borderline metrics) → KPI cells all 0 (INFO is intentionally not counted); render the findings list as muted cards with `data-severity="info"`.
- **Council mode with per-reviewer subsections** → group findings by reviewer under H3 dividers; the top-level risk-map row aggregates across all reviewers.
- **Findings Filter applied** (council reports) → if the source body explicitly says "X findings filtered (low confidence / out of scope)", render that callout above the Findings list as a muted note; do not synthesize the filtered findings.
- **Severity in mixed forms** (`CRITICAL` / `Critical` / `critical`) → case-insensitive matching, but render the chip in uppercase for consistency.
- **Report mixing gap PASS/FAIL with code/security readiness** (mixed mode) → render each sub-mode's verdict in its own row inside the verdict table; the status pill uses the worst-readiness rung per the SKILL.md verdict ladder.
- **Per-file linked locations** (`Location: src/foo.ts:42`) → render the path as `<code>` and the line number as muted `:42`; do not synthesize a clickable href to the local file (anchor would not resolve from `file://`).


## Example Use Cases

- **PR reviewer** – open the review report, glance at the verdict pill, jump to CRITICAL/HIGH findings via the risk-map chips, copy notes per section.
- **Remediation flow** – the visualizer is read-only; after reviewing visually, paste the copied notes into the `andthen:remediate-findings` skill alongside the original report path.
- **Council follow-up** – inspect Critic Coverage to confirm assumptions, unhappy paths, and hidden coupling were actually attacked (per `lens-adversarial.md`).
