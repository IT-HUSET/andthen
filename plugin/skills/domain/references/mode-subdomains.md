# Domain – Subdomains Mode

Classify the business's subdomains as core, supporting, or generic, and record them in the `Domain Map`'s business half. It writes no terms, because the glossary holds each term once.

## Workflow

### Step 1 – Subdomain Classification
For each capability the scope covers, name the subdomain, classify it as exactly one of core (maximal investment, full tactical DDD) / supporting (fit-for-purpose) / generic (off-the-shelf behind an anticorruption layer), and attach a one-line rationale referencing business differentiation and model complexity. Name what it owns. When the call is genuinely contested (a capability core today but generic in 18 months), plot it on the Core Domain Chart (DDD Crew, Tune) and name both sides for Open Questions; its Subdomains row carries the type it holds today.

Add Relationships (how subdomains relate, in domain language) and a Worked Example (named instances, a scenario across subdomains, and the rules it shows) only when the run has the material.

**Gate**: the classification, confirmed or corrected by the user before Step 2 writes it, because whether a capability sets the business apart is the user's knowledge and the code does not carry it. An unattended run writes nothing: it prints the proposal with each assumption as an `ASSUMPTION:` line.

### Step 2 – Write the Domain Map
Resolve the `Domain Map` location from the **Project Document Index** (default: `docs/DOMAIN-MAP.md`).

- Write Subdomains, Open Questions when Step 1 found a contested call, and Relationships and Worked Example when Step 1 produced them. A missing section this mode owns is added under its own heading.
- Update rows in place, never delete, and leave every section this mode does not own byte-identical, hand-curated ones included.

## Output

Print the `Domain Map` path and the classification as written, or under `--auto` the proposal. Once it is written, the next step is this skill in `--mode contexts` on the same scope.
