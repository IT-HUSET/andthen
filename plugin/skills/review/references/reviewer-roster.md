# Shared Review Council Reviewer Roster

Total council size is 5–7. Three roles are always included; pick 2–4 scope-relevant specialists on top.

## Always Include

The find/filter/synthesize spine of the council:

- **Red-Team Reviewer**: primary finding role that attacks fragile assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring. Applies `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` and `${CLAUDE_PLUGIN_ROOT}/references/red-team-calibration.md`.
- **Devil's Advocate**: findings-filter role that pressure-tests collected findings for false positives and weak severity.
- **Synthesis Challenger**: final filter pass for consistency, overlap, and missed systemic patterns.

## Specialists (pick by scope)

### Product & Requirements
- **Product Manager**: user value, scope fit, business logic, feature intent
- **Requirements Analyst**: acceptance criteria, edge cases, completeness, spec compliance

### Technical
- **Security Sentinel**: auth, validation, trust boundaries, secrets, exploitability
- **Performance Oracle**: latency, query efficiency, rendering cost, scaling risk
- **Architecture Strategist**: coupling, boundaries, abstractions, maintainability
- **Database Specialist**: schema design, migrations, constraints, data integrity
- **API Designer**: contracts, versioning, compatibility, boundary quality
- **Frontend Specialist**: component design, state, rendering, client-side behavior
- **Backend Specialist**: business logic, error handling, integration behavior

### Quality & Experience
- **UX/Accessibility Advocate**: usability, accessibility, error states, responsive quality
- **Test Strategist**: test coverage, missing scenarios, maintainability of tests
- **Code Maintainer**: long-term clarity, documentation, onboarding, technical debt
- **Content Designer**: prompt quality, technical writing, user-facing copy, tone consistency

## Selection Examples

- **Product feature**: Product Manager, Requirements Analyst, Security Sentinel, Content Designer, Red-Team Reviewer, Devil's Advocate, Synthesis Challenger
- **Backend/API work**: Security Sentinel, Performance Oracle, API Designer, Backend Specialist, Red-Team Reviewer, Devil's Advocate, Synthesis Challenger
- **Frontend/UI work**: UX/Accessibility Advocate, Frontend Specialist, Performance Oracle, Architecture Strategist, Red-Team Reviewer, Devil's Advocate, Synthesis Challenger
- **Infrastructure/config** (smaller scope, 5 reviewers): Security Sentinel, Architecture Strategist, Red-Team Reviewer, Devil's Advocate, Synthesis Challenger
