---
name: e2e-test
description: End-to-end browser testing for web applications. Discovers user journeys, executes interactive browser tests, validates responsive behavior, verifies data persistence, and generates a comprehensive test report. Use when verifying a web app's functionality end-to-end or after significant feature changes.
context: fork
agent: general-purpose
user-invocable: true
---

# E2E Test Skill

Orchestrates comprehensive end-to-end testing of web applications: discovers routes and user journeys via parallel sub-agents, executes browser-based tests, validates responsive behavior, and produces a detailed test report with any bugs found and fixed.


## Variables

_Optional: specific routes, features, or user journeys to focus on (leave blank for full coverage):_
FOCUS: $ARGUMENTS


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards**
- **Fix bugs found during testing** — this skill is not read-only; fix and document issues discovered
- Use the `agent-browser` skill for all browser automation (snapshots, clicks, form fills, screenshots)
- If `agent-browser` is unavailable, warn the user and stop
- Delegate to `andthen:build-troubleshooter` for any server startup failures
- Delegate responsive screenshot analysis to `andthen:visual-validation-specialist`
- Use sub-agents for parallel discovery work


## Workflow

### Phase 1: Pre-flight

1. **Platform check** — confirm macOS, Linux, or WSL; warn and stop on unsupported platforms
2. **Frontend check** — verify a frontend exists (`package.json`, framework config, `index.html`, etc.)
3. **Tool check** — confirm `agent-browser` skill is available; if not, stop with clear instructions
4. **Read guidelines** — read CLAUDE.md and any relevant project guidelines, including any Visual Validation Workflow sections

**Gate**: Environment confirmed suitable for E2E testing


### Phase 2: Parallel Discovery

Launch 3 sub-agents concurrently:

#### Sub-agent A: Application Structure
- Map all routes and pages (static, dynamic, protected)
- Identify authentication and authorization flows
- Document key user journeys and interaction patterns (happy paths + error paths)
- List all forms, modals, and interactive components
- Note third-party integrations (OAuth, payments, file uploads, etc.)

#### Sub-agent B: Data Layer
- Read DB schema (migrations, models, seeds, fixtures)
- Map data flows for each key user journey
- Identify which operations create/read/update/delete data
- Locate any existing test seed data or factories
- Map API endpoints and their expected request/response contracts

#### Sub-agent C: Code & Risk Analysis
- Check `git log --oneline -20` for recently changed files (higher regression risk)
- Flag areas of complexity, known fragility, or TODO/FIXME comments in critical paths
- Identify existing tests and their coverage gaps
- Look for error handling inconsistencies or missing edge case coverage

**Gate**: Discovery complete — all user journeys, data model, and risk areas documented


### Phase 3: Test Planning

Using discovery results:

1. **Define scope** — if `FOCUS` is provided, filter to matching routes/features; otherwise full coverage
2. **Prioritize journeys** by:
   - Business criticality (auth, core CRUD, primary workflows first)
   - Recently changed code (higher regression risk)
   - Known fragility or missing test coverage
3. **Identify test data needs** — note any required setup (seed data, env vars, fixtures)
4. **Define success criteria** for each journey (expected URL, element, message, or DB state)

**Gate**: Ordered journey list with acceptance criteria ready


### Phase 4: Environment Setup

1. Identify the dev server start command (from `package.json` scripts, README, CLAUDE.md)
2. Start the dev server
   - If startup fails, delegate to `andthen:build-troubleshooter` before continuing
3. Confirm the application is accessible (load landing page or health endpoint)
4. Note the base URL for testing

**Gate**: Dev server running and accessible


### Phase 5: Journey Testing

Execute journeys sequentially. For each journey:

#### 5.1 Setup
- Clear auth state (fresh session or explicit logout)
- Prepare any required test data

#### 5.2 Execution (via `agent-browser` skill)
1. Navigate to the journey's starting URL
2. Take an interactive snapshot to identify all clickable/fillable elements
3. Execute journey steps one at a time: navigate, click, fill, submit
4. After each significant step: screenshot current state and verify expected outcome (URL, text, element visibility)
5. On completion: verify final state and check DB/API for data persistence where applicable

#### 5.3 Issue Handling
- Classify failures: **Critical** (flow blocked) / **High** (degraded UX) / **Low** (cosmetic)
- Attempt a fix if the root cause is clear and contained; document fix with root cause
- For complex issues: document steps-to-reproduce + screenshot, then continue to next journey

**Gate**: All prioritized journeys executed, outcomes documented, clear bugs fixed


### Phase 6: Responsive Validation

Delegate to `andthen:visual-validation-specialist` with:
- Pages to test: home, primary feature page, auth page (and any others in `FOCUS`)
- Viewports: mobile (375×812), tablet (768×1024), desktop (1440×900)
- Check for: layout overflow, text truncation, broken flex/grid, inaccessible touch targets, hidden navigation

**Gate**: Responsive validation complete with screenshots


### Phase 7: Cleanup

- Stop the dev server if started by this skill
- Remove test data created during testing if safely identifiable (use seeds/fixtures rollback if available)

**Gate**: Environment restored


## Report

Generate a markdown report:

```markdown
# E2E Test Report — [YYYY-MM-DD]

## Summary
[2-3 sentences: scope, overall result, key findings]

## Test Environment
- Base URL: [url]
- Platform: [platform]
- Focus: [FOCUS value or "Full coverage"]

## Journeys Tested

| Journey | Result | Steps | Issues |
|---------|--------|-------|--------|
| [name]  | ✅/❌  | [n]   | [n]    |

## Issues Found

### Critical (flow-blocking)
[Each: Title — Journey — Steps to reproduce — Expected vs Actual — Screenshot: path]

### High Priority
[Same format]

### Fixed During Testing
[Title — Root cause — Fix applied]

## Responsive Validation
[Summary from visual-validation-specialist, with viewport × page matrix]

## Coverage
- Routes tested: [n] / [total discovered]
- Journeys tested: [n passed] / [n total]
- Viewports validated: mobile, tablet, desktop

## Recommendations
1. [Prioritized action items]
```

Store report at: `<project_root>/.agent_temp/qa/e2e-test-report-<YYYY-MM-DD>.md`

When complete, print the report's **relative path from the project root** (e.g., `.agent_temp/qa/e2e-test-report-2026-03-15.md`) and summarize key findings. Do not use absolute paths.


## Follow-Up Actions

After the report, ask the user if they'd like to:
1. Investigate specific failing journeys in depth
2. Expand coverage to additional routes or edge cases
3. Set up a persistent automated E2E test suite (use `andthen:qa-test-engineer`)
4. Fix any outstanding issues found during testing
