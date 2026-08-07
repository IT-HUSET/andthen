---
description: Drive a FIS or plan bundle to zero open blocking decisions before unattended execution – interviews the user per decision, settles open ADRs, emits a machine-stable READY/DEFERRED/BLOCKED verdict. Authoring belongs to the `andthen:spec` skill or `andthen:prd` skill; execution belongs to the `andthen:exec-spec` skill or `andthen:exec-plan` skill. Trigger on 'preflight this spec', 'resolve blocking decisions', 'ready for unattended exec'.
argument-hint: "[target: FIS path | plan-bundle dir] [--auto]"
user-invocable: true
---

# Preflight: Converge to Zero Open Blocking Decisions

Drive a single FIS or plan bundle to **zero open blocking decisions** before the `andthen:exec-spec` skill or `andthen:exec-plan` skill runs unattended, so execution never forks on an undecided choice.

Preflight does not author requirements or implement. It **composes by altitude**: the `andthen:review` skill detects; the `andthen:clarify` skill handles requirements gaps; the `andthen:architecture` skill handles ADRs/forks; investigation sharpens implementation choices for Preflight's interview; the `andthen:spike` skill settles empirical unknowns; and the `andthen:ops` skill persists.


## OPERATING PRINCIPLE

**Interactive-by-Contract.** Preflight closes blocking decisions through user answers. A verdict with an unanswered blocker violates the contract. Always run detection and the blocking-only drill-down; only zero blockers may yield `READY` without a question.

Under `AUTO_MODE` this inverts to strict-mode automation discipline – see *Automation* below.


## VARIABLES

TARGET: $ARGUMENTS with flags and their values removed – the target path
UNTRUSTED_REQUIREMENTS_DATA: derive the exact canonical line from the target FIS/PRD header or governing plan and preserve it across composed skill boundaries

- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts.


## INSTRUCTIONS

- Apply project rules (`CLAUDE.md` / `AGENTS.md` – read only if not already in context) and read the referenced guideline files relevant to this work.
- Require `TARGET`. Stop if missing or unresolvable (see Step 1).
- Resolve and propagate Source Trust per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) before decision prose. Pass the exact untrusted line to every composed skill receiving derived content; ops receives only validated deterministic values.
- **Interactive-by-Contract** – see **OPERATING PRINCIPLE**.
- **Composition, not reimplementation** – preflight owns the convergence loop and the blocking-decision interview; it delegates detection, ADR authoring, and deterministic writes. Do not copy a doc-review rubric or a full `clarify` interview flow; load the composed skills instead. The composed skills are referenced as skills, never passed as an agent type.
- **Preflight never hand-edits.** Its decision/body reconciliation, decision Notes, `docs/DECISIONS.md` notes, and plan transitions use the `andthen:ops` skill. Step 3's delegated review/remediation skill remains the writer for a mechanical authoring defect. ADR creation and indexing stays owned by the `andthen:architecture` skill.
- **`Preflight:` verdict grammar** – emit exactly one resolved token, once, as a bare line at line start beside (never inside) any verdict block: `^Preflight: (READY|DEFERRED|BLOCKED)$`. Never emit the menu form `Preflight: READY | DEFERRED | BLOCKED` literally – a consumer matches it line-anchored and the menu breaks the regex. The token is registered in `review-verdict.md` § Loop Convergence Signals as a sibling to `Auto-Remediation`; this line is the self-contained emit copy.
- **Automation** (`AUTO_MODE`) – strict no-prompt, deterministic-signal stance per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Run detection, drill-down, evidence gathering, and the misapplied-ADR check (applying its mechanical, decision-free doc-defect fix) only; hold no interview, run no spike, and invoke no interactive `architecture --mode trade-off` loop. Emit named blocks per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `BLOCKED:` for an unresolvable/ambiguous target or unsafe action; enumerate the unresolved blocking decisions as a signal/recommendation. Never invent an answer.


