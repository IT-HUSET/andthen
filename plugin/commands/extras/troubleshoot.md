---
description: Systematically identify, diagnose, and fix issues in the current implementation through comprehensive troubleshooting and root cause analysis.
argument-hint: [Scope]
---

# Troubleshoot and Fix Implementation Issues


## Variables

SCOPE: $ARGUMENTS


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- Systematic troubleshooting with multi-layer issue detection
- Root cause analysis using "5 Whys" technique
- Use `andthen:build-troubleshooter` for complex build issues
- Your context will be compacted as needed - continue troubleshooting iterations until resolved
- **IMPORTANT:** *Continue troubleshooting iterations until all critical and high-priority issues are resolved*


## Workflow

### 1. Current State Assessment

**1.1** - Analyze current state of implementation
- Analyse the current ongoing implementation
    - Use commands like `git status --porcelain` to identify changes and understand the current state
    - Use `git log` to review commit history and understand the evolution of the implementation
- Analyse the codebase to properly understand the project structure, relevant files and similar patterns
  - Use commands like `tree -d` and `git ls-files | head -250` to get an overview of the codebase structure

**1.2** - Capture baseline information:
- Document current branch and commit hash
- Note any pending changes or uncommitted work
- Identify scope of components/features that might be affected (from `SCOPE`)
- **Read additional guidelines and documentation** - Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed

**Gate**: Baseline documented

### 2. Multi-Layer Issue Detection

Execute comprehensive diagnostics across all layers using project-specific commands:
- **Build/compilation**: Run build, check for errors, missing imports, type issues
- **Runtime**: Start dev server, test functionality, check logs for errors/warnings
- **Code quality**: Run linting, formatting checks, identify security issues or anti-patterns
- **Tests**: Execute test suites, check coverage, verify no regressions
- **Configuration**: Validate env vars, config files, database connections, external integrations
- **Architecture**: Review component integrations, imports, API endpoints, state management

Document all issues with priority (Critical/High/Medium/Low), location, and error messages.

**Gate**: All issues identified and documented

### 3. Root Cause Analysis and Prioritization

**3.1** - **Categorize and prioritize issues**:
- **Critical**: App doesn't start, major functionality broken, security vulnerabilities
- **High**: Test failures, build warnings, significant performance issues
- **Medium**: Code quality issues, minor functionality problems, documentation gaps
- **Low**: Style inconsistencies, minor optimizations

**3.2** - **Analyze root causes**:
- Use "5 Whys" technique to dig deeper into each issue
- Identify if issues are related or have common underlying causes
- Map issue dependencies (some fixes may resolve multiple problems)
- Document analysis for each significant issue

**3.3** - **Create comprehensive fix plan**:
- **Setup task tracking**: Use task management tools to create prioritized todos for all identified issues
- Group related issues that can be fixed together
- Plan fixes in dependency order (foundational issues first)

**Gate**: Root causes identified, fix plan created

### 4. Systematic Issue Resolution

Execute fixes methodically and autonomously:

#### 4.1 Critical Issue Resolution (First Priority)
- Address any issues preventing application from starting or building
- Fix security vulnerabilities immediately
- Restore any broken core functionality
- **Delegate implementation** to specialized sub-agents as appropriate

#### 4.2 Progressive Fix Implementation
- Work through issues in priority order
- Fix one category at a time to avoid creating new problems
- For each fix:
  - Understand root cause thoroughly before implementing
  - Follow existing patterns and project guidelines strictly
  - Make minimal, surgical changes rather than broad refactoring
  - Test specific fix before moving to next issue

#### 4.3 Validation After Each Fix
- Run relevant tests to verify fix works
- Ensure no new issues were introduced
- Update task tracking with completed fixes
- Document any side effects or additional changes needed

**Gate**: All critical and high-priority issues resolved

### 5. Comprehensive Post-Fix Verification

#### 5.1 Full System Validation
- **Build Verification**: Ensure application builds without errors or warnings (per project guidelines)
- **Runtime Verification**: Start application and verify all major functionality works
- **Test Suite**: Run complete test suite and ensure all tests pass (per project guidelines)
- **Code Quality**: Run linting, formatting, and type checking with zero issues (per project guidelines)

#### 5.2 Integration and End-to-End Testing
- Test critical user workflows end-to-end
- Verify database connectivity and data operations
- Check API endpoints and external service integrations
- Validate responsive design and cross-browser compatibility (if applicable)

#### 5.3 Performance and Security Validation
- Check for performance regressions or new bottlenecks
- Verify security best practices are maintained
- Ensure no sensitive data is exposed or logged
- Run any security scanning tools available

**Always** use **parallel sub-agents** such as `andthen:qa-test-engineer`, `andthen:solution-architect`, `andthen:ui-ux-designer`, `andthen:build-troubleshooter`, and specialized technology agents as needed. For code review, use the `andthen-review-code` skill.

**Gate**: All validations pass - application builds/starts, all tests pass, code quality checks pass, no regressions, security validated.

Include verification evidence in completion summary (as applicable):
- **Build**: exit code or success/failure status
- **Tests**: pass/fail counts (e.g., "42/42 pass")
- **Linting/types**: error and warning counts
- **Visual validation**: screenshot confirming UI matches expectations (if UI)
- **Runtime**: confirmation app starts and key flows work

> *Don't skip this: "the change is simple, it obviously works" is not evidence.
> Code review ≠ running the code. If tests passed before your change, run them again after.*

### 6. Documentation and Prevention

**6.1** - **Document solutions**:
- Record root causes and solutions for significant issues
- Update troubleshooting guides if patterns emerge
- Note any configuration changes or environment setup requirements

**6.2** - **Preventive measures**:
- Identify if any development process improvements could prevent similar issues
- Suggest additional validation steps for future
- Consider if any monitoring or alerting should be added

**Gate**: Documentation complete

### 7. Iteration and Escalation

> **BRIGHT LINE — 3-Fix Stop Condition:**
> If 3 fix attempts targeting the same symptom or root cause have failed, **STOP immediately**.
> Do NOT attempt fix #4. The problem is likely architectural, not tactical.
> Surface the situation to the user with: what you tried, what failed, your hypothesis
> about root cause, and proposed architectural alternatives.

**7.1** - **Verification Loop**:
- If any issues remain unresolved or new issues emerge, start another troubleshooting iteration
- Re-run full detection process to ensure nothing was missed
- **Update task tracking**: Use task management tools to create new todos for remaining issues

**7.2** - **Escalation Criteria** (beyond the 3-Fix Stop Condition):
- If external dependencies or services are broken and need vendor support
- If issues require user input or business decisions
