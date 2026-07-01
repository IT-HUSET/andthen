---
description: Drive a FIS or plan bundle to zero open blocking decisions before an unattended exec run. Interactively interviews the user on each implementation-blocking decision, settles open ADRs, persists every resolution by altitude, and emits a machine-stable READY/DEFERRED/BLOCKED verdict. Do not use to author a spec or PRD (use the andthen:spec / andthen:prd skills) or to execute one (use the andthen:exec-spec / andthen:exec-plan skills). Trigger on 'preflight this spec', 'preflight this plan', 'harden this FIS before exec', 'resolve blocking decisions', 'is this spec ready for unattended exec'.
argument-hint: "[target: FIS path | plan-bundle dir] [--auto]"
user-invocable: true
---

# Preflight: Converge to Zero Open Blocking Decisions

Drive a single FIS or a plan bundle to **zero open blocking decisions** before it is handed to an unattended `andthen:exec-spec` / `andthen:exec-plan` run, so the autonomous run never forks on an undecided choice. The premise is a trade in attention: spend a human's now so the executors spend none later.

Preflight does not re-spec and does not implement. It **composes by altitude** – it detects decisions with the `andthen:review` skill, settles open ADRs with the `andthen:architecture` skill, routes requirements-altitude gaps back to the `andthen:clarify` skill, resolves implementation-blocking decisions with its own interview, and persists every resolution through the `andthen:ops` skill.


## OPERATING PRINCIPLE

**Interactive-by-Contract.** Preflight's deliverable IS the interview that drives blocking decisions to closure – user input is the work, not an obstacle. Producing a verdict while a blocking decision the user has not answered remains open is a contract violation, not a shortcut. The "the spec looks complete" intuition is the agent rationalizing past the contract; run detection and the blocking-only drill-down anyway, and a no-op convergence (zero blocking decisions found) is the *only* sanctioned way to reach `READY` without a question.

Under `AUTO_MODE` this inverts to strict-mode automation discipline (see *Automation* below): never interview, never fabricate an answer – run the non-interactive passes and surface the unresolved blocking set as a signal.


## VARIABLES

TARGET: $ARGUMENTS (strip any flag token like `--auto` before interpreting the remainder as the target path)

- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts.


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- Require `TARGET`. Stop if missing or unresolvable (see Step 1).
- **Interactive-by-Contract** – see **OPERATING PRINCIPLE**.
- **Composition, not reimplementation** – preflight owns the convergence loop and the blocking-decision interview; it delegates detection, ADR authoring, and deterministic writes. Do not copy a doc-review rubric or a full `clarify` interview flow; load the composed skills instead. The composed skills are referenced as skills, never passed as an agent type.
- **The `andthen:ops` skill is the only sanctioned write path** for the status artifacts preflight touches: FIS decision-Notes, `docs/DECISIONS.md` Still Current notes, and `plan.json` `spec-ready` transitions. Never hand-edit them. ADR creation and indexing stays owned by the `andthen:architecture` skill.
- **`Preflight:` verdict grammar** – emit exactly one resolved token, once, as a bare line at line start beside (never inside) any verdict block: `^Preflight: (READY|DEFERRED|BLOCKED)$`. Never emit the menu form `Preflight: READY | DEFERRED | BLOCKED` literally – a consumer matches it line-anchored and the menu breaks the regex. The token is registered in `review-verdict.md` § Loop Convergence Signals as a sibling to `Auto-Remediation`; this line is the self-contained emit copy.
- **Automation** (`AUTO_MODE`) – strict no-prompt, deterministic-signal stance per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Run detection, drill-down, evidence gathering, and the misapplied-ADR check (applying its mechanical, decision-free doc-defect fix) only; hold no interview and invoke no interactive `architecture --mode trade-off` loop. Emit named blocks per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `BLOCKED:` for an unresolvable/ambiguous target or unsafe action; enumerate the unresolved blocking decisions as a signal/recommendation. Never invent an answer.


## DECISION RECORDS

Preflight treats detection output as **decision records**, not raw review findings. The record schema, the blocking/non-blocking split, plan-bundle identity matching, convergence, and the verdict semantics live in [`decision-records.md`](references/decision-records.md). The blocking-decision interview technique guide lives in [`blocking-decision-interview.md`](references/blocking-decision-interview.md). Load both before Step 2.

A record is **blocking** only when implementation would fork on an observable behavior, persistence location, architecture choice, or requirements-altitude question that no cited source resolves. Mechanical doc defects and advisory review Notes are non-blocking and never gate the verdict.


## WORKFLOW

### 1. Resolve Target

Auto-detect from `TARGET` – no flag:
- A readable file → **single FIS**.
- A directory (or a path) containing `plan.json` → **plan bundle** (`plan.json` + every story FIS).
- Neither, or ambiguous between the two → do not guess and do not silently converge. In default mode, name what was expected (a FIS file, or a directory containing `plan.json`) and ask which target. Under `AUTO_MODE`, emit `BLOCKED:` with the expected target shape and the ambiguity details, no prompt.

