# Lens: Outcome Review

Rubric for validating a finished feature against the problem its PRD set out to solve – built the right thing, where the gap lens proves it was built to its FIS. The FIS is the plan's reading of the PRD, so nothing derived from it counts as evidence here: a scenario proof shows conformance to that reading, and a faithful implementation of a narrowed reading is exactly the defect this lens exists to find.


## Baseline

The PRD – from a plan, the file its `prd` names; otherwise the `prd.md` discovered as Intent Context – plus the Product document's Vision, Value Propositions, and Non-Goals when present. Without a PRD the pass is unavailable. A requirement only `skipped` stories' `sourceRefs` cite was cut from scope by hand: its Coverage Matrix row reads `not reviewed`, naming those stories, and it raises no finding.


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

Readiness per `review-verdict.md` § Outcome mode. Classes are the Structured Finding Contract's: an implementation short of the PRD is `code-defect`; a PRD overtaken by a recorded decision the finding cites is `spec-stale`; a PRD that never decided is `ambiguous-intent`. PRD-side findings route `Note` and name the `andthen:clarify` skill against the PRD with the listed gaps in `## Next Steps`; the review's completion decides whether that becomes its `Next` line. `code-defect` takes the normal Fix bar. The report's `<feature>` token is the PRD's feature name (its directory under Specs & Plans); the baseline is a document, so the report may sit beside it. Its Executive Summary states in one sentence whether the need is met.

