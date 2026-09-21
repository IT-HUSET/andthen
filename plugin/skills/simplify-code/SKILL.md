---
description: Simplify code for clarity, reuse, and leanness (YAGNI) – reduce complexity and over-engineering while preserving exact behavior. Trigger on 'simplify this code', 'clean this up', 'refactor this', 'remove over-engineering'.
argument-hint: "[--auto] [scope: dir/file path and/or description]"
---

# Simplify Code

`$ARGUMENTS` minus flags is the scope – a directory or file path, a description, or both; `PATH_SCOPE` is the path it names, when it names one. `--auto` is `AUTO_MODE`: automation-safe execution with no conversational prompts.


## INSTRUCTIONS

- **Intent + Rules Context** – per [`intent-and-rules-context.md`](../../references/intent-and-rules-context.md) (collected in Phase 1.3). Behavior-preserving is not intent-preserving: the Phase 2 Intent anchor drops cleanups that contradict the Intent (surfaced in the completion summary, not applied).
- **Preserve exact behavior** – change only *how* the code works, never *what* it does, unless explicitly requested
- Ground style judgments in the codebase's existing conventions and the project guidelines – not in generic taste
- **Automation rules** (headless-first, `--auto` strict mode, `--auto` propagation): see [`automation-mode.md`](../../references/automation-mode.md). Simplify-code-specific `BLOCKED:` triggers:
  - red baseline – tests, build, or lint failing before any simplify edit;
  - no defensible scope derivable from arguments, current-branch diff, or conversation context;
  - ambiguity between two or more incompatible simplification directions with no conservative default.
- **Scope stays the user's** – this is Boy Scout cleanup inside the requested scope; widening to an adjacent module mid-flow is the named failure mode, and that module is a separate run.
- **Lean code** over defensive bulk – every abstraction, guard, and test must be paid for by a present requirement, not a hypothetical one (YAGNI).


## GOTCHAS
- **Picking up `SURFACED` findings from a prior run of the `andthen:implement-fix` skill** – those are findings an upstream gate explicitly declined to auto-apply. Cleaning them up here re-introduces the drift the routing gate prevented.


## WORKFLOW

### Phase 1: Scope & Baseline

#### 1.1. Determine Scope

Resolve scope in precedence order:

1. `PATH_SCOPE`.
2. Described files – analyze the codebase to identify matches.
3. The current branch diff against its base/upstream (fall back to `git diff HEAD`).
4. Files named or edited earlier in this conversation.

Treat the resolved scope as authoritative – never widen it.

In `AUTO_MODE`, the diff/conversation fallback is defensible only when it yields a non-empty, cohesive set; otherwise stop with `BLOCKED: no defensible scope (no path, no description, branch-diff/conversation fallback yielded {nothing | shallow-clone error | a wide cross-module set})` rather than simplifying against noise.

#### 1.2. Establish Baseline
- Resolve the project's check commands per [`verification-evidence.md`](../../references/verification-evidence.md); they serve both this baseline and Phase 4.
- Establish a green baseline (tests + lint/type checks pass); record current state for regression comparison.
- In `AUTO_MODE`, a red baseline triggers `BLOCKED:` (per INSTRUCTIONS) rather than Stop-the-Line iteration – simplify-code never tries to fix the baseline itself

#### 1.3. Collect Intent + Rules Context

Collect the **Project Rules Context** and **Intent Context** bundles per [`intent-and-rules-context.md`](../../references/intent-and-rules-context.md). Walk up from the resolved scope's paths to find the governing FIS, PRD, `clarify` artifact, or active plan story; consult the **Project Document Index** when present. Extract Intent, Expected Outcomes, Non-Goals, and any explicit deferrals.

When no governing artifact is discoverable, record `Intent Context: none discoverable` in the completion summary – Phase 2 falls back to code-quality heuristics alone. Do not synthesize intent from the code itself.

**Gate**: Scope defined, baseline passing, Intent + Rules Context bundles collected (or recorded as absent with the reason)


### Phase 2: Analysis

**Reuse** – existing utilities, helpers, and project primitives that replace new or hand-rolled code, and divergence from the codebase's dominant pattern for the same job (error shape, data access, naming).

**Quality** – naming, redundant state, parameter sprawl, leaky abstractions, stringly-typed code where a domain type exists, nested conditionals a guard clause or lookup table would flatten, comments restating the code. Dead code and unused exports count only when the project's analyzer or a structural search proves them unused – a text grep does not.

**Efficiency** – redundant computation and repeated I/O, N+1s, missed concurrency, new blocking work in a startup, request, render, or polling path. The ones the model under-weights: recurring no-op state updates that still notify consumers, existence pre-checks where operate-and-handle-the-error is safer, unbounded structures, uncleaned listeners, and overly broad reads or loads.

**Necessity (YAGNI)**
- Generality with no current requirement: one-use abstractions, pass-through layers, unused parameters/configuration.
- Guards for states already excluded by types, caller contracts, or upstream validation.
- Tests that duplicate the same intent/boundary/failure sensitivity or assert implementation rather than behavior.

Remove only complexity proved inert across its real boundary. One caller or overlapping coverage is not proof; check callers, tests, and history (Chesterton's Fence).

Observable or exported removals are `behavior-affecting`: propose them, require explicit approval, and defer them in `AUTO_MODE`.

Cross-check against the `Architecture` document (see **Project Document Index**) if it exists – simplification should respect documented component boundaries and not silently change architectural shape. A cleanup that crosses boundaries belongs in the `andthen:architecture` skill first, not bundled into this run.

**Intent anchor.** When Intent Context was collected in Phase 1.3, drop any cleanup its anchor moves reject – one contradicting a Non-Goal, implementing an outcome the artifact defers to a later story, or restructuring code the artifact chose a shape for – and record each in the completion summary as `dropped: <anchor> in <FIS path>`.

Produce a prioritized list of improvements, then proceed with the conservative, lowest-risk subset – drop genuinely risky or scope-widening items and any cleanup the Intent anchor flagged, and record the deferred items in the completion summary.


### Phase 3: Simplification

Execute improvements from the prioritized list:
- Apply removals before refinements – code another finding deletes isn't worth polishing
- For large or separable scopes, use parallel subagents by lens or path
- For approved `behavior-affecting` removals, verify tests and callers reflect the removal


### Phase 4: Verification

With the relevant `Key Dev Commands` resolved in Phase 1.2:

1. **Linting/types**: Run full-project typecheck and lint when configured.
2. **Tests**: Run tests scoped to changed paths when the runner supports it; broaden to the full suite when the changed code is shared or hot-path.
3. **Code review**: For substantial changes, invoke the `andthen:review` skill with `--mode code` to catch regressions from fresh context.

**Gate**: All tests pass, no regressions, no new lint/type errors.

Include the applicable verification evidence fields from [`verification-evidence.md`](../../references/verification-evidence.md) in the completion summary, and state explicitly when no tests, lint, or typecheck are configured.

In `AUTO_MODE`, emit the deterministic completion summary per [`automation-mode.md`](../../references/automation-mode.md):

- changed paths relative to the repo root;
- one line per verification check with its result;
- the items Phase 2 conservatism dropped, including unapproved `behavior-affecting` findings;
- `BLOCKED:` in place of the summary when the run could not complete.
