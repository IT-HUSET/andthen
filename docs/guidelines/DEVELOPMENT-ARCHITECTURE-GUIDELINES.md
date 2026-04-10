# Development and Architecture Guidelines

These guidelines supplement — not restate — standard engineering principles. Apply SOLID, DRY, KISS, and YAGNI by default. These rules address architectural judgment and project-specific standards.


## Architecture Decision-Making

### CUPID Properties
Evaluate architecture using [CUPID](https://cupid.dev/):
- **Composable**: Clear contracts, minimal coupling, framework-agnostic where possible
- **Unix Philosophy**: Each component does one thing well with clear boundaries
- **Predictable**: Consistent behavior, defined failure modes, observable state
- **Idiomatic**: Leverage familiar patterns and conventions; reduce cognitive load
- **Domain-Aligned**: Structure reflects business domains, not just technical layers

### Domain-Driven Design
- Model business concepts directly in code using ubiquitous language
- Split complex domains into bounded contexts with clear boundaries
- Keep domain logic free of infrastructure concerns (DB, UI, frameworks)
- Maintain `UBIQUITOUS_LANGUAGE.md` as the terminology source of truth
- Qualify ambiguous terms by bounded context (e.g., `BillingAccount` vs `UserAccount`)

### Scalability and Resilience
- Prefer stateless services, horizontal scaling, and caching
- Design for failure: circuit breakers, retries with backoff, bulkheads
- Contain blast radius — one component's failure must not cascade


## Coding Standards

- Use the simplest solution that meets the requirements
- Check for existing similar functionality before writing new code
- Write tests for critical paths; prefer TDD. Temporary tests during implementation are fine if removed after
- Keep source files focused on a single concern
- Document only the "why" — never the obvious "what"
- Use latest stable versions of frameworks and libraries
- Never overwrite `.env` files without explicit confirmation


## Workflow

- Work in increments: break tasks into smaller, verifiable steps
- Validate understanding before implementation — re-read requirements, confirm assumptions
- Use up-to-date documentation (Context7 MCP) for API references
- Delegate complex subtasks to sub-agents; main agent orchestrates
- Update README.md only when features, dependencies, or setup steps change

### Documentation Source Authority

When researching APIs, libraries, or frameworks, prioritize sources in this order:
1. **Official documentation** (react.dev, docs.djangoproject.com, developer.apple.com, etc.)
2. **Official blogs and changelogs** (framework release notes, migration guides)
3. **Web standards references** (MDN, web.dev, language specs)
4. **Compatibility references** (caniuse.com, platform support matrices)

**Do not rely on**: Stack Overflow answers, blog tutorials, AI-generated summaries, or model training data recall — these may reflect outdated APIs, deprecated patterns, or incorrect usage. When in doubt, verify against the official source.


## Visual UI Validation

UI features require visual validation — code review alone is insufficient:
- Capture screenshots across target devices and orientations
- Verify touch targets, theme consistency, and responsive behavior
- Use the `ui-ux-designer` agent (validation mode) for systematic checks


## Critical Prohibitions

- **NEVER** create duplicate files with version suffixes (`file_v2.xyz`, `file_new.xyz`)
- **NEVER** modify core frameworks without explicit instruction
- **NEVER** create a branch unless explicitly instructed
- **NEVER** use `git rebase --skip` — causes data loss; ask the user for help with rebase conflicts
- Avoid major architectural changes to working features unless explicitly instructed
