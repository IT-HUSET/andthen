---
description: Use when reviewing a PRD, requirements-clarification, architecture trade-off report, or architecture strategic-design report visually. Renders a self-contained HTML view in the user's browser, captures section-anchored notes, and exports them as a markdown payload via clipboard. Trigger on 'review visually', 'visualize this prd', 'visualize this clarification', 'visualize trade-off', 'visualize strategic-design', 'andthen visualize'.
argument-hint: "<path-to-artifact-markdown>"
user-invocable: true
---

# Visualize Workflow Artifact

A self-contained HTML view of an AndThen artifact (PRD, `requirements-clarification.md`, architecture trade-off report, or architecture strategic-design report) opened in the user's browser, with section-anchored notes that export as a markdown payload downstream skills consume as conversational input.

Open-loop by design: emit HTML, open browser, exit. The skill does not block waiting for user interaction.


## When to Use

- Reviewing a PRD before handing to the `andthen:plan` skill
- Reviewing `requirements-clarification.md` before the `andthen:prd` skill
- Reviewing trade-off analysis before ADR formalization
- Reviewing a strategic-design report before refining or chaining into `--mode fitness` / `--mode decompose`
- Verifying an existing artifact retrospectively


## How to Use

1. Read the artifact at `$1`.
2. Detect the artifact type by content (filename advisory only).
3. Load the matching template from `templates/`:
   - `templates/prd.md` for PRDs
   - `templates/clarification.md` for `requirements-clarification.md`
   - `templates/tradeoff.md` for architecture trade-off reports
   - `templates/diagrams.md` for inline-SVG diagram patterns referenced by the templates above
   - **No specialized template** for `strategic-design` — fall back to **generic-prose rendering** (the same fallback `templates/prd.md` describes for unmatched H2 sections): emit one `<section data-anchor=...>` per H2, with the section body rendered as styled markdown. The Note affordance and View-source toggle apply per section, identical to template-driven types. Specialized renderers (e.g. context-map visual, subdomain-tree card grid) are deferred until visual polish is requested.
4. Generate a single self-contained HTML file at `.agent_temp/visualize/<slug>-<timestamp>.html`. Resolve the path against the repo root (`git rev-parse --show-toplevel`) when inside a git working tree, falling back to CWD when there is no repo. This matches the `.agent_temp/` convention other AndThen skills use, so artifacts land predictably regardless of which subdirectory the user invoked from. `<slug>` is the basename without extension; `<timestamp>` is `YYYYMMDD-HHMMSS`.
5. Open the file in the user's browser via the OS-detected command (see Browser-Open Detection below).
6. Print the output path and exit. Do not block on user interaction.


## Artifact Type Detection

Run heuristics in order; first match wins. **Filename hints are advisory only — content decides.**

| Type | Markers |
|---|---|
| `prd` | H1 contains "PRD" or "Product Requirements"; H2 contains both "Executive Summary" and "Functional Requirements" |
| `clarification` | H1 starts with "Requirements Clarification"; H2 contains "Decisions Log" |
| `strategic-design` | H1 contains "Strategic Design" / "Strategic-Design"; OR H2 set contains both "Subdomains" and "Context Map" (case-insensitive). Routes to generic-prose rendering — no specialized template. *Ordered before `tradeoff` because both report shapes share `Executive Summary` + `How to Read This Report`; the more-specific marker pair wins under first-match-wins.* |
| `tradeoff` | H1 or H2 contains "Trade-off" / "Trade off" / "Decision Analysis"; presence of a scoring matrix table (rows = options, columns = criteria) |

If no match, exit with the message *"andthen:visualize: cannot detect artifact type. Supported: PRD (`prd.md`), `requirements-clarification.md`, architecture strategic-design reports, architecture trade-off reports."* and write no HTML.


## Core Requirements (every render)

