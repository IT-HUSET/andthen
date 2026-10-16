# Domain Calibration

Boundary and domain heuristics and misfire traps for the domain modes, applied on top of `review-calibration.md` where the mode loads it.

## Boundary and Domain Calibration

**Bounded contexts** are a linguistic boundary, not a deployment one – a context map applies inside a modular monolith too. One team owns one or more whole contexts, never a fraction of one: a team boundary cutting across a context boundary predicts a distributed monolith. A God-object aggregate at the centre says the context is too broad.

**Integration patterns.** Every pair in a context map names its pattern from the nine – Evans' eight plus Big Ball of Mud as a quarantine wrapper. Move up that list (Partnership, Shared Kernel) when teams are aligned and models stable; move down it (Conformist, Anticorruption Layer, Separate Ways) when teams are distant, models incompatible, or the upstream cannot be negotiated with.

**Aggregates.** An invariant is a rule enforced *at commit*; a rule that only has to hold eventually never justifies widening an aggregate. To test a cluster, list the aggregates one use case modifies and name the invariant forcing them into a single transaction – no invariant, break the cluster. The rules describe a steady state, so a migration step may violate them transiently.

**CQRS** only when read and write shapes genuinely diverge, query load is a real constraint, or different teams own the two paths – never for CRUD.

**Event sourcing** only when audit or temporal queries are first-class, or state is fully derivable from history; schema versioning becomes permanent operational work.

**Ubiquitous language.** Domain class names are the terms an expert uses unprompted; weasel suffixes are the smell (`UserInfo`, `OrderData`, `PaymentManager`, `CustomerEntity`), with infrastructure classes the exception.

**Sizing.**

- Component size within 1–2 standard deviations of the mean (Ford/Richards).
- A cognitive-load ceiling of 2–3 low-complexity domains per team (Team Topologies).
- An owning team past ~5–7 people means the service may be too large.
- One business requirement change should touch exactly one package.
- A barrel exporting more than ~50 symbols means reassess scope.

**Extraction gate** (Newman). No compelling reason, an unclear domain, fewer than ~8 engineers, or no need for independent deployability → stay a modular monolith. Extract only the subsystems that need independent scaling, or the boundaries that need team autonomy (Conway).

## Traps

Check the matching trap before recording a finding: each marks where an anti-pattern's finding stops or a look-alike that is not one.

1. **Premature decomposition** – boundaries redrawn more than twice mean the domain is not understood well enough to split.
2. **False-invariant aggregate** – grouped by navigational convenience; the symptom is that most use cases touch only a subset.
3. **Leaky integration event** – internal aggregate structure published as a public contract, so consumers break on internal refactors. Domain events stay inside their context; integration events are purpose-built, versioned additively, published after persistence via an outbox, and consumed idempotently.
