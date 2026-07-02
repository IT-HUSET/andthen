---
description: Simplify and refine code for clarity, reuse, quality, and efficiency while preserving exact behavior. Trigger on 'simplify this code', 'clean this up', 'refactor this', 'reduce complexity'.
argument-hint: "[--auto] [--path <dir/file>] [scope/description]"
---

# Simplify Code

Make scoped code easier to read, reuse, test, and change.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--auto`, `--headless`, or `--path` before interpreting the remainder as the scope/description)

### Optional Flags
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules and guidelines (`CLAUDE.md` / `AGENTS.md` and referenced files) before starting.
- **Intent + Rules Context** – per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md) (collected in Phase 1.3). Behavior-preserving is not intent-preserving: the Phase 2 Intent anchor drops cleanups that contradict the Intent (surfaced in the completion summary, not applied).
- **Preserve exact behavior** – change only *how* the code works, never *what* it does, unless explicitly requested
- Match the codebase's existing conventions and style – read the project guidelines before making style judgments
- **Automation rules** (headless-first, `--auto` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Simplify-code-specific `BLOCKED:` triggers: red baseline (tests/build/lint failing before any simplify edit), no defensible scope derivable from arguments, current-branch diff, or conversation context, ambiguity between two or more incompatible simplification directions with no conservative default.
- **Anti-rationalization** – simplify-code's job is Boy Scout cleanup *within the user's requested scope* (per CRITICAL RULES); widening to other modules or files mid-flow is the failure mode. Reject these common rationalizations:
  - "I'll clean this adjacent module too while I'm here" – that widens scope; leave it for a separate simplify pass.
  - "This behavior change is obviously safe" – simplification preserves behavior exactly; behavior changes are a separate commit.
  - "Tests can come later" – a green baseline before and after is the simplification safety net.

### Simplification Philosophy

Favor **readable, explicit code** over compact or clever solutions. Reduce complexity, improve naming, remove dead code, and eliminate duplication where it genuinely helps. Preserve helpful abstractions; over-simplification that makes code harder to debug is not an improvement.


## GOTCHAS
- **Boy Scout cleanup that crosses Intent boundaries** – see the Phase 2 Intent anchor.
- **Picking up `SURFACED` findings from a prior run of the `andthen:remediate-findings` skill** – those are findings an upstream gate explicitly declined to auto-apply. Cleaning them up here re-introduces the drift the routing gate prevented.


## WORKFLOW

### Phase 1: Scope & Baseline

#### 1.1. Determine Scope

Resolve scope in precedence order: `--path` > described files (analyze the codebase to identify matches) > current branch diff against its base/upstream (fall back to `git diff HEAD`) > files named or edited earlier in this conversation. Treat the resolved scope as authoritative – never widen it.

In `AUTO_MODE`, the diff/conversation fallback is defensible only when it yields a non-empty, cohesive set; otherwise stop with `BLOCKED: no defensible scope (no --path, no description, branch-diff/conversation fallback yielded {nothing | shallow-clone error | a wide cross-module set})` rather than simplifying against noise.

#### 1.2. Establish Baseline
- Use the commands from the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`) for all baseline and Phase 4 verification calls. Fall back to discovery (package.json scripts, Makefile targets, language conventions) only when the document is missing.
- Establish a green baseline (tests + lint/type checks pass); record current state for regression comparison.
- In `AUTO_MODE`, a red baseline triggers `BLOCKED:` (per INSTRUCTIONS) rather than Stop-the-Line iteration – simplify-code never tries to fix the baseline itself

#### 1.3. Collect Intent + Rules Context

Collect the **Project Rules Context** and **Intent Context** bundles per [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md). Walk up from the resolved scope's paths to find the governing FIS, PRD, `clarify` artifact, or active plan story; consult the **Project Document Index** in `CLAUDE.md` when present. Extract Intent, Expected Outcomes, Non-Goals, and any explicit deferrals.

When no governing artifact is discoverable, record `Intent Context: none discoverable` in the completion summary – Phase 2 falls back to code-quality heuristics alone. Do not synthesize intent from the code itself.

**Gate**: Scope defined, baseline passing, Intent + Rules Context bundles collected (or recorded as absent with the reason)


### Phase 2: Analysis

Analyze the scoped code through three lenses:

**Reuse**
- Existing utilities, helpers, components, or project patterns that replace newly written code
- New functions or inline logic duplicating existing behavior
- Hand-rolled string/path/env/type-guard code where the project already has a better primitive

