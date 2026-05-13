---
description: Quick implementation path for small features or fixes with verification. Bypasses the FIS workflow – for larger features, use the `andthen:clarify` → `andthen:spec` → `andthen:exec-spec` chain instead. Trigger on 'quick fix this', 'implement this quickly', 'make this small change'.
argument-hint: "[--tdd] [--pr|--no-pr] <spec | --issue <number>>"
---

# Quick Implement with Verification

Fast implementation path for small features, bug fixes, or GitHub issues. Bypasses FIS workflow for quick turnaround while maintaining verification quality.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip any flag tokens like `--tdd`, `--pr`, `--no-pr`, or `--issue` before interpreting the remainder as the inline spec; `--pr`/`--no-pr` couple to input mode – see "PR behavior" under INSTRUCTIONS)

### Optional Flags
- `--tdd` → TDD_MODE: strict TDD execution mode for quick fixes. Write one test at a time, observe red, drive red→green→refactor, then advance to the next behavior. The TDD canon – Anti-Cheat Invariant, red→green→refactor discipline – is owned by the `andthen:testing` skill; load `/andthen:testing --mode tdd` for canon depth when needed, but the executor remains the test author (canon consultation, not delegation). If `AUTO_MODE` is inherited from an orchestrating caller, honor `--tdd` without confirmation gates.


## INSTRUCTIONS

- Read the Project-Specific Guidelines and Rules section, and relevant project guidelines, before starting.
- **Autonomously and iteratively** implement with comprehensive verification
- **Iterate** until all requirements met, no defects remain, all reviews pass
- Use GitHub CLI (`gh`) for GitHub operations
- **PR behavior**: `--issue` auto-creates a PR (opt out with `--no-pr`); inline spec does not create a PR (opt in with `--pr`)
- **Anti-rationalization** – if you feel tempted to skip tests, defer verification, or widen scope, reject these common rationalizations:
  - "This is too small for tests" – small work still needs verification; a short proof is enough, none is not.
  - "I'll just fix this adjacent issue too" – scope creep hides regressions and muddies diffs.
  - "I'll verify after the next change" – verification is cheapest before more work builds on a bad assumption.
  - "I'll report this complete with a caveat" – broken is not Done. Finish it or surface a real blocker.


## GOTCHAS
- Skipping verification after implementation – always run tests/build
- Scope creep: implementing more than was asked
- When stuck, emit named output blocks per [`execution-named-blocks.md`](${CLAUDE_PLUGIN_ROOT}/references/execution-named-blocks.md): `CONFUSION:` → `-> Which approach?`, `NOTICED BUT NOT TOUCHING:` → `-> Want me to create tasks?`, `MISSING REQUIREMENT:` → `-> Which behavior?`. Under `AUTO_MODE`, see the reference's AUTO_MODE Override section.


## WORKFLOW

### Phase 1: Analysis

#### 1.1. Parse Input & Get Requirements

**If `--issue` flag present:**
1. Extract the issue number and fetch the body with `gh issue view <number>`. Use the body content as the implementation scope – a raw bug report, a structured fix plan from `triage --to-issue`, or anything in between, all read as prose.
2. **Scope guard**: if the body describes a multi-story plan, a PRD, a full FIS, or anything else plainly beyond a small fix, stop and direct the user to the right skill (`andthen:plan` + `andthen:exec-plan` for multi-feature, `andthen:spec` + `andthen:exec-spec` for a single larger feature, `andthen:remediate-findings` for a review report).
3. Set `CREATE_PR=true` (unless `--no-pr` specified). PR will reference the issue with `Closes #<number>`.
4. Create feature branch following project conventions

**Otherwise:** use inline spec from arguments; set `CREATE_PR=true` only if `--pr` flag present.

#### 1.2. Analyze & Plan

1. Understand requirements and scope – interpret as *what* to implement, not *how*. Transform fuzzy asks into verifiable goals before coding:
   - "Fix the bug" → "Write a test that reproduces it; make it pass"
   - "Add validation" → "Write tests for invalid inputs; make them pass"
   - "Refactor X" → "Ensure tests pass before and after"

   Strong success criteria let you loop independently; weak ones ("make it work") force constant clarification.