**Gate**: target resolved to a single FIS or a plan bundle; otherwise asked (default) or `BLOCKED:` (`AUTO_MODE`).

### 2. Detect

For each FIS (the single FIS, or every story FIS in the bundle), run detection via a fresh-context pass that invokes the `andthen:review` skill with `--mode doc --inline-findings <fis_path>` (append `--auto` under `AUTO_MODE`). `--inline-findings` keeps findings inline – preflight persists resolutions into the mutated artifacts and the decision log, so there is no standalone report (a non-goal).

Normalize each finding into a decision record per `decision-records.md`, then run the **blocking-only drill-down**: keep records that would fork unattended implementation; demote the rest to non-blocking. This is a blocking filter, not a second spec pass – do not re-derive requirements the FIS already settles.

**Gate**: every target FIS detected; records normalized; blocking set identified.

### 3. ADR Sweep

For each record at `adr` altitude:
- **Misapplied** (the FIS cites or assumes an ADR incorrectly, a mechanical doc defect) → mark a blocking Note and apply the narrow doc-defect edit (the `andthen:review` skill's `--fix`, or the `andthen:remediate-findings` skill for the mechanical doc-defect slice only – its routing gate declines decision-laden edits, so it is not the decision-apply engine).
- **Genuinely open**, default mode → settle inline by invoking the `andthen:architecture` skill (`--mode trade-off`) on the decision; it writes and indexes the ADR in `docs/DECISIONS.md`. Resume the loop with the record resolved.
- **Genuinely open**, `AUTO_MODE` → leave it as a blocking record (no interactive trade-off loop); list it in the signal.

**Gate**: every `adr` record settled, edited, or (AUTO_MODE) recorded as blocking.

### 4. Resolve (interactive loop)

For each remaining blocking record, drive it to closure. **Skip this step entirely under `AUTO_MODE`** – blocking records stay open for the signal.

- **Requirements-altitude** (`requirements`) → route to the `andthen:clarify` skill; do not resolve a requirements question at FIS level.
- **Implementation-blocking** → run preflight's own interview per `blocking-decision-interview.md`. One decision per question; offer a recommendation with a one-line rationale; wait for the user's answer. Use an interactive user input tool when available (e.g. `AskUserQuestion`), numbered markdown otherwise.
- **Deferral** → a decision the user chooses to punt converges only with explicit **sign-off**; on sign-off it moves to a Deferred Decisions block and stops counting as blocking.

Persist each outcome immediately, by altitude, through the `andthen:ops` skill:
- Local / reversible, or a signed-off deferral → `andthen:ops update-fis <fis_path> decision-note <decision_key> <resolved|deferred> <body>`.
- Long-term-important non-ADR → `andthen:ops update-decisions still-current <topic> <decision-and-rationale>`.
- Architecture-significant → ADR via the `andthen:architecture` skill (already handled in Step 3); not written by hand.

**Gate**: every blocking record resolved-in-place, settled, deferred-with-sign-off, or routed to `clarify`; each persisted at its altitude.

### 5. Cross-Story Consistency Sweep _(plan bundle only)_

After per-FIS convergence, match decision records across stories by `decision_key + altitude + affected_surface`. When two stories resolved the same dimension to **conflicting** values, reopen the affected records as new `open` blocking decisions and re-converge the affected stories (back to Step 4) before any story status flips. This sweep is lightweight – it flags contradictions, it does not re-detect.

**Gate**: no cross-story contradiction remains open.

### 6. Converge and Emit Verdict

For a plan bundle, flip each converged story to `spec-ready`: `andthen:ops update-plan <plan_path> <story_id> spec-ready`. A story that still carries an open blocking record keeps its current status – update the clear ones as they pass, even when the bundle as a whole is blocked.

Emit the verdict per the bare-line grammar (one resolved token, once), with the READY/DEFERRED/BLOCKED conditions and bundle precedence from `decision-records.md` § verdict semantics. Under `AUTO_MODE`, accompany `Preflight: BLOCKED` with the enumerated unresolved set.

**Gate**: verdict emitted as a bare line-anchored single resolved token; bundle story statuses updated for every converged story.


## REPORT

Print: the resolved target, the verdict line, and a per-decision ledger (decision_key, altitude, affected surface, outcome: resolved / deferred-signed-off / routed-to-clarify / open). For a plan bundle, list each story's status and which stories reached `spec-ready`. Under `AUTO_MODE` with `Preflight: BLOCKED`, the ledger's `open` rows ARE the signal the orchestrator branches on – present them as a recommendation, never an interactive wait.


## FOLLOW-UP ACTIONS

Skip under `AUTO_MODE` (print only the verdict, ledger, and downstream command shape).

On `READY` / `DEFERRED`, suggest the unattended run: the `andthen:exec-spec` skill for a single FIS, the `andthen:exec-plan` skill for a bundle. On `BLOCKED`, name the still-open decisions and the upstream skill each needs (the `andthen:clarify` skill for requirements gaps, the `andthen:architecture` skill with `--mode trade-off` for open ADRs).
