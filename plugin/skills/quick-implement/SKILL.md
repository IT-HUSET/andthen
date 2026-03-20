---
description: Quick implementation path for small features or fixes with verification
argument-hint: <spec> | --issue <number>
---

# Quick Implement with Verification

Fast implementation path for small features, bug fixes, or GitHub issues. Bypasses FIS workflow for quick turnaround while maintaining verification quality.

**For larger features, use the full workflow:** `clarify` → `spec` → `exec-spec`


## VARIABLES

ARGUMENTS: $ARGUMENTS


## USAGE

```
/quick-implement <feature description>        # Implement from inline spec
/quick-implement --issue 123                  # Implement from GitHub issue (auto-PR)
/quick-implement --issue 123 --no-pr          # From issue, skip PR creation
/quick-implement <spec> --pr                  # Inline spec + create PR
```


## INSTRUCTIONS

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Autonomously and iteratively** implement with comprehensive verification
- **Iterate** until all requirements met, no defects remain, all reviews pass
- Use GitHub CLI (`gh`) for GitHub operations


## GOTCHAS
- Skipping verification after implementation — always run tests/build
- Scope creep: implementing more than was asked for in the issue


## WORKFLOW

### Phase 1: Analysis

#### 1.1. Parse Input & Get Requirements

**If `--issue` flag present:**
1. Extract issue number from arguments
2. Use `gh issue view <number>` to fetch issue details
3. Set `CREATE_PR=true` (unless `--no-pr` specified)
4. Create feature branch following project conventions

**Otherwise:**
1. Use inline specification from arguments
2. Set `CREATE_PR=true` only if `--pr` flag present

#### 1.2. Analyze & Plan

1. Understand requirements and scope - interpret as *what* to implement, not *how*
2. Analyze codebase structure and relevant patterns
   - Use `tree -d` and `git ls-files | head -250` for overview
   - For complex exploration, use the Explore agent
3. Read relevant documentation (use `andthen:documentation-lookup` as needed)
4. Identify roadblocks and plan mitigation
5. Break down into manageable todos/tasks and use task management tools to track them
6. **Think hard** - ensure plan is comprehensive

**Gate**: Plan complete, all requirements understood


### Phase 2: Implementation Loop

- Execute implementation loop consisting of: Implementation → Verification → Evaluation
- Repeat loop until all requirements met, no defects remain, all reviews pass. 

#### Step 1: Implementation

- Write tests first where applicable, otherwise alongside implementation
- Write code following existing codebase patterns
- Follow project guidelines strictly
- Use **sub-agents** _(if supported by your coding agent)_ for independent implementation tasks
- Delegate build issues to `andthen:build-troubleshooter` _(if supported by your coding agent)_

#### Step 2: Verification

Run each verification sub-step using **parallel sub-agents** _(if supported by your coding agent; otherwise execute sequentially)_:

##### 2.1. Code & Architecture Review
- Static analysis, linting, type checking
- Use the `andthen:review-code` skill for comprehensive review (code quality, security, architecture, UI/UX)

##### 2.2. Run Tests
- Execute all tests
- Use project-specific test commands
- Fix issues that arise

##### 2.3. Visual Validation (if applicable)
- Follow Visual Validation Workflow from project guidelines
- Verify UI changes meet requirements and design specs, by actual screenshot analysis

##### 2.4. Final Quality Assurance
As orchestrator (not delegated to sub-agent):
- Review all sub-agent results
- Check for functionality gaps or requirement mismatches
- Use `code-simplifier:code-simplifier` agent _(if supported by your coding agent)_ to look for simplification, maintainability, and general quality of life improvement opportunities

#### Step 3: Evaluation

- Verify implementation meets all requirements
- Review work against each task's acceptance criteria
- Correct implementation of requirements and acceptance criteria must be verified through tests and visual validation (when applicable).
- Mark completed todos in tracking

**If issues remain:**
- Analyze feedback from reviews and testing
- Request user clarification if needed
- Update todos for next iteration
- Execute another Implementation Loop

**Gate**: All validations pass - builds correctly, tests pass, no review issues, no regressions.

Include verification evidence in completion summary (as applicable):
- **Build**: exit code or success/failure status
- **Tests**: pass/fail counts (e.g., "42/42 pass")
- **Linting/types**: error and warning counts
- **Visual validation**: screenshot confirming UI matches expectations (if UI)
- **Runtime**: confirmation app starts and key flows work

> *Don't skip this: "the change is simple, it obviously works" is not evidence.
> Code review ≠ running the code. If tests passed before your change, run them again after.*


### Phase 3: Completion (conditional)

**Only execute if `CREATE_PR=true` or `--issue` mode:**

1. Commit changes with descriptive message
   - If from issue: reference issue number
2. Push branch to remote
3. Create PR using `gh pr create`:
   - Link to issue (include "Fixes #<number>" if applicable)
   - Brief description of implementation
   - Add relevant labels

**Gate**: PR created successfully (or changes committed if no PR)


## REPORT
After completed implementation, if the project has a learnings file (`LEARNINGS.md` or `implementation-notes.md`), append any **traps, gotchas, and non-obvious patterns** discovered during this implementation. Organize by topic. If no such file exists and there are noteworthy traps, create a *Learnings* section at the end of the original spec document.

The bar for inclusion: *"Would a competent developer with access to the code and git history still get bitten by this?"* Keep entries brief (1-2 sentences each). Do NOT record:
- What was implemented or how parts integrate (that's in git history and code)
- Routine decisions or deviations (that's in the spec)
- Language basics or standard framework behavior