## DECISION RECORDS

Preflight treats detection output as **decision records**, not raw review findings. The record schema, the blocking/non-blocking split, plan-bundle identity matching, convergence, and the verdict semantics live in [`decision-records.md`](references/decision-records.md). The blocking-decision interview technique guide lives in [`blocking-decision-interview.md`](references/blocking-decision-interview.md). Load both before Step 2.


## WORKFLOW

### 1. Resolve Target

Auto-detect from `TARGET` – no flag:
- A readable file → **single FIS**.
- A directory (or a path) containing `plan.json` → **plan bundle**. Include `spec-ready`; provisionally include `blocked` when it has a canonical valid FIS so Step 2 can classify an open or deferred hold. A `pending` story, missing/invalid FIS, or explicit `OVERSIZE:`/authoring failure stays unchanged and makes the bundle `BLOCKED` with its upstream route. Preserve `in-progress`, `done`, and `skipped`; preflight neither authors missing FISs nor clears non-decision holds.
- Neither, or ambiguous between the two → do not guess and do not silently converge. In default mode, name what was expected (a FIS file, or a directory containing `plan.json`) and ask which target. Under `AUTO_MODE`, emit `BLOCKED:` with the expected target shape and the ambiguity details, no prompt.

**Gate**: target resolved to a single FIS or a plan bundle; otherwise asked (default) or `BLOCKED:` (`AUTO_MODE`).

### 2. Detect

For each FIS, first hydrate persisted decisions using [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) § Persisted Decision Blocks. Malformed, conflicting, or unsigned blocks keep the target `BLOCKED`. Then run a fresh-context pass that invokes the `andthen:review` skill with `--mode doc --inline-findings <fis_path>` and the exact trust line when untrusted.

Normalize fresh findings and merge them with persisted records by `decision_key`, reopening a stale persisted resolution when evidence refutes it. Run the **blocking-only drill-down**: keep records that would fork unattended implementation; demote the rest. A provisional `blocked` story is eligible when it carries an open or valid deferred decision; otherwise classify it manual/unclassified, preserve it, and block with its upstream route.

**Gate**: every target FIS detected; records normalized; blocking set identified.

### 3. ADR Sweep

