# Self-Review

The rubric for the fresh reader an authoring skill spawns over the document it just wrote. It is the only independent reader before the next skill builds on the document, so a gap that survives here is built.

## The contract

**The question.** Where would the document's next reader – the `andthen:plan` skill for a PRD, an unattended executor for a FIS – have to **guess**?

**Fix bar.** Edit only what is mechanical, uniquely determined, and inside the document's stated intent: wording, a broken anchor, a summary line disagreeing with its source row, a missing tag, a conformance slip. Never edit a requirement, decision, scope line, threshold, or anything a Note would ask the owner about.

**Intent anchors.** A finding that an anchor or the document's own record settles or knowingly parks – a Non-Goal, a deferral, an Out-of-Scope line, a `Decisions` entry, the PRD's `Decisions Log`, `Constraints & Assumptions` or `Open Questions` – is closed by citing that line. The citation closes the choice, never a claim about how code or a tool behaves, since recording a claim does not test it. A claim a decision or scenario takes as given is a `blocks: empirical` Note unless a test, run or code line shows it on the path the claim describes. A finding against a stated outcome is a Note whatever its size.

**Traps**: absent sections the project's scale does not need, and brevity read as incompleteness.

**Return.** Return to the caller these blocks and nothing else – no report file, no readiness label:

- `Applied:` – one line per edit, as section → change.
- `Notes:` – each with location, finding, and `blocks: requirements | architecture | empirical | no`. `blocks: no` is an assumption the caller records; anything else is a decision it routes.
- `Attacked:` – what was attacked, in one line, even when nothing survived.
- `Scope trades:` – a FIS review only, in the shape § FIS gives.

## PRD

Look for ambiguity, contradiction between sections, a missing unhappy path, and **undefined behavior** – a stated capability whose result is unstated for an input the user flows reach. Skip what the author's validation already checked: section completeness, testable criteria, Success Metric shape, and problem-solution fit.

**Product document** – its **Non-Goals** and **Proportionality** facts. A requirement re-litigating a Non-Goal, or sized past what the stage facts carry, is a Note naming the anchor (`flagged: exceeds stage prototype in docs/PRODUCT.md`). Absent or `unknown` facts are no licence to size against imagined scale.

## FIS

Apply the authoring guidelines' *Self-Check*, *Plan-Spec Alignment Check*, and *Reverse Coverage Check*, and confirm the `Required Context` anchors resolve per *Consuming Upstream Context*. Phantom scope is a `PHANTOM_SCOPE` Note, never removed.

With no Architecture or Decisions baseline behind it, an architectural prescription needs code-pattern evidence or reads as an assumption.

**Scope trades.** The Architecture Decision's `**Why this over the floor**:` line says which requirement clause is buying the design. For each component the floor would not carry, return one Note naming that clause, the floor, the narrower reading that would drop it, and what the Target User loses against the Desired Outcome. "The design could be simpler" is not one: it gives the owner nothing to decide.

## Bundle

A plan bundle is reviewed as one document set: apply § FIS to each FIS, then the three checks no single document shows.

- **Inter-story coherence** – overlapping scope, contradictory ADR choices, inconsistent naming, and dependency gaps between `plan.json`'s `dependsOn` and FIS task order.
- **Seams and chains** – an output one story needs that another's spec never produces. For each multi-step flow in the source, compose every scenario's title and GWT in flow order and check that each leg's output satisfies the next precondition, naming handoff artifacts and flagging orphan outputs or unsourced inputs. Inspect Proof only to verify an articulated leg, never to fill a semantic gap.
- **Source → FIS traceability** – every story scope, Binding Constraint, and source acceptance criterion covered by ≥1 scenario or criterion.

The return is the bundle's coverage proof. To the blocks above it adds a **per-FIS roster**: one line per FIS naming fixes applied, Notes open, and any `PHANTOM_SCOPE`. The cross-cutting `Notes:`, `Scope trades:`, and `Attacked:` each name the stories they hold.
