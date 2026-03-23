---
description: Improve, simplify and refactor code using the code-simplifier:code-simplifier agent
argument-hint: <scope/description> | --path <dir/file>
---

# Refactor & Simplify Code


Systematic code improvement – simplification, refactoring, and cleanup – using the `code-simplifier:code-simplifier` agent.


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
- **No functional changes** unless explicitly requested – preserve existing behavior
- **No scope creep** – only refactor what's specified
- **Tests must pass** before and after refactoring
- Delegate refactoring work to `code-simplifier:code-simplifier` agent (if available)


## GOTCHAS
- Changing behavior while refactoring – preserve all existing functionality
- Not establishing a baseline (tests pass, build succeeds) before starting


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

Use the `code-simplifier:code-simplifier` agent (if available) to analyze the scoped code for:
- Unnecessary complexity, over-abstraction
- Code duplication (DRY violations)
- Dead code, unused imports/variables
- Inconsistent patterns or naming
- Readability and maintainability issues
- Simplification opportunities

Produce a prioritized list of improvements. Ask user for confirmation before proceeding if changes are substantial.


### Phase 3: Refactoring

Delegate to `code-simplifier:code-simplifier` agent (if available):
- Execute improvements from the prioritized list
- Work file-by-file or by logical unit
- For independent changes, use **parallel sub-agents**
- Ensure each change preserves existing behavior


### Phase 4: Verification

Run in **parallel sub-agents**:

1. **Tests**: Run full test suite – all tests must pass
2. **Code review**: Use the `andthen:review-code` skill to verify improvements and catch regressions
3. **Linting/types**: Run static analysis, confirm no new issues

**If failures:** fix issues and re-verify before completing.

**Gate**: All tests pass, no regressions, no new lint/type errors.

Include verification evidence in completion summary (as applicable):
- **Tests**: pass/fail counts (e.g., "42/42 pass")
- **Linting/types**: error and warning counts
- **Build**: exit code or success/failure status