- **Single self-contained HTML file.** All CSS, JS, and SVG inlined. No external scripts, fonts, stylesheets, icons. Must work from `file://` with no network access.
- **Dark theme.** System font for UI, monospace for code/values. Use the theme tokens below.
- **Read-only render + section-anchored notes.** No structured editing. Per-section "Note" affordance + "View source" toggle revealing the raw markdown for that section. Diagrams do not get their own Note affordance — the parent section's Note covers any diagram inside it (one note per section, regardless of how many diagrams that section contains).
- **Notes payload via clipboard.** "Copy notes" writes a markdown payload via `navigator.clipboard.writeText`; on failure, reveals a textarea with payload pre-selected for manual copy.
- **LocalStorage persistence.** Notes survive refresh; "Restore previous notes?" prompt on reload when a matching prior session exists.
- **`beforeunload` warning.** Fires when notes exist and have not been copied since last edit.


## Theme Tokens

```css
:root {
  --bg: #0d1117;
  --panel: #161b22;
  --border: #30363d;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --accent: #58a6ff;
  --accent-warn: #f85149;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
body { background: var(--bg); color: var(--text); font-family: var(--ui); margin: 0; padding: 1.5rem 2rem; }
code, pre { font-family: var(--mono); }
```


## Section Anchor Scheme

Anchor key = lowercase-kebab of the verbatim H2 text:
- `Functional Requirements` → `functional-requirements`
- `Success Metrics` → `success-metrics`

Collisions resolved by suffix (`-2`, `-3`). Anchors are stable across re-runs as long as headings don't change.

The **payload uses the verbatim heading text**, not the kebab anchor — downstream skills match against their own headings without slug normalization.

**Nested H3 cards** (e.g. per-option cards inside a trade-off `## Options` section) carry `data-anchor-parent="<parent-anchor>"` purely as a CSS / DOM hook for layout; only H2 sections carry `data-anchor` and a Note affordance. One Note per H2 covers the whole section regardless of how many H3 cards it contains.


## Notes State Shape

Single state object. Every interaction reads/writes through it. Persist on every change.

```javascript
const state = {
  artifactPath: '<the path the user passed to the skill>',  // use as-given (typically project-relative); do NOT canonicalize to absolute — downstream skills receive this in the payload header and match against their own working-tree paths
  artifactSha1: '<sha-1 hex of artifactPath>',
  tabUuid: sessionStorage.getItem('andthen-visualize-tab-uuid') || (() => {
    const u = crypto.randomUUID();
    sessionStorage.setItem('andthen-visualize-tab-uuid', u);
    return u;
  })(),  // per-tab, stable across refresh; sessionStorage scope = tab lifetime
  notes: [
    {
      sectionAnchor: 'functional-requirements',
      headingVerbatim: 'Functional Requirements',
      text: 'Split FR-3 into FR-3a/FR-3b',
      createdAt: '2026-05-04T14:30:00Z'
    }
  ],
  notesDirty: false  // set to true on every add/edit/delete; reset to false ONLY after a successful clipboard copy
};
```

**`notesDirty` write sites** — set to `true` in every code path that mutates `state.notes` (add note, edit note text, delete note). The reset to `false` lives in the success branch of `copyNotes()` only. A second edit after a copy MUST flip the flag back to `true` so `beforeunload` re-arms.


## Notes Payload Format (exact)

When the user clicks "Copy notes" with N>0 notes attached, write this to clipboard:

```markdown
# andthen:visualize notes for <artifact-path>

## Section: <heading text verbatim>
- <note 1 text>
- <note 2 text>

## Section: <next heading verbatim>
- <note text>
```

Group consecutive notes by `sectionAnchor`, but use `headingVerbatim` in the rendered `## Section: ...` line. Preserve note order within each section.

If `notes.length === 0`, do not write to clipboard. Show inline "No notes to copy" near the button.


## Clipboard Write with Fallback

```javascript
async function copyNotes() {
  if (state.notes.length === 0) {
    flashInline('No notes to copy');
    return;
  }
  const payload = buildPayload(state.notes, state.artifactPath);
  try {
    await navigator.clipboard.writeText(payload);
    state.notesDirty = false;
    flashCopiedFeedback();
  } catch {
    revealTextareaFallback(payload);
  }
}
```

