# Domain – Glossary Mode

Read the codebase, docs, and conversation as source material without modifying them. Write only the `Ubiquitous Language` document.

## Rules

`Product` and `Architecture` are Project Document Index entries.

## Workflow

### 1. Gather context

Read the existing `Ubiquitous Language` document when one exists. Merge into it by default: a full regenerate discards curated terms, so it happens only when the user asks for one.

Explore for domain-relevant sources, focused on `INPUT` when it is given, including the `Product`, `Architecture`, and `Domain Map` documents. On a large codebase, spawn `worker` subagents whose prompts carry the source areas to scan and a read-only scope.

**Gate**: every source area in scope is scanned.

### 2. Extract domain terms

For each source, extract domain terms across the usual DDD categories – entities, actions and processes, states, rules and policies, relationships – never technical jargon (framework terms, library names) that is not domain language. Note every inconsistency: one concept named differently across files.

**Gate**: every source's terms are extracted and every inconsistency is noted.

### 3. Resolve ambiguity and synonymy

- **Synonym clusters** – terms for the same concept get one **canonical term**.
- **Overloaded terms** – one word meaning different things in different contexts, such as "account" (user, billing, or bank account), get bounded-context qualifiers.
- **Merge** new terms into the existing glossary, marking additions `(new)` and changes `(updated)`.

**Gate**: every extracted term sits in one cluster or is marked overloaded, and every Step 2 inconsistency is resolved or listed.

### 4. Write the glossary

Group the `## [Domain Cluster]` headings by the `Domain Map`'s bounded contexts when it has them, and draw the `Bounded Context` values from them, so the glossary and the map stay aligned. Without contexts, group by its subdomains and leave the `Bounded Context` column empty, because a subdomain name there would join terms to a context that does not exist. Without a Domain Map, group by domain theme.

Write each `## Overloaded Terms` context exactly as a cluster heading or `Bounded Context` value spells it, so a reader can join each meaning to its context.

Write the `Ubiquitous Language` document (default `docs/UBIQUITOUS_LANGUAGE.md`) keeping its shape: cluster tables, then `## Overloaded Terms`.

**Gate**: the glossary is written with every cluster table and `## Overloaded Terms`.

## Output

Print the output path.
