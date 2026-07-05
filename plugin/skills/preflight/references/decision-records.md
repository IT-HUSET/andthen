# Decision Records, Convergence, and Verdict Semantics

The data model preflight runs on. Detection output is normalized into **decision records**; convergence drives every blocking record to closure; the verdict reports the result in a machine-stable token.


## Decision-record schema

Each detected decision normalizes to a record with these fields:

| Field | Meaning |
|-------|---------|
| `decision_key` | Stable slug naming the decision (e.g. `export-format`, `auth-session-store`). The identity used for cross-story matching and `ops` idempotency. |
| `source` | Where it surfaced: FIS path + section, or the review finding. |
| `altitude` | One of `fis-local` / `project-decision` / `adr` / `requirements`. Drives where the resolution persists. |
| `affected_surface` | The behavior, file, or contract the decision changes. |
| `status` | `open` / `resolved` / `deferred`. |
| `evidence` | One sentence: why this is (or is not) a blocking decision, citing the source that does or does not resolve it. |

`altitude` and persistence destination are 1:1:
- `fis-local` → FIS decision-Note only (`ops update-fis … decision-note`); local/reversible.
- `project-decision` → `docs/DECISIONS.md` **Still Current** note (`ops update-decisions still-current`); long-term-important, non-ADR.
- `adr` → ADR authored and indexed by the `andthen:architecture` skill (`--mode trade-off`); never hand-written.
- `requirements` → not resolved at FIS level; routed to the `andthen:clarify` skill.


## Blocking vs. non-blocking split

A record is **blocking** only when unattended implementation would *fork* on it – the implementer cannot safely pick alone because the choice changes an observable behavior, a persistence location, an architecture-significant structure, or a requirements-altitude question, and **no cited source resolves it**.

Non-blocking (never gates the verdict): mechanical doc defects (typos, broken anchors, stale cross-refs), advisory review Notes, polish, and any decision a cited source (the FIS itself, an existing ADR, `DECISIONS.md`, the PRD) already settles. The blocking-only drill-down demotes these; it does not re-open settled requirements.

The split is the whole point: preflight spends human attention on the few decisions that would otherwise stall an autonomous run, not on a second spec pass.


## Plan-bundle identity matching

For a plan bundle, after each story FIS converges on its own, the cross-story sweep matches records across stories by the composite key `decision_key + altitude + affected_surface`. When two stories carry matching records with **conflicting** `resolved` values, both are reopened as `open` blocking decisions and their stories re-converge before any story status flips to `spec-ready`. Matching records that agree are left alone; the sweep flags contradictions, it does not re-detect.


## Convergence

A target **converges** when no record is left in `open` status and every `resolved` record is **reconciled**: the FIS body states the ratified decision at its affected surfaces (the DECISION NOTE is provenance, not the contract's home), and no resolution contradicts another resolution or the body. An unreconciled or contradicting resolution counts as `open`. Deferral is a convergence outcome only with explicit user sign-off – a punted decision moves to `deferred` and stops counting as blocking; an un-signed-off punt stays `open`. The procedure that reaches this state is the skill's WORKFLOW.


## `Preflight:` verdict semantics

Emit grammar and consumer regex: the SKILL's `Preflight:` verdict-grammar INSTRUCTIONS bullet is the self-contained copy.

- **READY** – zero open blocking decisions. Single FIS fully converged, or every story in a bundle clear. A target with no blocking decisions reaches READY immediately, with no interview.
- **DEFERRED** – converged, but one or more remaining decisions are signed-off deferrals; none still `open`.
- **BLOCKED** – at least one blocking decision is still `open`: a single FIS with an unresolved decision, a bundle with any non-clear story, or an `AUTO_MODE` run that surfaced blocking decisions it could not resolve without an interview.

Precedence for a bundle: any `open` → BLOCKED; else any `deferred` → DEFERRED; else READY.