**Quality**
- Redundant state, parameter sprawl, copy-paste with slight variation, leaky abstractions
- Stringly typed code where constants, enums, unions, or domain types already exist
- Nested conditionals that would read better as guard clauses, lookup tables, or flatter branches
- Unnecessary comments explaining what the code does instead of why it exists
- Dead code, unused imports, unused exports; prefer configured analyzers or structural search over plain text grep when proving usage

**Efficiency**
- Redundant computation, repeated file reads, duplicate network/API calls, N+1 patterns
- Missed concurrency for independent operations
- New blocking work in startup, request, render, or polling hot paths
- Recurring no-op state/store updates that notify downstream consumers without a real change
- Pre-checking resource existence before operating where direct operation plus error handling is safer
- Unbounded data structures, missing cleanup, event/listener leaks, or overly broad reads/loads

Before proposing removal of any code, understand why it exists – check callers, tests, and git history. Never remove what you don't understand (Chesterton's Fence).

Cross-check against the `Architecture` document (see **Project Document Index**) if it exists – simplification should respect documented component boundaries and not silently change architectural shape. A cleanup that crosses boundaries belongs in the `andthen:architecture` skill with `--mode advise` first, not bundled into this run.

**Intent anchor.** When Intent Context was collected in Phase 1.3, consult it for each proposed cleanup. Apply the canonical anchor moves from [`intent-and-rules-context.md`](${CLAUDE_PLUGIN_ROOT}/references/intent-and-rules-context.md):

- **Cleanup contradicts a Non-Goal** (e.g. "no external dependencies", "no shared helpers across feature boundaries", "no caching layer in v1") → drop the cleanup; record it in the completion summary as `dropped: contradicts Non-Goal in <FIS path>`.
- **Cleanup implements behavior the artifact defers to a later story** (folds duplicate computation into a memo when the FIS deferred caching, extracts a façade the FIS deferred to a refactoring story) → drop; record `dropped: implements deferred outcome in <FIS path>`.
- **Cleanup restructures code the FIS explicitly chose a shape for** (a flat function chosen for hot-path performance, an inlined branch chosen for readability over abstraction) → drop; record `dropped: contradicts Expected Outcome / Structural Criterion in <FIS path>`.

Produce a prioritized list of improvements. Ask user for confirmation before proceeding if changes are substantial. In `AUTO_MODE`, do not pause for confirmation – proceed with the conservative, lowest-risk subset (drop genuinely risky or scope-widening items and any cleanup the Intent anchor flagged) and record the deferred items in the completion summary.


### Phase 3: Simplification

Execute improvements from the prioritized list:
- Work file-by-file or by logical unit
- For large or separable scopes, use parallel sub-agents by lens or path; pass each the resolved scope or full diff
- Verify each change preserves existing behavior
- Keep individual changes small and verifiable – don't batch unrelated improvements


### Phase 4: Verification

Use the relevant `Key Dev Commands` resolved in Phase 1.2.

1. **Linting/types**: Run full-project typecheck and lint when configured; these catch the common simplification regressions.
2. **Tests**: Run tests scoped to changed paths when the runner supports it. Broaden to related suites or the full suite when the changed code is shared, hot-path, or structurally significant. If the runner has no scoping mechanism, run the full suite.
3. **Code review**: For substantial changes, invoke the `andthen:review` skill with `--mode code` or the `andthen:quick-review` skill to catch regressions from fresh context.

**If failures:** fix issues and re-verify before completing.

**Gate**: All tests pass, no regressions, no new lint/type errors.

Include verification evidence in completion summary (as applicable):
- **Tests**: pass/fail counts (e.g., "42/42 pass")
- **Linting/types**: error and warning counts
- **Build**: exit code or success/failure status
- **Unavailable checks**: state explicitly when no tests, lint, or typecheck are configured

In `AUTO_MODE`, suppress conversational sections per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md) and emit a deterministic block the orchestrator can parse:
- `STATUS:` `OK` | `BLOCKED:` (use the `BLOCKED:` line shape from the canonical when not OK)
- `FILES_CHANGED:` newline-separated paths (relative to repo root); empty if no edits landed
- `VERIFY:` one line per check, format `<check>: <result>` (e.g. `tests: 42/42 pass`, `lint: 0 errors / 0 warnings`, `build: ok`)
- `DEFERRED:` newline-separated items dropped from Phase 2's prioritized list under `AUTO_MODE` conservatism (Phase 2 clause); empty if none
- Print only this block plus the artifact paths above; skip "Next Steps" / "FOLLOW-UP" prose
