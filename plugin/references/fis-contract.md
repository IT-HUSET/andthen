# FIS Contract

What a Feature Implementation Specification is: the surfaces it carries, the shapes an executor and a reviewer read, and what proves each one.

A FIS's executor is an unattended agent, so **human interaction is not schedulable work**: no task, scenario, or plan story waits on a person. Decisions a person owns close in Preflight, and human judgment of results follows the run.

## Proof Surfaces

Three surfaces carry acceptance, each in its own role:

- **Acceptance Scenarios** – the behavioral requirements.
- **Structural Criteria** – the non-behavioral ones, proved by task `Verify` lines.
- `### Work Areas` – the forward-coverage anchor. Each component, file, or surface changed maps to ≥1 task or scenario, and one with neither is a forward-coverage gap.

**Criteria are story-scoped.** Each needs a proving `Verify` in *this* FIS.

**In-FIS tie-breaker** – at execution time an ambiguous scenario or task is resolved by its tagged Expected Outcome (behavioral) or the Structural Criterion its `SATISFIES` names (structural).

## Consuming Upstream Context

A reader resolves a `Required Context` path against the repo root, then the FIS directory. Where a reference cannot be found or disambiguated, or conflicts with FIS Intent or Expected Outcomes, the FIS governs and the reader records the reference as `spec-stale`.

## Acceptance Scenario Shape

**Canonical shape** – one top-level bullet whose bold label carries the scenario ID, then `[OC<NN>(,OC<NN>)*]`, then optionally `[runtime]`. Given/When/Then lines and a ``- **Proof**: `<runnable target>` – <state>`` line nest under it. Never use `### S<NN>`: the bullet grammar is the scanned surface.

**Proof-of-Work** – title plus any GWT is the complete articulated contract. Proof is executable evidence and never owns acceptance semantics.

`[OC<NN>]` closes Intent → Outcomes → Scenarios forward. Each task's `SATISFIES` closes Scenarios and Structural Criteria back to the work: every one is named by ≥1 task, and `SATISFIES` is the only link a Structural Criterion has. Upstream acceptance criteria are seeds: each retained seed maps to ≥1 Acceptance Scenario.

## Runnable Proof Forms

Every `Proof` and `Verify` value opens with a backticked target in one of exactly three forms. A form the executing skill cannot act on is an authoring defect: execution derives a runnable proof for it and records the gap.

| form | shape | how it runs |
|---|---|---|
| test | `` `<file>#<test>` `` – `tests.test_orders#Checkout.test_x` | substituted into the `Key Dev Commands` **run one test** row: a dotted module where it writes `{file}.{test}`, a path otherwise |
| command | `` `cmd: <command>` `` | executed as written in the host's shell; exit 0 is the pass. Project toolchain and `git` only (`git grep` to search): a tool or POSIX idiom the host lacks fails for reasons unrelated to the code |
| inspection | `` `inspect: path/to/file:LINE` `` | **not** executable – the FIS declaring this proof needs a reader |

A trailing ` – <assertion>` names what must be true. **Free prose is not a form**: a proof nothing can run is what lets unwired code complete green.

**Tag a scenario or criterion `[runtime]`** in its bold label wherever the outcome is observable only by running something: under load, across a real boundary, at release, or any performance, E2E, browser, or deployment claim. The tag alone decides. A tagged item closes only on something that ran, and execution runs one where the FIS offers only `inspect:`. Anything untagged may close on static evidence.

**Diff-scoped leanness.** Proof/Verify and Structural Criteria never assert absolute file line, word, or match counts (`wc -l`), because unrelated edits invalidate them. Measure leanness on the story diff (`git diff --numstat`, net non-positive shipped files). A context-budget ceiling is not a criterion.

**Proof Binding** – a Proof binds an existing test or bare suite in the test form (a `Verify` may name one its task writes), in one of two states:

- `red at spec time` – new behavior or a bug repro, failing for the scenario contract or expected symptom, with a suite naming the covering failure;
- `green – parity/regression` – behavior-preservation only (ports, refactors, conformance), which cannot prove new behavior.
