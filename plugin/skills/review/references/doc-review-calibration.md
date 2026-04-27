# Document Review Calibration

Domain-specific calibration for reviewing specifications, plans, PRDs, and other documents. Load `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` first for universal calibration principles (anti-leniency protocol, finding quality, over-leniency patterns), then apply the domain-specific calibration below.

> **Core principle**: A document finding is severe when it would cause an implementer to build the wrong thing, miss a critical requirement, or make an irreversible decision based on incomplete information.


## Severity Calibration — Contrastive Examples

Each pair shows what IS and is NOT that severity level. Use these to calibrate your severity assignments.

### Critical

**IS Critical:**
> The spec says "authenticate users" for a multi-tenant SaaS platform but provides no detail on the authentication mechanism, session management, tenant isolation, or authorization model. An implementer would have to guess at every security boundary.

Why: Security-critical requirements with zero implementation guidance in a context where getting it wrong has severe consequences. An implementer could build an insecure system without realizing it.

**IS Critical:**
> The data model section defines a `Transaction` entity with fields `amount`, `currency`, and `status`, but the workflow section describes transactions as having `subtotal`, `tax`, `total`, and `state`. These appear to describe the same concept with conflicting structures and no reconciliation.

Why: Contradictory definitions of a core domain entity. An implementer would build against one section and break the other. This will surface late and be expensive to fix.

**is NOT Critical (common over-escalation):**
> The spec for a developer CLI tool doesn't include a rollback strategy or deployment plan.

Why: A CLI tool distributed via package manager doesn't need a rollback strategy — users install a new version or pin the old one. This is not a gap; it's an inapplicable concern. Flag only if the project's nature actually requires it.

**is NOT Critical:**
> The spec uses "user" in some places and "account" in others but context makes the meaning clear each time.

Why: Terminology inconsistency worth noting (Medium), but if the meaning is unambiguous in context, it won't cause an implementer to build the wrong thing.


### High

**IS High:**
> The spec requires "real-time notifications" but doesn't specify: real-time via what mechanism (WebSocket, SSE, polling)? What events trigger notifications? What's the latency expectation? What happens when the user is offline?

Why: An implementer cannot build this feature without making significant architectural decisions that the spec should have made. Different choices lead to fundamentally different implementations.

**IS High:**
> The acceptance criteria say "users can filter by date range" but the data model has no date field on the entity being filtered, and no section addresses how dates are derived or stored.

Why: The spec promises functionality that its own technical design can't support. An implementer will discover this mismatch during implementation and have to redesign.

**is NOT High (common over-escalation):**
> The spec for an internal admin dashboard doesn't mention accessibility (WCAG) requirements.

Why: For an internal tool used by a small team, accessibility may genuinely not be in scope. Don't project enterprise requirements onto every project. This is Low unless the project's context demands it.

**is NOT High:**
> The spec doesn't specify exact error message wording for validation failures.

Why: Error message copy is a detail that can be decided during implementation without architectural impact. This is Low — a nice-to-have level of specification detail.


### Proportionality Calibration

**IS disproportionate flagging:**
> Reviewing a spec for a simple webhook relay service (receives events, transforms, forwards). The reviewer flags: missing i18n strategy, missing monitoring/alerting plan, missing load testing strategy, missing disaster recovery plan, missing API versioning strategy.

Why this is wrong: A webhook relay is infrastructure glue. It doesn't have a UI (no i18n), its monitoring needs are basic (health check + error rate), and flagging DR/load testing/API versioning for a simple relay is projecting enterprise SaaS concerns onto a utility service.

**IS a proportionate flag for the same project:**
> The webhook relay spec doesn't address retry behavior when the downstream target is unavailable, or what happens to events during an outage.

Why this is correct: Retry and failure handling IS the core complexity of a webhook relay. This is a genuine gap in the document's coverage of its primary concern.


## False Positive Traps

Common patterns that look like document issues but aren't:

1. **Flagging absent sections that aren't relevant to the project.** Example: marking "Missing: Internationalization Strategy" as High for a single-language internal tool. Always ask: "Does this project actually need this?" before flagging absence as a gap.

2. **Demanding implementation-level detail in a high-level document.** Example: flagging a PRD for not specifying database indexes or API response schemas. PRDs define *what*, not *how*. Match your expectations to the document type.

3. **Flagging intentional scope exclusions as gaps.** Example: the spec explicitly says "Push notifications are out of scope for v1" and the reviewer flags "Missing: push notification specification." The spec addressed this — it's a scope decision, not an oversight.

4. **Treating brevity as incompleteness.** Example: flagging a concise, clear requirement ("Users can export data as CSV") as "underspecified" when the implementation path is obvious. Not every requirement needs a paragraph of elaboration.

5. **Projecting a different project's needs.** Example: reviewing a prototype/MVP spec with production-system expectations (HA, multi-region, 99.99% uptime). Calibrate to the project's actual stage and goals.
