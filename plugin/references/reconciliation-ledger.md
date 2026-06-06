# Reconciliation Ledger

**Single canonical source** for the cross-skill reconciliation ledger: the durable, greppable record of deliberate spec-vs-code drift. Implementation and remediation skills write OPEN entries when a change leaves code or an upstream document out of sync with the governing FIS; review reads them to demote already-tracked drift out of the FAIL path and to require new evidence before re-raising a withdrawn finding; recurrence escalates an unreconciled entry once to a blocking state; completion-presentation gates refuse to present a run as shipped while entries are unresolved.

> Skills that reference this document: `ops` (the `update-ledger` mutator), `exec-spec`, `exec-plan`, `quick-review`, `review`, `remediate-findings`.

**Why this exists**: the finding-class axis (`code-defect | spec-stale | design-changed | ambiguous-intent`) already classifies drift correctly, but classification is stateless – each review re-discovers the same `spec-stale` finding, re-fails the verdict, and the drift is often *born* during implementation with no upstream propagation. The ledger is the minimal persistent state that makes classification self-terminating: a pivot recorded once stops being re-found as a "new" blocker, a finding withdrawn on a false falsifier cannot silently re-raise, and a run cannot be presented as closed while reconciliation is still pending. It stays **dumb, greppable, and deterministic** – no semantic dedup, no fuzzy matching, no spec-version vector clocks.


## Location (FIS-adjacent) and scope

The ledger is **per-FIS**, a sibling of its governing FIS: `{fis-path-without-extension}.reconciliation-ledger.md` (e.g. `docs/specs/checkout/s01-payment.md` → `docs/specs/checkout/s01-payment.reconciliation-ledger.md`). Consuming skills resolve the path from the FIS under execution/review and pass it to `ops`; **a run with no governing FIS resolves no ledger** (reconciliation needs a spec to reconcile against). It ships and dies with the feature – there is no project-global ledger.

**Scope: the code↔FIS boundary only.** Entries record code diverging from its governing FIS. Doc-lens review of a spec (FIS/PRD) classifies findings with the same vocabulary but **never writes ledger entries**; higher boundaries (FIS↔PRD, PRD↔vision) are human-owned and recommend-only.

`ops update-ledger add` may create the FIS-adjacent ledger from the **canonical template** (below) when absent; every transition form (`reconcile`, `withdraw`, `bump-recurrence`, `override-close`) requires an existing matching entry and never creates the file.


## Class and Status axes (orthogonal)

**Class** reuses the existing finding-class vocabulary from the intent-fidelity work – no new class is introduced. **All four classes are ledger-eligible.**

| Class | Ledger behavior |
|---|---|
| `code-defect` | Feeds the functional verdict's three code-correctness dimensions. Stays OPEN until fixed; **no recurrence escalation**. |
| `spec-stale` | Reconciliation drift. Follows the OPEN → `RECONCILE REQUIRED` recurrence-escalation ladder. Never feeds the verdict dimensions. |
| `design-changed` | Coherent implementation pivot from the spec. Same recurrence ladder as `spec-stale`. Never feeds the verdict dimensions. |
| `ambiguous-intent` | Decision-blocked. Stays OPEN until the missing decision is supplied; **no recurrence escalation**. Never feeds the verdict dimensions. |

**Status** is a separate, orthogonal dimension – it does **not** collapse into the `Class` axis or into Fix/Note routing. A WITHDRAWN `spec-stale` entry is still `spec-stale`; an OPEN entry never auto-applies code.

| Status | Meaning |
|---|---|
| `OPEN` | Active reconciliation work. Every OPEN entry, regardless of class, blocks the completion-presentation gate. |
| `RECONCILE REQUIRED` | An unreconciled `spec-stale`/`design-changed` entry that recurred. Blocking. Clearable **only** via the sanctioned design-change amendment (`ops update-fis design-change` + ADR), which transitions it to CLOSED. A bare re-run neither clears nor re-nags it. |
| `CLOSED` | Reconciliation applied (or escalation resolved). Terminal. Suppressed in future runs unless explicitly re-opened with new evidence. |
| `WITHDRAWN` | The finding was judged invalid with a recorded falsifier. Suppressed in future runs; re-opens only when a run supplies new evidence that explicitly refutes the recorded falsifier. |

Only `spec-stale`/`design-changed` walk the recurrence ladder. `code-defect` and `ambiguous-intent` have no recurrence escalation – they stay OPEN until fixed or decided.


## Stable finding ID

The cross-run identity of an entry. Deterministic, greppable, derived from durable inputs only – **never** from run timestamps, finding order, or a content hash.

**Full ID**: `{relative-path}:{class}:{normalized-title-slug}`

Normalization:
- `{relative-path}` – POSIX relative path (forward slashes; relative to repo root).
- `{class}` – the lowercase canonical class value (`code-defect` / `spec-stale` / `design-changed` / `ambiguous-intent`).
- `{normalized-title-slug}` – the finding title text lowercased, with punctuation and whitespace runs collapsed to single `-`, and repeated/edge hyphens trimmed.

