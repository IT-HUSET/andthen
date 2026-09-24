# FIS Contract

What a Feature Implementation Specification is: the surfaces it carries, the shapes an executor and a reviewer read, and what proves each one. Authoring against it is `fis-authoring-guidelines.md`.

A FIS's executor is an unattended agent, so **human interaction is not schedulable work**: no task, scenario, or plan story waits on a person – decisions a person owns close in Preflight, and human judgment of results follows the run. A human gate the source gives a person – a sign-off, a manual check – is a Preflight question about where the run stops for their look, never swapped for an agent gate, which drops the requirement where nobody sees it go.


## Proof Surfaces

Three surfaces carry acceptance, by distinct roles: **Acceptance Scenarios** are the behavioral requirements; **Structural Criteria** the non-behavioral ones, proved by task `Verify` lines; `### Work Areas` the forward-coverage anchor – each component, file, or surface changed maps to ≥1 task or scenario, and one with neither is a forward-coverage gap.

**Outcomes vs. Structural Criteria** – if the user would notice the behavior, it's an Outcome; if they only notice when it breaks, it's a Structural Criterion. **Criteria are story-scoped**: each needs a proving `Verify` in *this* FIS, so a run-wide heavy check – a performance baseline, the full suite green, an E2E journey – belongs to the run's final verification, not here, where it would drag the end-of-run suite into every story. A criterion names an invariant this story's own diff could break.

**In-FIS tie-breaker** – at execution time an ambiguous scenario or task is resolved by its tagged Expected Outcome (behavioral) or the Structural Criterion its `SATISFIES` names (structural), so write both unambiguous enough to carry that load.


## Consuming Upstream Context

**Required Context** holds the load-bearing cross-document references the executor reads before implementing, each ``- `path#anchor` – why it binds this FIS``, never a bare "see the plan". A reference the executor could skip does not belong in the FIS.

A reader (execution, review, remediation) resolves a `Required Context` path against the repo root, then the FIS directory. One it cannot find or disambiguate, or one conflicting with FIS Intent/Outcomes, never stops a run: the FIS governs, and the reader records the reference as spec-stale for re-spec. Source-pinned inline fallbacks are authoritative snapshots: source drift is a re-spec finding, never an invitation to rewrite them. An older FIS is read as-is, never migrated: references under `## References & Constraints` or in prose count as Required Context, and a `## Deeper Context` section is read only when load-bearing for a finding.


## Acceptance Scenario Shape

**Canonical shape** – one top-level bullet whose bold label carries the scenario ID, then `[OC<NN>(,OC<NN>)*]`, then optionally `[runtime]`; Given/When/Then lines and a ``- **Proof**: `<runnable target>` – <state>`` line nest under it. Never use `### S<NN>`: the bullet grammar is the scanned surface. Each scenario is articulated at one of three levels:

- **Unbound** – concrete Given/When/Then nested under the bullet.
- **Fully bound** – precise title + Proof, only where the title alone states every acceptance-significant precondition, action, observable outcome, and required mechanism.
- **Supplemented** – the missing Given/When/Then detail before Proof, never a transcription of the test.

**Proof-of-Work**: title plus any GWT is the complete articulated contract; Proof is executable evidence and never owns acceptance semantics. `[OC<NN>]` closes Intent → Outcomes → Scenarios forward; each task's `SATISFIES` closes Scenarios and Structural Criteria back to the work, and is the only link a Structural Criterion has. Upstream acceptance criteria are seeds – each retained seed maps to ≥1 Acceptance Scenario.


## Runnable Proof Forms

Every `Proof` and `Verify` value opens with a backticked target in one of exactly three forms. A form the executing skill cannot act on is an authoring defect: execution derives a runnable proof for it and records the gap.

| form | shape | how it runs |
|---|---|---|
| test | `` `<file>#<test>` `` – `tests.test_orders#Checkout.test_x` | substituted into the `Key Dev Commands` **run one test** row: a dotted module where it writes `{file}.{test}`, a path otherwise |
| command | `` `cmd: <command>` `` | executed as written in the host's shell; exit 0 is the pass. Project toolchain and `git` only (`git grep` to search): a tool or POSIX idiom the host lacks fails for reasons unrelated to the code |
| inspection | `` `inspect: path/to/file:LINE` `` | **not** executable – the FIS declaring this proof needs a reader |

A trailing ` – <assertion>` names what must be true. **Free prose is not a form**: a proof nothing can run is what lets unwired code complete green.

Reach for `inspect:` only where nothing executable can observe the outcome (a licence header, a generated file's shape). **Tag a scenario or criterion `[runtime]`** in its bold label wherever the outcome is observable only by running something – under load, across a real boundary, at release, or any performance, E2E, browser, or deployment claim. The tag alone decides: a tagged item closes only on something that ran – execution runs one where the FIS offers only `inspect:` – and anything untagged may close on static evidence.

**Diff-scoped leanness.** Proof/Verify and Structural Criteria never assert absolute file line/word/match counts (`wc -l`): unrelated edits invalidate them. Measure leanness on the story diff (`git diff --numstat`, net non-positive shipped files); a context-budget ceiling is not a criterion.

**Proof Binding** – a Proof binds an existing test or bare suite in the test form, in one of two states: `red at spec time` – new behavior or a bug repro, failing for the scenario contract or expected symptom, with a suite naming the covering failure; `green – parity/regression` – behavior-preservation only (ports, refactors, conformance), which cannot prove new behavior.

**Proof-surface runnability** – every present `Proof` and required `Verify` opens with a *Runnable Proof Form* – `Proof`s bind existing targets, `Verify`s may be task-written – and every Acceptance Scenario and Structural Criterion is named by ≥1 task `SATISFIES`. A form-less or unresolvable target is unrunnable and an unnamed scenario or criterion unbound – authoring defects fixed before hand-off, never a Preflight question.