2. Analyze codebase: `tree -d` and `git ls-files | head -250` for overview; use Explore (or general-purpose) agent for complex exploration
3. Read relevant documentation, including the `Architecture` document (see **Project Document Index**) if it exists and the change touches structural or cross-component code. When external library/API lookup is needed, spawn a sub-agent that consults the project's `## Documentation Lookup Tools` section; Claude Code plugin users may invoke the `andthen:documentation-lookup` agent directly.
4. Break down into manageable tasks and track them

**Gate**: Plan complete, all requirements understood


### Phase 2: Implementation Loop

Execute: Implementation → Verification → Evaluation. Repeat until all requirements met, no defects, all reviews pass.

#### Step 1: Implementation

- Write tests first for any non-trivial branching logic. Apply the **Beyonce Rule** (Bender & Winters, *Software Engineering at Google*, 2020) and the **Anti-Cheat Invariant** (Beck, *Augmented Coding: Beyond the Vibes*) – see `prove-it-pattern.md` and `tdd-discipline.md` for canon. Tests-alongside is acceptable only for purely structural changes (renames, reorganization, declarations); test-after is forbidden.
- When `TDD_MODE=true`, write tests one at a time and drive each red→green→refactor before the next; if `AUTO_MODE` is inherited, honor the flag without confirmation gates.
- **Requirement-Anchored**: every test and motivated code change traces to a requirement from the inline spec or `--issue` body.
- If a discovered gap changes behavior, prompt in interactive mode before expanding scope.
- If running under `AUTO_MODE`, document the conservative interpretation as an `ASSUMPTION` instead of silently widening the ask.
- After 3 stop-and-amend events in a single run, the inline spec is too thin: in interactive mode, surface `CONFUSION:` recommending re-entry via the `andthen:exec-spec` skill with a generated FIS; in `AUTO_MODE`, stop with `BLOCKED:` listing the events and the same recommendation.
- Write code following existing codebase patterns and project guidelines
- Use **sub-agents** for independent tasks to protect the main context window
- Invoke the `andthen:triage` skill for build or configuration issues
- Load the `andthen:testing` skill for canon depth (`--mode tdd` / `--mode prove-it` / `--mode strategy`). The executor remains the test author either way.

#### Step 2: Verification

Run in parallel:

**2.1. Code & Architecture Review** – Invoke the `andthen:review` skill with `--mode code` for static analysis, linting, type checking, code quality, security, architecture.

**2.2. Run Tests** – Execute all tests using the commands from the `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`). Fall back to discovery and language / tech stack conventions only when the document is missing.

**2.3. Visual Validation** (if UI changed) – Follow Visual Validation Workflow from project guidelines; verify via screenshot analysis.

**2.4. Final Quality Assurance** (orchestrator, not delegated) – Review sub-agent results; check for gaps; review implemented code for simplification opportunities.

#### Step 3: Evaluation

- Verify implementation meets all requirements and acceptance criteria
- Mark completed todos
- If issues remain: analyze feedback, update todos, execute another loop

**Gate**: All validations pass – builds correctly, tests pass, no review issues, no regressions.

Include verification evidence: **Build** (exit code/status), **Tests** (pass/fail counts), **Linting/types** (error/warning counts); add **Visual validation** when UI changed, **Runtime** when app was started or flow exercised.


### Phase 3: Completion (conditional)

**Only if `CREATE_PR=true` or `--issue` mode:**

1. Commit with descriptive message (reference issue number if applicable)
2. Push branch to remote
3. Create PR: `gh pr create` with issue link ("Fixes #<number>" if applicable), implementation description, relevant labels
4. Print the PR URL and number

**Gate**: PR created (or changes committed if no PR)


## Post-Completion
If the `State` document (see **Project Document Index**) exists, add a lightweight session note. If the `Learnings` document exists, append brief traps/gotchas. If no `Learnings` document exists and there are noteworthy traps, add a `Learnings` section at the end of the original spec document.