**Matching key**: cross-run matching keys **primarily on `{relative-path}:{class}`**. The `{normalized-title-slug}` is a *secondary disambiguator*, applied only when two or more entries share the same path and class. Because finding titles are model-generated phrasing, keying primarily on path+class keeps run-to-run match stability off the title wording; when multiple entries share that key, the full stable ID selects the intended entry.

Matching is **exact-string**. No hash as the primary ID, no semantic/ML similarity step, no spec-version vector clock.


## Entry schema

Each entry is a greppable markdown block under `## Entries`. The stable ID is the `###` heading; every field is a `Key: value` line so `rg` can target any dimension (`rg "Status: OPEN"`, `rg "RECONCILE REQUIRED"`, `rg "^### "`).

```markdown
### {relative-path}:{class}:{normalized-title-slug}
- Status: OPEN | RECONCILE REQUIRED | CLOSED | WITHDRAWN
- Class: code-defect | spec-stale | design-changed | ambiguous-intent
- Stale targets: {comma-separated upstream docs left stale, e.g. docs/PRODUCT.md#admin-roles, README.md} | –
- Source run: {skill + brief run ref, e.g. exec-spec reconciliation-ledger 2026-06-04}
- Recurrence: {integer; initial OPEN = 1}
- Falsifier: {recorded falsifier text when WITHDRAWN; – otherwise}
- Override reason: {reason recorded by override-close; – otherwise}
- Created: {YYYY-MM-DD}
- Updated: {YYYY-MM-DD}
- Notes: {freeform one-line context; optional}
```

Fields stay one-per-line so transitions are surgical single-line edits and the file diffs cleanly.


## Status lifecycle and transitions

```
                 bump-recurrence (count → 2, spec-stale/design-changed only)
   add ──► OPEN ───────────────────────────────► RECONCILE REQUIRED
            │                                            │
            │ reconcile (applied)                        │ reconcile (design-change + ADR)
            ▼                                            ▼
          CLOSED ◄────────────────────────────────── CLOSED
            ▲
            │ withdraw (+ falsifier)
   any ─────┴──► WITHDRAWN ──► (re-OPEN only when a new run refutes the recorded falsifier)
```

- **add** → create an OPEN entry with `Recurrence: 1`. Idempotent on the full stable ID: if an OPEN/RECONCILE-REQUIRED entry already has the same `{relative-path}:{class}:{normalized-title-slug}`, do not duplicate. If another non-terminal entry shares only `{relative-path}:{class}`, append the new slug as a distinct entry. **Terminal-match re-open branch**: if a terminal entry (`CLOSED`/`WITHDRAWN`) matches by the normal matching key – unique `{relative-path}:{class}` first, full stable ID only when that key is ambiguous – `add` requires refuting evidence and re-opens the *existing* entry **in place**. Transition it back to OPEN, record the refuting evidence, and preserve the prior `Falsifier` as history; never append a second entry for that same match. Without refuting evidence, an `add` against a terminal match is rejected (a suppressed entry does not silently re-create).
- **bump-recurrence** → for an OPEN `spec-stale`/`design-changed` entry re-surfaced while still unreconciled, increment `Recurrence`. When it reaches **2**, transition the entry to `RECONCILE REQUIRED`. Further re-surfacings neither create duplicates nor re-nag. No-op for `code-defect`/`ambiguous-intent` (they do not escalate).
- **reconcile** → transition an OPEN or RECONCILE-REQUIRED entry to `CLOSED` when the reconciliation has been applied. For a `RECONCILE REQUIRED` entry the only sanctioned trigger is the design-change amendment (`ops update-fis design-change` + ADR).
- **withdraw** → transition any non-terminal entry to `WITHDRAWN`, recording the `Falsifier`. A withdrawn entry stays suppressed until a later run cites **new evidence that explicitly refutes the recorded falsifier**, which re-opens it (back to OPEN) with that evidence cited.
- **override-close** → record an `Override reason` against an OPEN/RECONCILE-REQUIRED entry so a completion-presentation gate may proceed despite pending reconciliation. This is an escape hatch, not a default: the reason is recorded against the specific entry; a blanket bypass with no recorded reason is forbidden.

Reject malformed transitions (no matching entry, illegal source state, missing required argument such as a falsifier on `withdraw` or a reason on `override-close`).


## Recurrence and escalation rules (deterministic)

1. The initial OPEN entry has `Recurrence: 1`.
2. The next **unresolved re-surfacing** of the same stable ID (same matching key, entry still OPEN, upstream still unamended) is a `bump-recurrence` to `Recurrence: 2`, which transitions `spec-stale`/`design-changed` entries to `RECONCILE REQUIRED`.
3. Further re-runs neither clear the entry nor create duplicate nags – the single `RECONCILE REQUIRED` entry is the durable, actionable record.
4. `RECONCILE REQUIRED` clears **only** via the sanctioned design-change amendment (`ops update-fis design-change` + ADR) → CLOSED. A bare re-run cannot clear or re-nag it.


