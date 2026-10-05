---
description: Simplify code for clarity, reuse, and leanness (YAGNI) – reduce complexity and over-engineering while preserving exact behavior. Trigger on 'simplify this code', 'clean this up', 'refactor this'.
argument-hint: "[--auto] [scope: paths and/or description]"
---

# Simplify Code

Simplify the scope for clarity, reuse, and leanness, with behavior preserved exactly.

## Input

`$ARGUMENTS` minus flags is the scope – paths, a description, or both; `PATH_SCOPE` is the paths it names, when it names any.

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.

Every run reads [`verification-evidence.md`](../../references/verification-evidence.md).

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Preserve exact behavior** – change only *how* the code works, never *what* it does, unless explicitly requested.
- **Scope stays the user's** – this is Boy Scout cleanup inside the requested scope. Widening to an adjacent module mid-flow is the named failure mode; that module is a separate run.
- Observable or exported removals are `behavior-affecting`: propose them, require explicit approval.
- **Architecture.** A cleanup that would move code across a component boundary – checked against the `Architecture` document (**Project Document Index**) only when a candidate would – belongs in the `andthen:architecture` skill first, not in this run.
- **Intent anchor.** When Step 1 read an Intent anchor, drop any cleanup it rejects – one contradicting a Non-Goal, implementing an outcome the artifact defers to a later story, or restructuring code the artifact chose a shape for – and record each in the completion summary as `dropped: <anchor> in <FIS path>`.

## Workflow

### 1. Scope & Baseline

1. Resolve scope in precedence order, and treat the result as authoritative:
   1. `PATH_SCOPE`.
   2. Described files – analyze the codebase to identify matches.
   3. The current branch diff against its base/upstream (fall back to `git diff HEAD`).
   4. Files named or edited earlier in this conversation.

   In an unattended run, the diff/conversation fallback is defensible only when it yields a non-empty, cohesive set; otherwise stop rather than simplifying against noise.
2. Resolve the project's check commands per `verification-evidence.md`; they serve both this baseline and Step 4. A green gate result the invocation hands over for this tree is the baseline; otherwise run them and record the result.
3. The governing FIS is the Intent anchor: the one the arguments name, each FIS of a plan they name, else the one discoverable for the scope's paths. Read its `What We're NOT Doing` and `Architecture Decision` sections, and the PRD or `Product` document only where it cites them: the FIS already carries what binds from them. With none, record `Intent Context: none discoverable` in the completion summary: Step 2 falls back to code-quality heuristics alone.

**Gate**: scope defined, baseline recorded, Intent anchor read or recorded as absent.

### 2. Analysis

**Reuse** – existing utilities, helpers, and project primitives that replace new or hand-rolled code, and divergence from the codebase's dominant pattern for the same job (error shape, data access, naming).

**Quality** – stringly-typed code where a domain type exists. Dead code and unused exports count only when the project's analyzer or a structural search proves them unused – a text grep does not.

**Efficiency** – the ones the model under-weights: recurring no-op state updates that still notify consumers, existence pre-checks where operate-and-handle-the-error is safer, unbounded structures, uncleaned listeners, and overly broad reads or loads.

**Necessity (YAGNI)**

- Generality with no current requirement: one-use abstractions, pass-through layers, unused parameters/configuration.
- Guards for states already excluded by types, caller contracts, or upstream validation.
- Tests that duplicate the same intent/boundary/failure sensitivity or assert implementation rather than behavior.

Remove only complexity proved inert across its real boundary. One caller or overlapping coverage is not proof (Chesterton's Fence).

Produce a prioritized list of improvements, then proceed with the conservative, lowest-risk subset. Drop genuinely risky or scope-widening items, and record the deferred items in the completion summary.

**Gate**: every candidate is applied-next, deferred, or `dropped:` with its anchor, and the deferred and dropped ones are recorded.

### 3. Simplification

Execute improvements from the prioritized list:

- Apply removals before refinements: code another finding deletes isn't worth polishing.
- For large or separable scopes, use parallel implementer subagents by lens or path: the installed `implementer` role agent when available, else a generic inherited subagent; never pin model or effort in a prompt. Each returns its changed paths and the items it deferred.

**Gate**: every applied item maps to a list entry, and approved `behavior-affecting` removals have their tests and callers updated.

### 4. Verification

With the relevant `Key Dev Commands` resolved in Step 1:

1. **Linting/types**: run full-project typecheck and lint when configured.
2. **Tests**: run tests scoped to changed paths when the runner supports it; broaden to the full suite when the changed code is shared or hot-path.

**Gate**: every check the baseline had green still passes, no new lint/type errors, and a check already failing at the baseline is reported, not fixed. A cleanup that turns a check red is edited back, never fixed forward, because behavior is the contract.

## Output

The completion summary names what was applied and deferred, each `dropped:` item, `Intent Context: none discoverable` when no anchor was found, and the verification evidence per `verification-evidence.md`.

## Follow-up

Code review: invoked by another skill, leave it to that skill. Standalone, a substantial change ends on a `Next (fresh session):` line invoking the `andthen:review` skill over the changed paths, for correctness, because this session is the change's author.