For each record at `adr` altitude:
- **Misapplied** (the FIS cites or assumes an ADR incorrectly, a mechanical doc defect) → mark a blocking Note and apply the narrow doc-defect edit (the `andthen:review` skill's `--fix`, or the `andthen:remediate-findings` skill for the mechanical doc-defect slice only – its routing gate declines decision-laden edits, so it is not the decision-apply engine).
- **Genuinely open**, default mode → settle inline by invoking the `andthen:architecture` skill (`--mode trade-off`) on the decision; it writes and indexes the ADR in `docs/DECISIONS.md`. Resume the loop with the record resolved.
- **Genuinely open**, `AUTO_MODE` → leave it as a blocking record (no interactive trade-off loop); list it in the signal.

**Gate**: every `adr` record settled, edited, or (AUTO_MODE) recorded as blocking.

### 4. Resolve (interactive loop)

For each remaining blocking record, drive it to closure. **Skip this step entirely under `AUTO_MODE`** – blocking records stay open for the signal.

- **Requirements-altitude** (`requirements`) → route to the `andthen:clarify` skill. Keep the record open while the handoff runs; on return, re-detect and reconcile the affected FIS surface before closing it.
- **Implementation-altitude but not sharp** → investigate the relevant code and architecture until the fork is precise. A genuine architecture fork routes to the `andthen:architecture` skill and returns; otherwise the now-sharp choice enters preflight's own interview below. Keep the record open and close only after the resolution is persisted and reconciled into the affected FIS body.
- **Implementation-blocking** → run preflight's own interview per `blocking-decision-interview.md`.
- **Empirical unknown** → a blocking decision that turns on evidence only a spike can supply settles via the `andthen:spike` skill on that one question, closing per `blocking-decision-interview.md` § Closing a decision.
- **Deferral** → records a signed execution hold; it does not make the target runnable. See `decision-records.md` § Convergence.

Persist each outcome at its altitude through the `andthen:ops` skill (resolved `fis-local` lands in Step 5's atomic write):
- signed-off deferral → `andthen:ops update-fis <fis_path> decision-note <decision_key> deferred <body>`.
- resolved `fis-local` → prepare its decision record plus exact old/new body amendment for Step 5's single atomic ops write.
- `project-decision` → `andthen:ops update-decisions still-current <topic> <decision-and-rationale>`.
- `adr` → already settled in Step 3; never hand-written.

**Gate**: every blocking record resolved-in-place, settled, deferred-with-sign-off, or returned from its upstream handoff and re-detected; each outcome persisted at its altitude or staged for Step 5's atomic write.

### 5. Reconcile

A resolution the FIS body contradicts is not closed – the body is what an executor implements. For each record resolved this run, invoke `andthen:ops update-fis <fis_path> decision-note <decision_key> resolved <body>` with the decision fields and exact `Old:`/`New:` pairs for its named `affected_surface`. Ops applies the body reconciliation and provenance Note atomically; preflight never edits the FIS itself. Deferred records leave the body untouched.

Then check coherence: the resolved set against itself and against the reworked body. Two individually sound answers that share an affected surface may not compose – a contradiction reopens the involved records (back to Step 4).

For every amended FIS, re-run fresh doc readiness and each affected scenario's Proof binding against the final contract. A stale/missing binding keeps the record open and routes through the owning `andthen:spec` skill (or mechanical review/remediation), then re-detects; Proof identity is never assumed valid because ops preserved it.

**Gate**: every resolved decision stated in the body it affects; no contradiction within the resolved set or between a resolution and the body.

### 6. Cross-Story Consistency Sweep _(plan bundle only)_

After per-FIS convergence, run the cross-story sweep per `decision-records.md` § Plan-bundle identity matching; re-converge stories with reopened records (back to Step 4) before any story status flips.

**Gate**: no cross-story contradiction remains open.

### 7. Converge and Emit Verdict

For a plan bundle, promote `blocked` only when its admitted decision hold was resolved this run, final FIS/Proof readiness passes, and re-detection finds no blocking/`OVERSIZE:`/authoring signal: `andthen:ops update-plan <plan_path> <story_id> spec-ready`. Preserve clear `spec-ready`; transition any story with an active signed deferral to `blocked`, including a newly deferred `spec-ready` story. Every other hold remains blocked.

Emit the verdict per the bare-line grammar, with the READY/DEFERRED/BLOCKED conditions and bundle precedence from `decision-records.md` § verdict semantics.

**Gate**: verdict emitted as a bare line-anchored single resolved token; bundle story statuses updated for every converged story.


## REPORT

Print: the resolved target, the verdict line, and a per-decision ledger (decision_key, altitude, affected surface, outcome: resolved / deferred-signed-off / open, including any active upstream handoff). For a plan bundle, list each story's status and which stories reached `spec-ready`. Under `AUTO_MODE` with `Preflight: BLOCKED`, the ledger's `open` rows ARE the signal the orchestrator branches on – present them as a recommendation, never an interactive wait.


## FOLLOW-UP ACTIONS

Skip under `AUTO_MODE` (print only the verdict, ledger, and next-action shape).

On `READY`, suggest the unattended run: the `andthen:exec-spec` skill for a single FIS, the `andthen:exec-plan` skill for a bundle. On `DEFERRED`, name the signed execution holds that must be resolved first. On `BLOCKED`, name the still-open decisions and the upstream skill each needs (the `andthen:clarify` skill for requirements gaps, the `andthen:architecture` skill with `--mode trade-off` for open ADRs, the `andthen:spike` skill for a decision blocked on an empirical unknown).
