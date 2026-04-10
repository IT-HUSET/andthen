# Shared Review Council Reviewer Roster

Choose 5-7 reviewers from this roster based on scope analysis.

## Available Reviewers

### Product & Requirements
- **Product Manager** – Feature alignment, user value, requirements match, scope creep, business logic correctness
- **Requirements Analyst** – Acceptance criteria verification, edge case coverage, spec compliance, completeness

### Technical Specialists
- **Security Sentinel** – Auth, XSS, CSRF, injection, secrets, input validation, OWASP Top 10, trust boundaries. Should run Semgrep scan (MCP `security_check` tool or CLI `semgrep scan --config auto --json`) on changed files if available, and incorporate findings into review.
- **Performance Oracle** – Query optimization, N+1, algorithmic complexity, caching, bundle size, rendering
- **Architecture Strategist** – SOLID principles, coupling/cohesion, patterns, abstractions, maintainability
- **Database Specialist** – Schema design, migrations, indexes, constraints, data integrity, query performance
- **API Designer** – API contracts, versioning, backwards compatibility, REST/GraphQL best practices
- **Frontend Specialist** – Component design, state management, hooks, rendering, bundle optimization
- **Backend Specialist** – Business logic, error handling, data flow, service integration

### Quality & Experience
- **UX/Accessibility Advocate** – Usability, error states, WCAG compliance, keyboard nav, responsive design
- **Test Strategist** – Test coverage, test quality, missing cases, test maintainability, integration tests
- **Code Maintainer** – Long-term maintainability, documentation, tech debt, onboarding, code clarity
- **Content Designer** – Prompt quality (clarity, structure, tokens), user-facing text (error messages, docs, UI copy), technical writing, tone consistency

## Always Include
- **Devil's Advocate** – Challenges all findings during initial review, filters false positives, forces validation through debate
- **Synthesis Challenger** – Reviews after all debates, challenges final conclusions, ensures consistency, validates severity ratings, and acts as the quality gate

## Selection Examples
- **Product feature**: Product Manager, Requirements Analyst, Security Sentinel, Content Designer, Devil's Advocate, Synthesis Challenger
- **Backend API changes**: Security Sentinel, Performance Oracle, API Designer, Backend Specialist, Devil's Advocate, Synthesis Challenger
- **Frontend UI update**: UX/Accessibility Advocate, Performance Oracle, Frontend Specialist, Architecture Strategist, Devil's Advocate, Synthesis Challenger
- **Infrastructure/config**: Security Sentinel, Architecture Strategist, Code Maintainer, Devil's Advocate, Synthesis Challenger
