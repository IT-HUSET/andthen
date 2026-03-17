# Domain Language Review Checklist

> Validates that code uses consistent domain terminology aligned with the project's Ubiquitous Language glossary (`UBIQUITOUS_LANGUAGE.md`).
>
> **Skip** when: No `UBIQUITOUS_LANGUAGE.md` exists, the project has no significant domain complexity, or changes are purely infrastructure/tooling.


## Pre-Review

- [ ] Read `UBIQUITOUS_LANGUAGE.md` (if it exists) to understand canonical terms
- [ ] Identify which bounded contexts are affected by the changes


## Terminology Consistency

- [ ] **Canonical terms used**: New code uses terms from the glossary, not listed synonyms
- [ ] **No terminology drift**: Same concept isn't called different names across files/modules
- [ ] **Bounded context boundaries respected**: Terms aren't used outside their defined context
- [ ] **No ambiguous naming**: Variables/classes don't use overloaded terms without context qualification


## Domain Model Alignment

- [ ] **Entities named correctly**: Domain entities match glossary definitions
- [ ] **Actions use domain verbs**: Methods/functions use domain action terms (e.g., `approve()` not `setStatusApproved()`)
- [ ] **States match domain states**: Enums/constants use domain state names from the glossary


## New Term Detection

- [ ] **New domain concepts identified**: If the code introduces concepts not in the glossary, flag for glossary update
- [ ] **No ad-hoc abbreviations**: New terms use full, descriptive domain language (not cryptic shorthand)


## Issue Classification

### CRITICAL
- Domain term used with wrong meaning (e.g., "Tenant" used to mean "User")
- Bounded context violation that could cause confusion across teams

### HIGH
- Synonym used instead of canonical term (e.g., "client" instead of "Customer")
- Inconsistent naming across related files (same concept, different names)

### SUGGESTIONS
- Opportunity to improve naming clarity
- New concept that should be added to glossary
