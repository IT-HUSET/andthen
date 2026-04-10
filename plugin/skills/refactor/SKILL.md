---
description: Improve, simplify, and refactor code for clarity, consistency, and maintainability
argument-hint: <scope/description> | --path <dir/file>
---

# Refactor & Simplify Code

Systematic code improvement – simplification, refactoring, and cleanup. The goal: make code easier to understand and change while preserving exact behavior.


## VARIABLES

ARGUMENTS: $ARGUMENTS


## USAGE

```
/refactor <description of what to improve>    # Targeted refactoring by description
/refactor --path src/api/                     # Refactor specific path
/refactor --path src/utils.ts                 # Refactor specific file
/refactor                                     # Refactor recently changed code
```


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work
- **Preserve exact behavior** – change only *how* the code works, never *what* it does, unless explicitly requested
- **No scope creep** – only refactor what's specified
- **Tests must pass** before and after refactoring
- Match the codebase's existing conventions and style – read the project guidelines before making style judgments

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

#### 1.2. Establish Baseline
- Run existing tests to confirm passing state
- Run linting/type checks
- Note current state for regression comparison

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

Produce a prioritized list of improvements. Ask user for confirmation before proceeding if changes are substantial.


### Phase 3: Refactoring

Execute improvements from the prioritized list:
- Work file-by-file or by logical unit
- For independent changes, use **parallel sub-agents** _(if supported)_
- Verify each change preserves existing behavior
- Keep individual changes small and verifiable – don't batch unrelated improvements


### Phase 4: Verification

Run in **parallel sub-agents** _(if supported; otherwise sequentially)_:

1. **Tests**: Run full test suite – all tests must pass
2. **Code review**: Use `andthen:review-code` to verify improvements and catch regressions
3. **Linting/types**: Run static analysis, confirm no new issues

**If failures:** fix issues and re-verify before completing.

**Gate**: All tests pass, no regressions, no new lint/type errors.

Include verification evidence in completion summary (as applicable):
- **Tests**: pass/fail counts (e.g., "42/42 pass")
- **Linting/types**: error and warning counts
- **Build**: exit code or success/failure status
