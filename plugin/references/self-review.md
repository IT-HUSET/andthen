# Self-Review

The rubric for the fresh reader an authoring skill spawns over the document it just wrote – never the author. One pass, applied in place: this is the only independent reader the document gets before the next skill builds on it, so a gap that survives here is built.

## The contract

**Fix bar** – edit only what is mechanical, uniquely determined, and inside the document's stated intent: wording, a broken anchor, a summary line disagreeing with its source row, a missing tag, a conformance slip. Never a requirement, decision, scope line, threshold, or anything a Note would ask the owner about.

**Intent anchors**, supplied by the caller as paths: a finding a Non-Goal, deferral, or Out-of-Scope line covers is dismissed with that citation; one against a stated outcome is a Note whatever its size. Withdraw a candidate only against text that covers it.

**Traps**: absent sections the project's scale does not need; deferrals flagged as gaps; brevity read as incompleteness; conformance slips reported one per instance instead of applied.

**Return** to the caller these blocks, plus any the caller adds, and nothing else – no report file, no readiness label: `Applied:`, one line per edit as section → change; `Notes:`, each with location, finding, and `blocks: requirements | architecture | empirical | no` (`blocks: no` is an assumption the caller records, anything else a decision it routes); `Attacked:`, what was attacked in one line, even when nothing survived. A FIS review adds `Scope trades:` in the shape below.

## PRD

The next reader is a planner, not a stakeholder. Walk the requirements asking where the `andthen:plan` or `andthen:spec` skill would have to **guess**:

- **Ambiguity** – a term, threshold, actor, or state the document uses two ways, or never defines.
- **Contradiction between sections** – a scope line, a metric, and a functional requirement that cannot all hold.
- **Undefined behavior** – a stated capability whose result is unstated for an input the user flows reach.
- **Missing unhappy path** – a requirement with no error, rejection, empty, or expiry state where its user can reach one.

The gaps the interview never asked about are what this pass exists for – not a re-run of the skill's validation step, which already checked template sections, Success Metric shape, and problem-solution fit.

A PRD has no design, so there are no scope trades to offer – pricing a requirement against a floor is the FIS review's, once a design exists.

**Anchors**:

- **Product document** – its **Non-Goals** and **Proportionality** facts, cited the way the interview cites them (`flagged: exceeds stage prototype in docs/PRODUCT.md`). A requirement re-litigating a Non-Goal, or sized past what the stage facts carry, is a Note naming the anchor; absent or `unknown` facts are not licence to size against imagined scale.
- **The PRD's own record** – `Decisions Log`, `Constraints & Assumptions`, `Open Questions`. A concern one of them settles – or knowingly parks – is closed by citation, not re-raised.
- **Summary vs. source** – every `Executive Summary` bullet derives from a canonical row below it, and on conflict the summary is the bug: a mechanical edit, not a Note.

## FIS

Apply the guidelines' *Self-Check*, *Plan-Spec Alignment Check*, and *Reverse Coverage Check* – the question is whether an unattended executor could run this spec and be stopped where it goes wrong: behavior it would have to infer, a term used two ways, a design choice stated as fact. Read every `Proof` and `Verify` against *Runnable Proof Forms*, and confirm the `Required Context` anchors resolve per *Consuming Upstream Context*.

Challenge the FIS's architecture claims. If no Architecture/ADR/Decisions baseline exists, an architectural prescription needs code-pattern evidence or must be framed as an assumption or execution-time discovery, not settled design.

**Scope trades.** The Architecture Decision's `**Why this over the floor**:` line says which requirement clause is buying the design. For each component the floor would not carry, return one Note naming that clause, the floor, the narrower reading that would drop it, and what the Target User loses against the Desired Outcome. Check the `Decisions` document and the Non-Goals first – a trade already settled is closed by citation. Each is an offer to the requirement's owner, never a fix. The shape is the whole value:

- **Is a scope trade**: *FR-3 "exports run against remote hosts" buys the SSH transport, host registry, and retry layer – five of the story's eight tasks. Read as same-network hosts, the existing file copy covers it; lost: off-site exports, which the Desired Outcome does not name.*
- **Is not**: *the design could be simpler.* It gives the owner nothing to decide.

## Bundle

A plan bundle is reviewed as one document set: apply § FIS to each FIS, then the three checks no single document shows.

- **Inter-story coherence** – overlapping scope, duplicate work, contradictory ADR choices, inconsistent naming, and dependency gaps between `plan.json`'s `dependsOn` and FIS task order.
- **Seams and chains** – an output one story needs that another's spec never produces; for each multi-step flow in the source, compose every scenario's title and GWT in flow order and check that each leg's output satisfies the next precondition, naming handoff artifacts and flagging orphan outputs or unsourced inputs. Inspect Proof only to verify an articulated leg, never to fill a semantic gap.
- **Source → FIS traceability** – every story scope, Binding Constraint, and source acceptance criterion covered by ≥1 scenario or criterion; silent narrowing without a scope note is a finding ("remote host support" must not become "always loopback"), and so is FIS scope with no source (`PHANTOM_SCOPE`).

The return is the bundle's coverage proof, and adds to the blocks above a **per-FIS roster**: one line per FIS naming fixes applied, Notes open, any `PHANTOM_SCOPE`, and any `OVERSIZE:` echo. The cross-cutting `Notes:` name the stories each one holds, as do `Scope trades:` and `Attacked:`.
