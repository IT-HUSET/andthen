# FIS Contract

What a Feature Implementation Specification is: the surfaces it carries, the shapes an executor and a reviewer read, and what proves each one. Authoring against it is `fis-authoring-guidelines.md`, which the spec and plan paths load beside this file.

A FIS's executor is an unattended agent, so **human interaction is not schedulable work**: decisions a person owns close – settled or deferred – in Preflight, human judgment of results follows the run. Never author a task, scenario, or plan story that waits on a person. A human gate – in non-proof prose, or a sign-off the source gives a person – is a blocking Note for closure, never swapped for an agent gate: the swap drops the requirement where nobody sees it go.


## Proof Surfaces

Three surfaces carry acceptance, by distinct roles: **Acceptance Scenarios** are the behavioral requirements; **Structural Criteria** the non-behavioral ones, proved by task `Verify` lines; `### Work Areas` the forward-coverage anchor – an inventory of the components, files, and surfaces changed, each mapping to ≥1 implementing task or Acceptance Scenario, and one with neither is a **forward-coverage gap**, distinct from missing-test/missing-feature gaps.

**Outcomes vs. Structural Criteria** – if the user would notice the behavior, it's an Outcome; if they only notice when it breaks, it's a Structural Criterion. **Criteria are story-scoped**: each one needs a proving `Verify` in *this* FIS, so a run-wide heavy check written here – a performance baseline, the full suite green, an E2E journey – drags the whole end-of-run suite into every story. Those belong to the run's final verification; a criterion here names an invariant this story's own diff could break.

**In-FIS tie-breaker** – at execution time an ambiguous scenario or task is resolved by its tagged Expected Outcome (behavioral) or the Structural Criterion its `SATISFIES` names (structural). Write both so they can carry that load: an outcome vague enough to be read two ways forces `CONFUSION:` instead of resolving it.


## Consuming Upstream Context

A cross-document reference is a **trust boundary**, resolved while authoring with an anchor and intent, never a bare "see the plan". The **two-tier model** is what a reader meets: **Required Context**, the load-bearing anchored references the executor reads before implementation, each bullet ``- `path#anchor` – what to learn and why it constrains this FIS``; and **Deeper Context**, supplementary anchored references read on demand in the same shape.

A reader (execution, review, remediation) resolves anchored `Required Context` by probing repo root and FIS directory: one match wins, while zero matches, two distinct ones, or a conflict with FIS Intent/Outcomes is spec-stale `CONFUSION:`. Source-pinned inline fallbacks are authoritative snapshots: source drift is a re-spec finding, never an invitation to rewrite them. Read `Deeper Context` only when load-bearing for a finding; a followed broken Deeper target warns. Absence is valid when no upstream source is load-bearing, and an older FIS that keeps its references under `## References & Constraints` or in prose is read as-is – never require migration.


## Acceptance Scenario Shape

**Canonical shape** – one top-level bullet whose bold label carries the scenario ID, then `[OC<NN>(,OC<NN>)*]`, then optionally `[runtime]`; Given/When/Then lines and a ``- **Proof**: `<runnable target>` – <state>`` line nest under it. Never use `### S<NN>`: the bullet grammar is the scanned surface. Each scenario is articulated at one of three levels:

- **Unbound** – concrete Given/When/Then nested under the bullet.
- **Fully bound** – precise title + Proof, only where the title itself states every acceptance-significant precondition, action, observable outcome, and required mechanism. GWT is present wherever the title cannot carry that contract clearly; the inspected target is evidence, never the contract's only home.
- **Supplemented** – the missing Given/When/Then detail before Proof, never a transcription of the test.


## Runnable Proof Forms

Every `Proof` and `Verify` value opens with a backticked target in one of exactly three forms. A form the executing skill cannot act on is a defect it reports.

| form | shape | how it runs |
|---|---|---|
| test | `` `<file>#<test>` `` – `tests.test_orders#Checkout.test_x` | substituted into the `Key Dev Commands` **run one test** row: a dotted module where it writes `{file}.{test}`, a path otherwise; a `{file}` that resolves to nothing is a proof that cannot run |
| command | `` `cmd: <command>` `` | executed as written; exit 0 is the pass |
| inspection | `` `inspect: path/to/file:LINE` `` | **not** executable – the FIS declaring this proof needs a reader |

A trailing ` – <assertion>` names what must be true. **Free prose is not a form**: a proof nothing can run is what lets unwired code complete green.

Reach for `inspect:` only where nothing executable can observe the outcome (a licence header, a generated file's shape). It certifies **static** criteria only. **Tag a scenario or criterion `[runtime]`** in its bold label wherever the outcome is observable only by running something – under load, across a real boundary, at release, or any performance, E2E, browser, or deployment claim, however its title happens to read. The tag alone decides: a tagged item resting on `inspect:` is a defect execution admission stops, and anything untagged may close on static evidence.

**Diff-scoped leanness.** Proof/Verify and Structural Criteria never assert absolute file line/word/match counts (`wc -l`): unrelated edits invalidate them. Measure leanness on the story diff (`git diff --numstat`, net non-positive shipped files). Context-budget ceilings are not criteria; re-baseline necessary growth with a `reason`.

**Proof Binding** – an existing test or bare suite binds in the test form as ``- **Proof**: `path#test-name` – <state>``, resolved and run before the FIS is finalized. States: `red at spec time` – new behavior or bug repro, failing for the scenario contract or expected symptom, with a suite naming the covering failure; `green – parity/regression` – behavior-preservation only (ports, refactors, conformance), which cannot prove new behavior. Bindings are never aspirational.

**Proof-of-Work**: title plus any GWT is the complete articulated contract; Proof is executable evidence and never owns acceptance semantics. `[OC<NN>]` closes Intent → Outcomes → Scenarios forward; each task's `SATISFIES` closes Scenarios and Structural Criteria back to the work, and is the only link a Structural Criterion has. Upstream acceptance criteria are seeds – each retained seed maps to ≥1 Acceptance Scenario.

**Proof-surface runnability** – every present `Proof` and required `Verify` opens with a *Runnable Proof Form* whose `{file}` exists, and every Acceptance Scenario and Structural Criterion is named by ≥1 task `SATISFIES`. A form-less or unresolvable target is unrunnable; an unnamed scenario or criterion is unbound. Both block closure and elude a fill-only review.
