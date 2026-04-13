---
description: Quick implementation path for small features or fixes with verification
argument-hint: <spec> | --issue <number>
---

# Quick Implement with Verification

Fast implementation path for small features, bug fixes, or GitHub issues. Bypasses FIS workflow for quick turnaround while maintaining verification quality.

**For larger features, use the full workflow:** `andthen:clarify` → `andthen:spec` → `andthen:exec-spec`


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

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** in CLAUDE.md / AGENTS.md before starting.
- **Autonomously and iteratively** implement with comprehensive verification
- **Iterate** until all requirements met, no defects remain, all reviews pass
- Use GitHub CLI (`gh`) for GitHub operations


## GOTCHAS
- Skipping verification after implementation – always run tests/build
- Scope creep: implementing more than was asked
- Use structured output protocols (`${CLAUDE_PLUGIN_ROOT}/references/structured-output-protocols.md`) when encountering ambiguity or undefined requirements


## WORKFLOW

### Phase 1: Analysis

#### 1.1. Parse Input & Get Requirements

**If `--issue` flag present:**
1. Extract issue number and fetch with `gh issue view <number>`
2. If the issue body contains a typed envelope per `${CLAUDE_PLUGIN_ROOT}/references/github-artifact-roundtrip.md`:
   - `artifact_type: triage-plan` is compatible — use the embedded plan as the implementation scope
   - Any `*-review` artifact is **not** compatible — stop and direct the user to `andthen:remediate-findings`
   - `plan-bundle`, `fis-bundle`, and `triage-completion` are **not** compatible — stop and direct the user to the appropriate plan / spec / triage workflow
3. Set `CREATE_PR=true` (unless `--no-pr` specified)
4. Create feature branch following project conventions

**Otherwise:** use inline spec from arguments; set `CREATE_PR=true` only if `--pr` flag present.

#### 1.2. Analyze & Plan

1. Understand requirements and scope – interpret as *what* to implement, not *how*
2. Analyze codebase: `tree -d` and `git ls-files | head -250` for overview; use Explore agent for complex exploration
3. Read relevant documentation (use the `andthen:documentation-lookup` agent as needed)
4. Break down into manageable tasks and track them

**Gate**: Plan complete, all requirements understood


### Phase 2: Implementation Loop

Execute: Implementation → Verification → Evaluation. Repeat until all requirements met, no defects, all reviews pass.

#### Step 1: Implementation

- Write tests first where applicable, otherwise alongside implementation
- Write code following existing codebase patterns and project guidelines
- Use **sub-agents** _(if supported)_ for independent tasks
- Delegate build issues to the `andthen:build-troubleshooter` agent _(if supported)_

#### Step 2: Verification

Run in parallel _(if supported; otherwise sequentially)_:

**2.1. Code & Architecture Review** – Invoke the `andthen:review-code` skill for static analysis, linting, type checking, code quality, security, architecture.

**2.2. Run Tests** – Execute all tests with project-specific commands.

**2.3. Visual Validation** (if UI changed) – Follow Visual Validation Workflow from project guidelines; verify via screenshot analysis.

**2.4. Final Quality Assurance** (orchestrator, not delegated) – Review sub-agent results; check for gaps; review implemented code for simplification opportunities.

#### Step 3: Evaluation

- Verify implementation meets all requirements and acceptance criteria
- Mark completed todos
- If issues remain: analyze feedback, update todos, execute another loop

**Gate**: All validations pass – builds correctly, tests pass, no review issues, no regressions.

Include verification evidence per `${CLAUDE_PLUGIN_ROOT}/references/verification-evidence.md`: **Build**, **Tests**, **Linting/types**; add **Visual validation** when UI changed, **Runtime** when app was started or flow exercised.


### Phase 3: Completion (conditional)

**Only if `CREATE_PR=true` or `--issue` mode:**

1. Commit with descriptive message (reference issue number if applicable)
2. Push branch to remote
3. Create PR: `gh pr create` with issue link ("Fixes #<number>" if applicable), implementation description, relevant labels
4. Print the PR URL and number

**Gate**: PR created (or changes committed if no PR)


## Post-Completion
Follow `${CLAUDE_PLUGIN_ROOT}/references/post-completion-guide.md` (`Quick Implement` → `STATE.md` and `Learnings`).
