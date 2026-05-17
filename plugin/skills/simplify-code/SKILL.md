---
description: Simplify and refine code for clarity, reuse, quality, and efficiency while preserving exact behavior. Trigger on 'simplify this code', 'clean this up', 'refactor this', 'reduce complexity'.
argument-hint: "[--auto|--headless] [--path <dir/file>] [scope/description]"
---

# Simplify Code

Behavior-preserving code improvement. Make scoped code easier to read, reuse, test, and change without changing what it does.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--auto`, `--headless`, or `--path` before interpreting the remainder as the scope/description)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- **Fully read and understand all project rules, guardrails, principles and guidelines (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files) before starting work.**
- **Preserve exact behavior** – change only *how* the code works, never *what* it does, unless explicitly requested
- **No scope creep** – simplify only the requested or defensibly resolved scope
- **Tests must pass** before and after simplification
- Match the codebase's existing conventions and style – read the project guidelines before making style judgments
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Simplify-code-specific `BLOCKED:` triggers: red baseline (tests/build/lint failing before any simplify edit), no defensible scope derivable from arguments, current-branch diff, or conversation context, ambiguity between two or more incompatible simplification directions with no conservative default.
- **Anti-rationalization** – simplify-code's job is Boy Scout cleanup *within the user's requested scope* (per CRITICAL RULES); widening to other modules or files mid-flow is the failure mode. Reject these common rationalizations:
  - "I'll clean this adjacent module too while I'm here" – that widens scope; leave it for a separate simplify pass.
  - "This behavior change is obviously safe" – simplification preserves behavior exactly; behavior changes are a separate commit.
  - "Tests can come later" – a green baseline before and after is the simplification safety net.
  - "Three clever lines beat six clear ones" – readability is the goal; compactness is not.

### Simplification Philosophy

Favor **readable, explicit code** over compact or clever solutions. Reduce complexity, improve naming, remove dead code, and eliminate duplication where it genuinely helps. Preserve helpful abstractions; over-simplification that makes code harder to debug is not an improvement.


## GOTCHAS
- Not establishing a baseline (tests pass, build succeeds) before starting
- Over-simplification that makes code harder to debug or extend
- Premature abstraction – three similar lines of code is often better than one clever helper


## WORKFLOW

### Phase 1: Scope & Baseline

#### 1.1. Determine Scope

**If `--path` flag present:**
- Use specified file(s)/directory as authoritative scope

**If description provided:**
- Analyze codebase to identify relevant files matching the description
- Treat user-named scope as authoritative; do not widen it

**If no arguments:**
- In a git repository, default to the current branch diff against its base branch or upstream. If no base is available, fall back to staged + unstaged changes (`git diff HEAD`).
- Outside git, or when no diff is available, use files clearly mentioned by the user or edited earlier in this conversation.
- In `AUTO_MODE`, this fallback is only defensible when it yields a non-empty, cohesive scope; stop with `BLOCKED: no defensible scope (no --path, no description, branch-diff/conversation fallback yielded {nothing | shallow-clone error | a wide cross-module set})` rather than simplifying against noise.

#### 1.2. Establish Baseline
- Use the commands from the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`) for all baseline and Phase 4 verification calls. Fall back to discovery (package.json scripts, Makefile targets, language conventions) only when the document is missing.
- Run existing tests to confirm passing state
- Run linting/type checks
- Note current state for regression comparison
- In `AUTO_MODE`, a red baseline triggers `BLOCKED:` (per INSTRUCTIONS) rather than Stop-the-Line iteration – simplify-code never tries to fix the baseline itself

**Gate**: Scope defined, baseline passing


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

Produce a prioritized list of improvements. Ask user for confirmation before proceeding if changes are substantial. In `AUTO_MODE`, do not pause for confirmation – proceed with the conservative, lowest-risk subset (drop genuinely risky or scope-widening items) and record the deferred items in the completion summary.


### Phase 3: Simplification

Execute improvements from the prioritized list:
- Work file-by-file or by logical unit
- For large or separable scopes, use parallel sub-agents by lens or path; pass each the resolved scope or full diff
- Verify each change preserves existing behavior
- Keep individual changes small and verifiable – don't batch unrelated improvements


### Phase 4: Verification

Use the relevant commands from the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`) read in Phase 1.2. Fall back to discovery only when the document was missing.

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