Textarea fallback: insert a visible `<textarea>` pre-populated with `payload`, focus it, call `.select()`, with the message *"Clipboard write blocked. Copy the payload below manually."*


## LocalStorage

Key scheme: `andthen:visualize:<artifactSha1>:<tabUuid>`

```javascript
function saveToLocalStorage() {
  try {
    const key = `andthen:visualize:${state.artifactSha1}:${state.tabUuid}`;
    localStorage.setItem(key, JSON.stringify({
      artifactPath: state.artifactPath,
      tabUuid: state.tabUuid,
      notes: state.notes,
      updatedAt: new Date().toISOString()
    }));
  } catch {}
}
```

On load, scan for any keys matching `andthen:visualize:<artifactSha1>:` from a *different* tabUuid. If found, prompt *"Restore previous notes?"* — accept copies them into `state.notes` and **sets `state.notesDirty = true`** so the `beforeunload` warning re-arms (the restored notes were never copied to clipboard *in this tab*; treating them as already-saved would let the user lose them on accidental tab close).

If LocalStorage is unavailable (private browsing): show a one-time warning at top of page — *"Note persistence disabled (private browsing?). Notes won't survive refresh."* Render proceeds.


## `beforeunload` Warning

```javascript
window.addEventListener('beforeunload', (e) => {
  if (state.notes.length > 0 && state.notesDirty) {
    e.preventDefault();
    e.returnValue = '';
  }
});
```

The standard browser warning shows. We don't customize the message — most browsers ignore custom strings.


## Browser-Open Detection (Bash)

After writing the HTML, run the OS-appropriate open command. On any failure, print the path with `Open this in your browser:` prefix and exit 0.

```bash
case "$(uname -s)" in
  Darwin*)            opener="open" ;;
  Linux*)             opener="xdg-open" ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT) opener='start ""' ;;
  *)                  opener="" ;;
esac
if [ -n "$opener" ] && command -v "${opener%% *}" >/dev/null 2>&1; then
  $opener "$html_path" >/dev/null 2>&1 || echo "Open this in your browser: $html_path"
else
  echo "Open this in your browser: $html_path"
fi
```


## Common Mistakes

- **External resources** (CDN scripts, web fonts, hosted icons) → must work from `file://`, inline everything.
- **`agent-browser`** → wrong tool. It's used by the `andthen:excalidraw-diagram` skill for *automation*. Visualize wants the user's *primary* browser.
- **Non-deterministic class names or DOM ordering** → keep section blocks ordered as in the source; class names follow the section anchor scheme.
- **Slug-normalizing the payload heading** → keep verbatim H2 text in the payload. Slugs are for in-page anchors only.
- **Dropping notes on copy success** → reset `notesDirty = false` but preserve `notes[]`. The user may keep editing.
- **Skipping LocalStorage** → refresh-loses-work is a real UX bug; persistence is mandatory.
- **Customizing the `beforeunload` message** → don't bother, browsers ignore it.
- **Hand-building HTML for diagrams from scratch each time** → use `templates/diagrams.md` for the coordinate math; it's the part most likely to be wrong.


## FOLLOW-UP ACTIONS

Skip this section when `AUTO_MODE=true` — print only the output path.

After the user reviews the rendered artifact and copies notes:

1. **Apply notes via downstream skill** — paste the clipboard payload into the chat when invoking the relevant downstream skill:
   - PRD review notes → `andthen:prd` (amendment context) or as conversational input to a fresh `andthen:plan` invocation
   - Clarification review notes → `andthen:clarify` amendment mode
   - Trade-off review notes → next `andthen:architecture` invocation (e.g. ADR formalization)
   - Strategic-design review notes → next `andthen:architecture` invocation (e.g. `--mode strategic-design` for refinement, `--mode fitness` to formalize, or `--mode decompose` for a contested boundary)
2. **Re-visualize after edits** — re-run `/andthen:visualize <path>` on the updated artifact to verify changes landed.