## Match-and-route rules (review-side)

When a review run loads the ledger and computes a finding's stable ID, route by the matched entry's **status and class** (a finding can only match an entry of its own class, since `{class}` is part of the matching key – so the OPEN-match branch is class-aware):

- **OPEN match, `spec-stale` / `design-changed`** → already-tracked reconciliation work, **not** a fresh blocker: record the finding as Note tied to the existing entry. Reconciliation-class findings never feed the verdict's three code-correctness dimensions. If still unreconciled, `bump-recurrence` (which may escalate to `RECONCILE REQUIRED`).
- **OPEN match, `code-defect`** → a known-but-unfixed bug: keep class `code-defect` and **continue feeding the verdict** (it stays a real blocker until fixed – do *not* demote it to Note, which would hide an unfixed defect). No recurrence escalation. It is *not* "new" for the CONVERGED criterion, so a re-matched code-defect keeps the verdict FAIL without blocking convergence.
- **OPEN match, `ambiguous-intent`** → decision-blocked: record as Note tied to the entry; no recurrence escalation; stays OPEN until the missing decision is supplied. Does not feed the verdict.
- **RECONCILE REQUIRED match** → existing blocking reconciliation work: record as Note tied to the entry, do not bump recurrence, do not duplicate, and do not feed reconciliation-class findings into the verdict dimensions. The completion-presentation gate remains the blocker until the sanctioned design-change + ADR reconciliation closes the entry.
- **CLOSED / WITHDRAWN match** → keep the finding in the report's withdrawn/suppressed section; do **not** promote it to a blocker. Exception: if the run supplies new evidence that explicitly refutes the recorded falsifier, **re-open the entry in place** (back to OPEN) via `update-ledger add` with that evidence cited – `add`'s terminal-match branch preserves the entry identity and prior falsifier rather than duplicating (see *Status lifecycle and transitions*).
- **No match** → a genuinely new finding; route normally per the review routing gate.

**Verdict scoping**: the gap-verdict's three dimensions (Functionality / Completeness / Wiring) are fed **only by `code-defect` findings**. `spec-stale` / `design-changed` / `ambiguous-intent` findings route to Note and never lower them, so OPEN-matched reconciliation drift cannot drag the verdict to FAIL. Only `code-defect` can.

**CONVERGED stopping criterion**: a review pass is CONVERGED when it produces **no new `code-defect` at severity ≥ MEDIUM** – where OPEN-ledger-matched findings are not "new". CONVERGED is emitted as an additive line alongside the unchanged byte-level `## Verdict` block (the Verdict block format is a parser contract; CONVERGED and any ledger annotations are parsed separately). CONVERGED is a reachable stopping criterion instead of chasing zero findings.


## Completion-presentation gate

The gate lives in the **orchestrating skills** (the `exec-plan` completion summary and the `exec-spec` standalone completion summary), **not** in the `ops` status mutators – `ops` mutators stay single-document. The orchestrating skill resolves each ledger adjacent to its governing FIS (exec-plan across all its stories' FISes) and reads it directly.

- A run **cannot be presented as shipped/complete** while the ledger holds any `OPEN` or `RECONCILE REQUIRED` entry, unless an explicit override reason is recorded against those entries (`ops update-ledger override-close`). The refusal names the blocking entries.
- **Per-story status writes are NOT gated**: `ops update-state active-story ... Done` and per-story `ops update-plan ... done` proceed normally even when the story opened a reconciliation entry. The entry is the durable record; upstream reconciliation is human-owned and recommend-only, so a story legitimately records its own completion. Gating per-story writes would deadlock the autonomous pipeline.


## As-Built Upstream Reconciliation recommendation

When a run (exec-spec, exec-plan rolling up its stories, or remediation) wrote OPEN ledger entries, it emits an **As-Built Upstream Reconciliation** recommendation at wrap-up, listing each open entry and the upstream targets needing update. It is **recommend-only for the PRD and other product-level docs** – the ledger recommends, the human applies; never auto-edit the PRD. In `AUTO_MODE` the recommendation is surfaced as text (never an interactive wait).


## AUTO_MODE invariant

Every new path surfaces its recommendation / `BLOCKED:` text and never waits interactively. Critically, a **deferred (`BLOCKED:`) design pivot still writes its OPEN ledger entry** – the entry write precedes the `BLOCKED:` emit – so the pivot is durably recorded rather than lost. Letting the AUTO_MODE `BLOCKED:` path skip the ledger write defeats the whole point.


## Canonical template

`ops update-ledger add` scaffolds this when the target file is absent:

```markdown
# Reconciliation Ledger

> Durable, greppable record of deliberate spec-vs-code drift. Entries are written by implementation and remediation skills and transitioned by review / remediation. See `reconciliation-ledger.md` for the schema, stable-ID derivation, status lifecycle, and match/recurrence/escalation rules.

## Entries

_No reconciliation entries recorded yet._
```

`add` removes the `_No reconciliation entries recorded yet._` placeholder (exact-string match) when appending the first entry.
