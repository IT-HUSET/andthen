---
description: Improve, simplify, and refactor code for clarity, consistency, and maintainability. Trigger on 'refactor this', 'clean this up', 'simplify this code'.
argument-hint: "[--auto|--headless] <scope/description | --path <dir/file>>"
---

# Refactor & Simplify Code

Systematic code improvement – simplification, refactoring, and cleanup. The goal: make code easier to understand and change while preserving exact behavior.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--auto`, `--headless`, or `--path` before interpreting the remainder as the scope/description)

### Optional Flags
- `--auto` / `--headless` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Preserve exact behavior** – change only *how* the code works, never *what* it does, unless explicitly requested
- **No scope creep** – only refactor what's specified
- **Tests must pass** before and after refactoring
- Match the codebase's existing conventions and style – read the project guidelines before making style judgments
- **Automation rules** (headless-first, `--auto` / `--headless` strict mode, `--auto` propagation): see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md). Refactor-specific `BLOCKED:` triggers: red baseline (tests/build/lint failing before any refactor edit), no defensible scope derivable from arguments or recent git history, ambiguity between two or more incompatible refactor directions with no conservative default.
- **Anti-rationalization** — refactor's job is Boy Scout cleanup *within the user's requested scope* (per CRITICAL RULES); widening to other modules or files mid-flow is the failure mode. Reject these common rationalizations:
  - "I'll refactor this adjacent module too while I'm here" — that widens scope; leave it for a separate refactor pass.
  - "This behavior change is obviously safe" — refactors preserve behavior exactly; behavior changes are a separate commit.
  - "Tests can come later" — a green baseline before and after is the refactor's only safety net.
  - "Three clever lines beat six clear ones" — readability is the goal; compactness is not.

### Refactoring Philosophy

The purpose of refactoring is to make code easier to understand, maintain, and extend. Favor **readable, explicit code** over compact or clever solutions:

- **Reduce complexity**: flatten nesting, eliminate over-abstraction, remove dead code and unused imports
- **Improve clarity**: better naming, consolidate related logic, remove comments that describe the obvious
- **Eliminate duplication**: extract shared logic only when it genuinely reduces maintenance burden
- **Respect balance**: don't over-simplify – avoid combining too many concerns into single functions, don't remove helpful abstractions, don't prioritize "fewer lines" over readability, don't create overly clever solutions that are hard to debug or extend


## GOTCHAS
- Changing behavior while refactoring – preserve all existing functionality
- Not establishing a baseline (tests pass, build succeeds) before starting
- Over-simplification that makes code harder to debug or extend
- Premature abstraction – three similar lines of code is often better than one clever helper


## WORKFLOW

### Phase 1: Scope & Baseline

#### 1.1. Determine Scope

**If `--path` flag present:**
- Use specified file(s)/directory as scope

**If description provided:**
- Analyze codebase to identify relevant files matching the description

**If no arguments:**
- Use `git diff --name-only HEAD~5` to find recently changed files
- In `AUTO_MODE`, this fallback is only defensible when it yields a small, cohesive file set; stop with `BLOCKED: no defensible scope (no --path, no description, recent-git-history fallback yielded {nothing | shallow-clone error | a wide cross-module set})` rather than refactoring against noise

#### 1.2. Establish Baseline
- Run existing tests to confirm passing state
- Run linting/type checks
- Note current state for regression comparison
- In `AUTO_MODE`, a red baseline triggers `BLOCKED:` (per INSTRUCTIONS) rather than Stop-the-Line iteration — refactor never tries to fix the baseline itself

**Gate**: Scope defined, baseline passing


### Phase 2: Analysis

Analyze the scoped code for improvement opportunities:
- Unnecessary complexity, over-abstraction
- Code duplication
- Dead code, unused imports/variables
- Inconsistent patterns or naming
- Readability and maintainability issues
- Simplification opportunities

Before proposing removal of any code, understand why it exists — check callers, tests, and git history. Never remove what you don't understand (Chesterton's Fence).

Produce a prioritized list of improvements. Ask user for confirmation before proceeding if changes are substantial. In `AUTO_MODE`, do not pause for confirmation — proceed with the conservative, lowest-risk subset (drop genuinely risky or scope-widening items) and record the deferred items in the completion summary.


### Phase 3: Refactoring

Execute improvements from the prioritized list:
- Work file-by-file or by logical unit
- For independent changes, use **parallel sub-agents**
- Verify each change preserves existing behavior
- Keep individual changes small and verifiable – don't batch unrelated improvements


### Phase 4: Verification

Run in **parallel sub-agents**:

1. **Tests**: Run full test suite – all tests must pass
2. **Code review**: Invoke the `andthen:review` skill with `--mode code` to verify improvements and catch regressions
3. **Linting/types**: Run static analysis, confirm no new issues

**If failures:** fix issues and re-verify before completing.

**Gate**: All tests pass, no regressions, no new lint/type errors.

Include verification evidence in completion summary (as applicable):
- **Tests**: pass/fail counts (e.g., "42/42 pass")
- **Linting/types**: error and warning counts
- **Build**: exit code or success/failure status

In `AUTO_MODE`, suppress conversational sections per [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md) and emit a deterministic block the orchestrator can parse:
- `STATUS:` `OK` | `BLOCKED:` (use the `BLOCKED:` line shape from the canonical when not OK)
- `FILES_CHANGED:` newline-separated paths (relative to repo root); empty if no edits landed
- `VERIFY:` one line per check, format `<check>: <result>` (e.g. `tests: 42/42 pass`, `lint: 0 errors / 0 warnings`, `build: ok`)
- `DEFERRED:` newline-separated items dropped from Phase 2's prioritized list under `AUTO_MODE` conservatism (Phase 2 clause); empty if none
- Print only this block plus the artifact paths above; skip "Next Steps" / "FOLLOW-UP" prose
