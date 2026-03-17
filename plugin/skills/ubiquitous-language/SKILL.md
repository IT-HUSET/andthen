---
name: andthen.ubiquitous-language
description: Extract and maintain a domain glossary (UBIQUITOUS_LANGUAGE.md) from codebase, documentation, and conversation. Use when starting a new domain-heavy project, onboarding to an existing codebase, or when terminology drift is suspected.
argument-hint: [Scope or focus area] [--update]
---

# Extract and Maintain Ubiquitous Language

Scan the codebase, documentation, and conversation history to extract domain-relevant terms, resolve ambiguity and synonymy, and produce or update a structured `UBIQUITOUS_LANGUAGE.md` glossary.


## Variables

_Arguments (scope and optional flags):_
ARGUMENTS: $ARGUMENTS

### Parse Arguments
- Extract `--update` flag → UPDATE_MODE (reads existing `UBIQUITOUS_LANGUAGE.md` and incorporates new terms)
- Remaining text → SCOPE (focus area, e.g., "authentication", "billing", or blank for full project)


## Instructions

- **Fully** read and understand the **Workflow Rules, Guardrails and Guidelines** section in CLAUDE.md / AGENTS.md (or system prompt) before starting work, including but not limited to:
  - **Foundational Rules and Guardrails**
  - **Foundational Development Guidelines and Standards** (e.g. Development, Architecture, UI/UX Guidelines etc.)
- **Read-only analysis** — do not modify any source code
- **Domain focus** — extract terms that represent business/domain concepts, not generic programming terms
- **Resolve, don't accumulate** — when two terms mean the same thing, pick one canonical name and list the other as a synonym to avoid


## Workflow

### 1. Gather Context

**1.1** If UPDATE_MODE: read the existing `UBIQUITOUS_LANGUAGE.md` to understand current glossary state.

**1.2** Explore the codebase to identify domain-relevant sources:
- Domain model files (entities, value objects, aggregates, services)
- API endpoints and route definitions
- Database schemas and migrations
- Documentation (README, PRD, specs, architecture docs)
- Test descriptions (often reveal intended behavior in domain terms)

Use Explore sub-agent _(if supported by your coding agent)_ for large codebases.

**1.3** If SCOPE is provided, focus exploration on that area.

**Gate**: Sources identified

### 2. Extract Domain Terms

For each source, extract terms that represent:
- **Entities**: Core business objects (User, Order, Invoice, Subscription)
- **Actions/Processes**: Domain operations (Checkout, Onboard, Reconcile, Provision)
- **States**: Business states (Active, Suspended, Pending Approval, Archived)
- **Rules/Policies**: Business rules (Grace Period, Rate Limit, Retention Policy)
- **Relationships**: Domain relationships (belongs to, manages, subscribes to)

For each term, note:
- Where it appears (file:line references)
- How it's used (entity name, function name, variable, comment)
- Any inconsistencies (same concept, different names across files)

**Gate**: Raw term list compiled

### 3. Resolve Ambiguity and Synonymy

**3.1** Identify synonym clusters — terms that refer to the same concept:
- e.g., "client" vs "customer" vs "user" vs "account holder"
- e.g., "cancel" vs "terminate" vs "deactivate" vs "suspend"

**3.2** For each cluster, pick a **canonical term** based on:
- Which term is most used in the codebase
- Which term best matches domain expert language
- Which term is least ambiguous

**3.3** Identify overloaded terms — same word meaning different things in different contexts:
- e.g., "account" (user account vs billing account vs bank account)
- Assign bounded context qualifiers

**3.4** If UPDATE_MODE: merge new terms with existing glossary, marking changes with `(new)` or `(updated)`.

**Gate**: Terminology resolved, canonical names selected

### 4. Generate Glossary

Output `UBIQUITOUS_LANGUAGE.md` using this structure:

```markdown
# Ubiquitous Language

> Domain glossary for [Project Name]. Canonical terms for use in code, documentation, and team communication.
>
> **Usage**: Use these exact terms in code (class names, variables, functions), documentation, and discussion. Avoid synonyms listed in the "Avoid" column.

## [Domain Cluster: e.g., "Users & Authentication"]

| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| Tenant | An organization-level account that owns resources | company, org, workspace | Multi-tenancy |
| Member | A user belonging to a Tenant | employee, team member, staff | Identity |

## [Domain Cluster: e.g., "Billing"]

| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| Subscription | ... | plan, membership | Billing |

## Overloaded Terms

| Term | Context A | Meaning A | Context B | Meaning B |
|------|-----------|-----------|-----------|-----------|
| Account | Identity | User login credentials | Billing | Payment method |

## Changelog
- [date]: Initial extraction / Updated [terms]
```

Store in project root or as configured in **Project Document Index**.

**Gate**: Glossary generated


### 5. Validation

- [ ] All domain clusters have at least 2 terms
- [ ] No synonym appears as a canonical term elsewhere
- [ ] Overloaded terms are identified with context qualifiers
- [ ] Bounded contexts are meaningful (not just "general")
- [ ] Terms are actionable — a developer can use them to name things


## Output

Save as: `docs/UBIQUITOUS_LANGUAGE.md` _(or as configured in **Project Document Index**)_

When complete, print the output path and suggest:
1. Review the glossary for accuracy with domain experts
2. Run `andthen.ubiquitous-language --update` periodically to keep it current
3. Use `andthen.review-code` to check code against the glossary
