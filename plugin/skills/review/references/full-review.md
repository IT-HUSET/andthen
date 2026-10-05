# Full Review

**Contents**: Workflow (1. Resolve Scope · 2. Plan Coverage · 3. Run Find-Passes · 4. Filter, Classify, Route) · Output · Follow-up

## Workflow

### 1. Resolve Scope

Build one target map: review target, implementation scope, requirements baseline, and user intent; the resolved lens set and why; the Intent Context source or `none discoverable`; and any recorded Drift Notes from the governing FIS's `## Implementation Observations`.

**Earlier reports and recorded observations are input, never scope.** Read the latest earlier report on this target at the Output destination, `## Remediation Status` included, and each governing FIS's open `## Implementation Observations` items, its open quick-review findings and `NOTICED BUT NOT TOUCHING` among them. The report states whether each finding the earlier report left open is now resolved or still open, and each finding or observation still open enters Step 4 as a finding of this review.

Resolve the lenses by the first rule that applies:

- **Explicit `--mode`**: run those lenses, a chain in declared order for reporting. `mixed` is a resolved lens set, never an explicit value: `code`, `gap`, `security` when its trigger fires, and `outcome` with a PRD baseline (`lens-outcome.md` § Baseline).
- **No `--mode`, but the request names review concerns**: map them to lenses in mention order.
  - `security` – security, vulnerability, authz, injection, secrets
  - `code` – correctness, bug, logic, edge case, docs, README, comments
  - `gap` – spec, requirements, acceptance, "matches the spec", conformance
  - `outcome` – solves the problem, user need, success metrics, product fit

  A concern names what to *check*. A topic noun naming what the target is *about* is not one ("review the docs for the auth feature" → `code`, not `security`).
- **No `--mode` and no named concern**: requirements-vs-implementation fit or a broad audit → `mixed`; a PR, code, or implementation audit with no baseline, a docs-only change set included → `code`. Neighboring requirements docs are context, not a baseline – only the fit question makes them one.

Only the `--mode` flag is explicit. A concern- or signal-derived lens set still gains `security` when a `lens-security.md` escalation trigger fires; under the flag, the code lens flags missed security coverage as a HIGH finding instead.

A requirements document is reviewed where it is written – the `andthen:clarify` and `andthen:plan` skills each close on a self-review – and here only as the baseline `gap` and `outcome` read. A bare PRD, plan, or FIS with nothing implemented against it is routed there.

Stop only when no declared lens can resolve a required target or baseline, an unsafe external action is required, or publication cannot proceed.

**Gate**: target map, lens set, rules/intent context, and recorded drift are explicit.


### 2. Plan Coverage

For every active lens, list the surfaces that must be attacked:

- FIS/PRD/issue claims, Acceptance Scenarios, Structural Criteria, Work Areas, Expected Outcomes, Non-Goals, and explicit deferrals
- Changed implementation/config/test/doc artifacts and their obvious callers/consumers
- Trust boundaries and security-trigger surfaces

For each surface, capture:

- `surface`
- `evidence read`
- `positive proof`
- `falsifier attempted` – the negative/edge/path/state that would prove the artifact does not actually satisfy the claim
- `result` – `covered`, `finding`, or `not reviewed`

`not reviewed` on an in-scope primary surface becomes a finding unless a cited Intent/Non-Goal/deferral or a Review Policy exclusion removes it from scope.

**Test-contract falsification.** When any proof-bearing artifact above changed, ask for each important assertion: “What bad state would still pass?” A missing probe is a finding when it threatens the story intent.

Group falsifiers by threatened invariant and cover relevant equivalence classes together; a later manifestation amends that finding family. Before bespoke harnesses or adjacent tracing, anchor a candidate to Intent, a Project Rule, a documented/public input contract, or a causal regression. Otherwise give it one bounded inspection, then route it `Note`.

Slice the plan into partitions per `large-diff-fanout.md` only when the fan-out trigger fires, because each partition costs about one full review:

- **Large surface** – ≥20 changed files, ≥1000 changed LOC excluding generated/vendor/lockfile noise, or 3+ top-level packages/modules/app entry points.
- The caller asked for a partitioned review explicitly.

Fan-out is the skill's one automatic cost multiplier, so it fires on surface size alone, never on phrasing. A caller who asks to keep it inline suppresses it, and the report line is contract: `Fan-out suppressed; inline review over <N>-file diff`.

**Gate**: coverage plan exists and high-risk surfaces have falsifiers assigned.


### 3. Run Find-Passes

The **lens pass** is the unit of work, and one pass carries every resolved lens. Inside the pass:

1. **The Guardrails check** runs first, once, against diff-verifiable Project Rules Context. Each violation counts toward `Guardrails Coverage: N checked, M findings`; a missing or zeroed line means the check did not run, not that nothing was checked. A **Review Policy** document in that bundle supplies the project's own calibration, per `intent-and-rules-context.md`.
2. **Each lens** runs against the coverage plan, in the Critic posture.
3. **`refactor-invariants.md`** runs its triggered checks when a deletion, rename, relocation, cache, codegen, schema, or parameter-threading trigger fires.

Below Step 2's fan-out trigger the whole run is one pass, and a chain's pass is always a reviewer subagent carrying every lens: those rubrics and calibrations are the read-set that would crowd out the filtering, judgment, and report this session still owes. Above it, run one subagent per partition per `large-diff-fanout.md`, then its boundary pass, inline or as one final subagent on a very large diff.

**Gate**: the Guardrails check, every resolved lens with its Critic posture, the triggered refactor-invariant checks, and any partition and boundary pass completed, or explicitly marked unavailable with impact.


### 4. Filter, Classify, Route

When lenses report the same gap, or distinct gaps sharing one pattern, link them: one defect is one finding naming each lens, and a shared pattern is stated once, with its consequence and the findings that show it. Every accepted finding carries the full field set plus `Class:` and `Routing:` per `review-calibration.md` § Structured Finding Contract, which owns the field names, the class meanings, and the Fix bar. Routing keys on **fix character, not defect severity**, because without that split every accepted finding flows into `--fix` and marginal observations become edits. Intent anchors route as `intent-and-rules-context.md` says, each decision citing its anchor.

**Gate**: every finding has passed § Findings Filter, and every accepted one is structured, classed, routed, and scored.


## Output

Write one report to the first destination that applies, never into a source tree:

1. `--output-dir`, when given.
2. The spec directory the run is already anchored in – the reviewed document's own, or the one holding the governing FIS or plan Step 1 resolved as Intent Context.
3. `reviews/` under the **Project Document Index** `Agent Temp` location.

Name the file `<feature>-andthen-<suffix>-<agent>-<YYYY-MM-DD>.md`:

- `<feature>` is the name of the spec directory the run resolved, whether or not the report lands there, plus `-<story-id>` lowercased for a story target. With no spec directory, it is your own slug for the target.
- `<agent>` is the executing agent's short name: `claude`, `codex`, else `agent`.
- A colliding name takes `-2`, `-3`, ….
- `<suffix>` comes from this table:

| Resolved lens set | Report suffix | Mode token |
|---|---|---|
| `code` | `code-review` | `code` |
| `gap` | `gap-review` | `gap` |
| `security` | `security-review` | `security` |
| `outcome` | `outcome-review` | `outcome` |
| any chain | `mixed-review` | `mixed` |

Write it from `report-template.md` – header, sections, finding blocks, and verdict line in the template's literal shapes and order – because downstream tooling parses the file by them. Verdict and readiness values come from `review-verdict.md`.

**Gate**: one consolidated parseable result delivered.


## Follow-up

**`--fix`** invokes the `andthen:implement-fix` skill with `<report-path>`, plus `--auto` in an unattended run, and a backlog question it returns ends your output, after any `Next` line. Skip it, stating the reason, only for a clean report, a single-lens gap PASS with no findings, or a report whose every finding is routed Note outside an unattended run. Unattended, that pass is what dispositions the Notes.

**A recurring trap** – a defect class repeated across findings, or a repeat of an existing `Learnings` entry – is appended to the `Learnings` document (**Project Document Index**) under the fitting topic. Where a lint rule or test could catch it, recommend that check.

**On completion**, print the report path relative to the project root, absolute in an unattended run. Then close on one `Next` line for the first case that applies, never a menu: a command prints as `Next (fresh session):`. It is printed, never invoked: the next run is the orchestrator's to spend. A run another skill invoked prints none, because its caller owns the next step.

- **`--fix` fixed a CRITICAL or HIGH finding, or left a Fix finding PARTIALLY RESOLVED or UNRESOLVED** – this skill again on the same target with `--fix`, as a follow-up to `<report-path>`: that one round re-checked each finding, not what its fixes broke, and this session applied them, so the follow-up must not be its own reading.
- **A PRD-side outcome finding** – the `andthen:clarify` skill on the PRD with: `<the listed gaps>`.
- **A reconciliation finding for the `andthen:decide` skill** – that skill on `<report-path>`.
- **Fix-routed findings, without `--fix`** – the `andthen:implement-fix` skill on `<report-path>`.
- **A `plan.json` target ready under `plan-schema.md` § Shipping** – the `andthen:ship` skill on `<plan.json>`.
- **A `plan.json` target not ready under `plan-schema.md` § Shipping because a CRITICAL or HIGH finding is `DEFERRED`** – `Next: blocked –` then each such finding with the blocker its `## Remediation Status` entry names.
- **Otherwise** – no line.
