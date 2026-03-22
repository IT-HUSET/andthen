---
description: Review specifications, plans, PRDs, requirement documents, or other documentation for completeness, clarity, edge cases, and technical accuracy. Generate detailed report with prioritized findings and readiness assessment.
context: fork
agent: general-purpose
user-invocable: true
---

# Review Spec, Plan, Requirements, or Other Documents


Thoroughly review specifications, implementation plans, PRDs, technical designs, requirement documents, or other documents to ensure they are complete, clear, unambiguous, and ready for implementation or distribution.


## VARIABLES

_Path to specific document(s) to review, or additional focus areas (**required**):_
SPEC_PATH_OR_FOCUS: $ARGUMENTS


## INSTRUCTIONS

- **Make sure `SPEC_PATH_OR_FOCUS` is provided** - otherwise **STOP** immediately and ask user for input
- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md (and/or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Read-only review** - No modifications to specs during analysis
- **Be thorough and critical** - Challenge assumptions, find edge cases, identify ambiguities
- **Favor simplicity** - Actively identify over-engineering; recommend simplest solution (KISS, YAGNI, DRY)
- **Proportional review** - Calibrate the depth and expectations of your review to the project's actual scale, stage, and goals. A simple CLI tool, a prototype, or an MVP does not need the same scrutiny as an enterprise SaaS platform. Never recommend patterns, processes, or infrastructure that are disproportionate to the project's scope and ambition. If the document doesn't mention something (e.g. i18n, monitoring, rollback), consider whether it's actually needed before flagging it as missing.
- **The words "spec" and "specification" in this command** refers to any specification, plan, requirement document, PRD, technical design, or other documentation that is the focus of the review


## GOTCHAS
- Reviewing at the wrong level of detail for the document's maturity stage
- Confusing review-doc with review-gap — doc reviews the document, gap reviews implementation


## WORKFLOW

### Phase 1: Discovery and Context

1. **Locate specification documents**
   - If _`SPEC_PATH_OR_FOCUS`_ is provided, review those documents/areas
   - List all documents found and their relationships

2. **Build context**
   - Understand existing patterns, conventions, tech stack
   - Identify problem being solved, success criteria, scope boundaries
   - Note dependencies, constraints, and assumptions
   - **Read additional guidelines and documentation** - Read additional relevant guidelines and documentation (API, guides, reference, etc.) as needed

3. **Understand project scale and vision**
   - Determine the project's nature (CLI tool, library, web app, SaaS, internal tool, prototype, etc.)
   - Determine the project's stage (greenfield, MVP, early product, mature product, etc.)
   - Understand the overall vision and goals — what is the project trying to achieve?
   - Use this understanding to calibrate all subsequent review phases proportionally

**Gate**: All relevant specs identified, context understood, and project scale/vision established


### Phase 2: Completeness Review

Verify specification covers all necessary aspects _(only flag items as missing if they are actually relevant to the project's scale, stage, and goals)_:

1. **Functional requirements** - Features, workflows, use cases, success/error states
2. **Non-functional requirements** - Performance, security, accessibility, i18n, compatibility _(only those relevant to the project)_
3. **Technical specifications** - Data models, APIs, integrations, error handling, monitoring
4. **Edge cases and errors** - Validation rules, timeouts, retries, error messages, boundary conditions
5. **Testing strategy** - Acceptance criteria, test approach, test scenarios
6. **Operations** - Deployment, configuration, monitoring, rollback, maintenance _(only if applicable to the project's stage)_

Document all missing or incomplete areas.

**Gate**: Completeness assessment finished


### Phase 3: Clarity and Ambiguity Review

Identify unclear, ambiguous, or contradictory specifications:

1. **Language precision** - Check for vague terms ("fast", "user-friendly"), conflicting requirements, undefined terms
2. **Implementation clarity** - Verify developers can implement without guessing, acceptance criteria are testable
3. **Missing details** - Find TBD/TODO items, referenced missing documents, unvalidated assumptions
4. **Consistency** - Verify consistency across sections, examples match specs, naming is consistent
   - If the reviewed spec is a FIS (Feature Implementation Specification), ensure the spec follows the format and structure as defined in the `andthen:spec` command
5. **Conciseness and Brevity** - Ensure specs are as brief and concise as possible without losing meaning. Unnecessary prose should be avoided, and code listings should be minimized (prefer using pseudo code when possible)
6. **Maintain Important Details** - Ensure all important and essential details are preserved. Avoid removing or simplifying details that are critical to understanding the specification, such as diagrams, process flows, or complex requirements.


Document all ambiguities and clarity issues.

**Gate**: All ambiguities identified


### Phase 4: Technical Accuracy and Standards

Verify technical solutions use current best practices:

1. **Technology versions** - Check if libraries/frameworks use latest stable versions, identify deprecated APIs
2. **Best practices** - Verify industry standards, security (OWASP), accessibility (WCAG 2.1+), project patterns
3. **Technical feasibility** - Assess if solution is feasible, identify risks, verify performance expectations
4. **Documentation lookup** - Verify use of latest APIs, best practices, deprecations. Perform multiple web searches and use Context7 MCP as needed for different technologies/APIs/topics.


**Gate**: Technical accuracy verified


### Phase 5: Edge Cases and Risk Analysis

Identify missing edge cases and risks:

1. **Edge cases inventory**
   - Empty/maximum states, invalid input, concurrent access
   - Network failures, third-party failures, data migration
   - Browser/platform-specific issues

2. **User journey edge cases** - Unexpected action order, navigation away mid-process, multiple tabs/sessions

3. **Security edge cases** - Malicious input, privilege escalation, injection attacks, data leakage

4. **Risk assessment** - Identify highest risks, potential failures, invalid assumptions, dependency risks

**Gate**: Comprehensive edge case analysis complete


### Phase 6: Scope and Architecture Validation

Ensure scope is well-defined and architecture is sound:

1. **Scope validation**
   - Verify in-scope items are necessary and achievable
   - Confirm out-of-scope items are explicitly stated
   - Identify scope creep risks, phase boundaries
   - Challenge "nice-to-haves" masquerading as requirements

2. **Architecture review** _(calibrate to project scale — skip aspects that are irrelevant to the project's nature and stage)_
   - Use the `andthen:review-code` skill's architectural review guidance
   - Assess and evaluate **only aspects relevant to the project's scale and goals**, such as:
      - Architectural soundness, component separation, separation of concerns
      - Evaluate scalability, performance, maintainability
      - Review integration points, API contracts, data flows
      - Where applicable: CUPID principles, DDD patterns, clean architecture, service architecture
      - Anti-patterns, performance, resilience, security architecture
   - **Do not recommend patterns or architecture disproportionate to the project** — e.g., don't suggest DDD/bounded contexts for a simple library, or microservices for a tool that works fine as a monolith
   - Identify signs of over-engineering, such as:
      - **Unnecessary complexity**: Custom implementations when standard libraries/patterns exist, premature abstractions, overly generic solutions
      - **Premature optimization**: Performance optimizations without measured need, caching/pooling without proven bottlenecks
      - **Excessive layering**: Unnecessary indirection, wrapper classes without clear benefit, over-abstracted interfaces
      - **Feature bloat**: Speculative features for "future flexibility", unused configuration options, gold-plating
      - **Technology overkill**: Complex tools/frameworks when simpler ones suffice, microservices where monolith works, unnecessary dependencies
      - **Pattern misapplication**: Design patterns used without clear need, architecture patterns inappropriate for scale

   For each identified issue, recommend **simplest solution** that meets actual requirements.

**Gate**: Scope and architecture validated, over-engineering identified


### Phase 7: Stakeholder and Success Criteria

Validate stakeholder needs and measurable success criteria:

1. **Stakeholder alignment** - Verify all needs addressed, no conflicting requirements, user perspective represented
2. **Success criteria** - Confirm criteria are specific, measurable, objective, and testable
3. **User experience** - Check UX specification, user journeys, error states, user-centered design

**Gate**: Stakeholder needs and success criteria validated


### Phase 8: Review Report Generation

Generate comprehensive review report with prioritized findings:

1. **Categorize findings** - Critical (must fix before implementation), High (should fix), Medium (can fix during), Low (nice-to-have)
2. **Specific recommendations** - For each issue, provide concrete suggestion with examples and rationale
3. **Risk highlights** - Call out biggest risks and areas likely to cause implementation issues
4. **Readiness assessment** - Overall assessment: Ready / Needs Minor Updates / Needs Significant Rework / Not Ready

**Gate**: Comprehensive review report generated


## REPORT

Your job is *ONLY* to review and generate report. Do *NOT* modify specification documents.

Generate markdown report with:
- **Executive Summary** - What was reviewed, overall assessment, high-level findings, key recommendations
- **Scope and Context** - What spec achieves, scope boundaries, assumptions, context issues
- **Completeness Analysis** - Missing requirements by category, completeness assessment
- **Clarity Issues** - Ambiguous/vague requirements with suggested improvements
- **Technical Accuracy** - Version issues, deprecated approaches, standards compliance, feasibility concerns
- **Edge Cases and Risks** - Missing edge cases by category, security concerns, risk mitigation
- **Architecture Assessment** - Soundness, scalability, maintainability, integration clarity
- **Over-Engineering Analysis** - Unnecessary complexity, premature optimizations, excessive layering, feature bloat, technology overkill, pattern misapplication (with simpler alternatives)
- **Stakeholder Alignment** - Success criteria clarity, stakeholder needs, UX considerations
- **Prioritized Recommendations** - Critical/High/Medium/Low issues with specific suggestions
- **Readiness Assessment** - Can implementation start? What must be fixed? Next steps

**Report file naming:**
- **Agent identifier**: Determine your agent short name (e.g., `claude`, `codex`, `cursor`, `aider`). If uncertain, use `agent`.
- **File collision avoidance**: Before writing, check if the target filename already exists. If it does, append an incrementing suffix: `-2`, `-3`, etc. **Never overwrite existing reports!**

**Report output directory** — resolve in priority order:
1. **Spec directory**: If the document being reviewed lives in a spec/FIS directory (or has an associated spec directory from the Project Document Index), store the report **in that same directory**.
2. **Target directory**: Otherwise, store the report **in the same directory** as the document being reviewed.
3. **Fallback**: Store in `{AGENT_TEMP}/reviews/` where `{AGENT_TEMP}` is the **Agent Temp** path from the Project Document Index (default: `.agent_temp/`).

**Filename**: `<spec-name>-doc-review-<agent>-<YYYY-MM-DD>.md`

When complete, print the report's **relative path from the project root**. Do not use absolute paths.


## FOLLOW-UP ACTIONS

After report, ask user if they'd like to:
1. Update specification based on findings
2. Focus on specific areas for deeper review
3. Proceed to implementation (if ready)
4. Escalate critical issues for clarification
