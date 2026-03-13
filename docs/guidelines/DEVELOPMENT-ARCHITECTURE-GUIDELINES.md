# Critical Development and Architecture Guidelines and Standards

## Core Development Philosophy

- **Keep It Simple**: Strive for solutions that are as simple as possible but no simpler. Always prefer efficient, **elegant designs** and straightforward solutions over unmotivated complexity, overengineering and speculative "future-proofing" (avoid YAGNI – *You Aren't Gonna Need It*). Simple solutions are easier to understand, maintain, and debug.
- **Single Responsibility & Separation of Concerns**: Each module, class, or service should have one well-defined responsibility. This separation of concerns makes the system easier to reason about and modify. If a component does too many things, consider splitting it up for better focus and maintainability.
- **Loose Coupling & High Cohesion**: Design components to be as **independent (loosely coupled)** as possible while keeping related functionality grouped (high cohesion). Loosely coupled components have minimal knowledge of each other, reducing ripple effects from changes. Highly cohesive components focus on a single task or area of logic, which improves modularity and clarity.
- **Dependency Inversion**: Follow the principle that high-level modules and low-level modules should depend on abstractions, not on each other's concrete implementations. This makes code more flexible and testable. For example, depend on interfaces or abstract classes, allowing implementations to be swapped without changing higher-level logic.
- **DRY (Don't Repeat Yourself)**: Avoid duplicating code or logic. Consolidate common functionality into reusable functions, modules, or services. This reduces maintenance effort and inconsistencies. *However*, balance DRY with simplicity – don't abstract prematurely or create artificial unification that overcomplicates the design.
- **Avoid Premature Optimization**: First ensure the code is **clear and correct**, then optimize for performance where necessary. Do not sacrifice readability for micro-optimizations that aren't proven necessary. Optimize based on evidence (profiling, observed bottlenecks) or well-known performance best practices – otherwise, *you risk adding complexity without benefit*.
- **No Broken Windows**: Fix small problems before they spread. If you notice a bug, poor naming, or messy code ("broken windows"), address it promptly. Keeping the codebase clean and healthy prevents issues from accumulating and sets a standard of quality.

## Architectural Considerations

- **Consider Existing Patterns First**: When designing a solution, check if the problem can be solved with established **design patterns or existing architecture in the project**. Don't reinvent the wheel for problems that have known solutions. Consistency with existing architecture makes the system more uniform and easier to maintain.
- **Evaluate Trade-offs**: For any important architecture decision, weigh multiple approaches and their pros/cons. For example, choosing between a relational database vs. NoSQL, or between a monolith vs. microservices, involves trade-offs in complexity, performance, and team expertise. Make decisions deliberately, aligned with requirements and constraints.
- **Appropriate Service Granularity**: Design modules and services with **cohesive functionality** and the right level of granularity. Each service or component should map to a specific business capability or feature set. Too large (coarse-grained) and the service becomes a **monolith** internally; too small (overly fine-grained) and you get excessive fragmentation and communication overhead. Strike a balance that allows independent development and deployment without creating unnecessary complexity.
- **Modularity and Decoupling**: Break the system into well-defined, self-contained modules. **Modularity** means splitting a large system into smaller parts that can be understood and modified in isolation. Ensure modules communicate through clean interfaces or APIs only. The goal is to minimize the knowledge each part has about the internals of others (decoupling), so that changes in one module have little impact on others.
- Avoid major architectural changes to working features unless explicitly instructed

### Use CUPID for Architectural Decision-Making

CUPID properties (https://cupid.dev/) focus on creating architectures that are "joyful" to work with. CUPID emphasizes properties rather than rigid rules for architectural design.

- **C - Composable**: Components should work together with minimal coupling, using clear contracts. Design system components that harmonize cohesively with minimal dependencies, clear interfaces / API contracts, and framework-agnostic design where possible. Design for reuse and combination of modules.
- **U - Unix Philosophy (Do One Thing Well)**: Each service or component should have a single purpose, a clear boundary, and do its one thing excellently. Apply the Unix philosophy to system boundaries and service design, with appropriate granularity, clear separation between different system concerns, and well-defined system boundaries. Avoid building "kitchen sink" modules.
- **P - Predictable**: The system's behavior should be consistent and unsurprising under various conditions. Define clear failure modes and performance characteristics. Ensure predictable performance characteristics, well-defined failure modes, clear data flow and state management. Observability (logging, monitoring) helps ensure behavior is transparent and debug-friendly.
- **I - Idiomatic**: Leverage familiar design patterns and conventions. Use frameworks and architectural styles that the team (or agent) knows well. Include industry-standard architectural patterns, consistent technology choices across the system, familiar deployment and operational patterns. Consistency and convention-over-configuration reduce cognitive load, helping contributors to quickly understand the system.
- **D - Domain-Aligned**: Align the architecture with the business domain. The system structure should reflect real-world business concepts and boundaries. This often means grouping functionality by **domain** (for example, separate modules/services for Billing, Inventory, User Management, etc.), rather than by technical layers only. Include clear separation of business logic from infrastructure concerns, and alignment with business processes and terminology.

### Scalability and Resilience

- **Design for Scalability**: Build with growth in mind by allowing horizontal scaling. Prefer stateless services, load balancing, and caching.
- **Robustness and Fault Tolerance**: Expect failures and design for graceful degradation. Apply circuit breakers, retries with backoff, failover, redundancy, and fallback paths.
- **Error Isolation**: Contain the blast radius of failures. Use bulkheads and well-defined module boundaries so one failure doesn't spread.
- **Performance and Efficiency**: Use efficient algorithms and data structures, optimize critical paths, reduce unnecessary calls, and cache where appropriate.

### Domain-Driven Design Principles

- **Focus on the Domain**: Model business concepts directly in code.
- **Ubiquitous Language**: Use business terms consistently in code and discussions.
- **Bounded Contexts**: Split complex domains into contexts with clear boundaries.
- **Rich Domain Models**: Capture rules inside entities and value objects. Use aggregates for consistency.
- **Domain Services and Repositories**: Place cross-aggregate logic in services, abstract persistence with repositories.
- **Separate Core from Infrastructure**: Keep domain logic free of database, UI, or framework concerns.

## Coding Guidelines

- Write **clean, understandable code** with descriptive names and consistent style
- Keep functions/classes focused; short and modular is best
- Follow principles like **SOLID** to keep designs flexible and maintainable:
  - **S**ingle Responsibility: Each class should have one reason to change
  - **O**pen/Closed: Open for extension, closed for modification
  - **L**iskov Substitution: Subtypes must be substitutable for their base types
  - **I**nterface Segregation: Prefer specific interfaces over general ones
  - **D**ependency Inversion: Depend on abstractions, not concretions
- Document only when necessary: explain "why," not obvious "what"
- Log significant operations and errors. Handle exceptions consistently
- Use the simplest solution that meets the requirements
- Avoid code duplication - check for existing similar functionality first
- Never overwrite .env files without explicit confirmation
- Make absolutely sure implementations are based on the latest versions of frameworks/libraries
- Write tests for critical functionality; avoid excessive micro-tests that just add to the maintenance burden
- It's ok to write fine-grained temporary "throw-away" tests when implementing features, as long as they are removed afterwards
- Keep source code files focused on a single concern/responsibility
- Keep frameworks/libraries up to date and remove unused dependencies

## Workflow Patterns

- Use **version control** with clear commits. Apply CI/CD pipelines for testing and deployment
- Work in **increments**. Break down tasks into smaller, verifiable steps
- Focus only on code relevant to the task
- Only make changes that are requested or well-understood
- Preferably create tests BEFORE implementation (TDD)
- Break complex tasks into smaller, testable units
- Validate understanding before implementation. Re-read requirements and confirm assumptions
- Always use up-to-date documentation to ensure use of correct APIs
    - Use the `Context7` MCP for looking up API documentation
- Delegate repetitive subtasks to sub-agents or automation
- Update README.md when important/major new features are added, dependencies change, or setup steps are modified
- Keep docs (README, setup, architecture overview) updated but concise

### Use Sub Agents for Complex Tasks

- Proactively delegate as much work as possible to the available sub agents for complex tasks, and let the main claude
  code agent act as an orchestrator.

## Visual UI Feature Requirements

- **CRITICAL**: UI features require visual validation - code implementation alone is insufficient
- For responsive UI, multi-device UI, or visual design changes, **ALWAYS** include:
    - Screenshot capture across target devices and orientations
    - Visual quality assessment and documentation
    - Touch target verification through visual inspection
    - Theme/design authenticity confirmation across screen sizes
- **Use the ui-ux-designer agent (in validation mode)** for systematic validation against baseline references
- Consider creating feature requests for visual validation
- **Remember**: Users experience UI visually, not architecturally

## Documentation Guidelines

- Never document code that is self-explanatory
- Never write full API-level documentation for application code
- For complex or non-obvious code, add concise comments explaining the purpose and logic (but only when needed)

## Dependency Management

- Add dependencies only if necessary and after checking alternatives
- Always use the _latest stable_ versions of dependencies
- Prefer lightweight, well-established libraries
- Regularly audit and update dependencies to mitigate security risks. Audit for vulnerabilities
- Use environment isolation (lockfiles, containers) for consistency
- Document major changes in changelogs
- **NEVER** add dependencies without first establishing a clear need and checking existing alternatives

## DO's and DON'Ts

**DO:**
- Favor clarity over cleverness
- Keep code cohesive and modular
- Use existing utilities instead of reinventing them
- Handle edge cases and errors explicitly

**DON'T:**
- Write spaghetti code or god classes
- Over-engineer or add features "just in case"
- Copy-paste code across the codebase
- Ignore technical debt or code smells
- Modify frameworks/libraries without strong reason

## **COMMON PITFALLS TO AVOID**

- **NEVER** create duplicate files with version numbers or suffixes (e.g., file_v2.xyz, file_new.xyz) when refactoring or improving code
- **NEVER** modify core frameworks without explicit instruction
- **NEVER** add dependencies without checking existing alternatives
- **NEVER** create a new branch unless explicitly instructed to do so
- **ABSOLUTELY FORBIDDEN: NEVER USE `git rebase --skip` EVER** (can cause data loss and repository corruption, ask the user for help if you encounter rebase conflicts)

**Mandatory Reality Check:**
Before implementing ANY feature, ask:

1. **What is the core user need?** (e.g., "validate UI looks right")
2. **What's the minimal solution?** (e.g., "screenshot comparison")
3. **Am I adding enterprise features to a simple app?** (if yes, STOP)
