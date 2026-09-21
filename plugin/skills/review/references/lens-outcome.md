# Lens: Outcome Review

Rubric for validating a finished feature against the problem its PRD set out to solve – built the right thing, where the gap lens proves it was built to its FIS. The FIS is the plan's reading of the PRD, so nothing derived from it counts as evidence here: a scenario proof shows conformance to that reading, and a faithful implementation of a narrowed reading is exactly the defect this lens exists to find.


## Baseline

The PRD – from a plan, the file its `prd` names; otherwise the `prd.md` discovered as Intent Context – plus the Product document's Vision, Value Propositions, and Non-Goals when present. Without a PRD the pass is unavailable: reported as such with its impact in a chain, `BLOCKED: outcome has no PRD baseline` alone.


## Coverage Matrix

One row per Desired Outcome, Target User, User Story, Success Metric, and Non-Goal, in the skill's `surface / evidence read / positive proof / falsifier attempted / result` shape. Positive proof is a **walked path**: the product exercised as that user along the PRD's User Flows – a browser journey, driven by hand or through the `andthen:visual-validation` skill, when the surface is a UI, else the CLI or API driven by hand – never a test the FIS bound. The falsifier is that user's unhappy path: the input they get wrong, the step they skip, the state they cannot recover from, the metric nobody can see.


## Failure Modes

- **Unmet need** – the Desired Outcome is not reachable end-to-end for a Target User, or a User Story cannot be started or finished by the user it names.
- **Narrowed scope** – a PRD requirement the plan or FIS silently reduced ("remote hosts" became "loopback"), or the MVP Boundary shipped as the whole. The `andthen:plan` skill catches this before execution; this is the check after.
- **Unmeasurable metric** – a Success Metric whose `How observed` the built feature does not supply. Before release the bar is observable, never met; a metric only production can settle is a Note naming what would settle it.
- **Non-Goal breached** – the feature does what the PRD or Product document excludes.
- **Surprise** – behavior a reasonable user of that persona would not expect: silent failure, an error state with no way forward, copy that says something else, an operator who cannot tell it worked.

**Critic angles for this lens** – assume the FIS misread the PRD and look for where; find the happy path that ends somewhere the user cannot leave.


## Severity

CRITICAL: a Target User cannot reach the Desired Outcome. HIGH: a User Story unreachable or incomplete, a Success Metric unmeasurable, a Non-Goal breached. MEDIUM: a surprise on a stated path. LOW: polish on a path that works. Severity scales with the users affected, never with the size of the fix.


## Findings Filter Values

Role `Findings Filter reviewing outcome findings`; questions: does the PRD state this need or was it inferred, is the evidence a walked path, does a Non-Goal, Out of Scope item, or deferral cover it, is severity proportional to the users affected?


## Findings Output

Readiness per `review-verdict.md` § Outcome mode. Classes are the Structured Finding Contract's: an implementation short of the PRD is `code-defect`; a PRD the built feature or a recorded decision has overtaken is `spec-stale`; a PRD that never decided is `ambiguous-intent`. PRD-side findings route `Note` and name the `andthen:clarify` skill against the PRD in **Recommended Next Action**; Step 6 owns whether that becomes an offer. `code-defect` takes the normal Fix bar. The report's `<feature>` token is the PRD's feature name (its directory under Specs & Plans); the baseline is a document, so the report may sit beside it.


## Report Sections

```markdown
## Executive Summary
verdict and readiness, the need met or not in one sentence, Findings Filter stats

## Coverage Matrix

## Outcome Findings
per the Structured Finding Contract, grouped by failure mode

## Critic Coverage
(personas walked, narrowings hunted, unhappy paths attacked.)

## Recommended Next Action
one line – the skill, the PRD path, the trigger
```

