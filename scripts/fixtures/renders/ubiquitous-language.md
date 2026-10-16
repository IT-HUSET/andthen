# Ubiquitous Language

> Domain glossary for Session Hardening. Use these exact terms in code, documentation, and discussion; avoid the listed synonyms.
>
> **Glossary and nothing else.** A term earns a row when getting its name wrong causes a defect – ambiguity, schema drift, misrouting. A row is one sentence under 200 characters: what the term is and where it lives. Mechanism, rationale, status, and open questions stay in the document that owns them – point, don't restate. A row that needs more is a spec in a cell.

## Auth

| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| Session | A signed-in identity bound to one hardened cookie. | login, token | Auth |
| Sign-in | Exchanging credentials for a session; the cookie policy applies here. | log-in, authenticate | Auth |

## Audit

| Term | Definition | Avoid (synonyms) | Bounded Context |
|------|-----------|-------------------|-----------------|
| Audit row | One immutable record of a sign-in attempt, success or failure. | log entry | Audit |

## Overloaded Terms

| Term | Context A | Meaning A | Context B | Meaning B |
|------|-----------|-----------|-----------|-----------|
| Event | Auth | A sign-in attempt, successful or not. | Audit | An immutable row in the trail. |
