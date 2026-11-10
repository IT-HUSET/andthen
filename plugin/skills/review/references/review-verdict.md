# Review Verdict Model

Unified severity scale and per-mode verdict/readiness definitions for every lens of the `andthen:review` skill; how a verdict renders is `report-template.md`.


## Severity Scale

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | Security vulnerabilities, data loss, broken core behavior, contradictory requirements that make implementation impossible, or any issue that blocks shipping. |
| **HIGH** | Significant maintainability, performance, or correctness issues; major missing-requirement or implementation-drift gaps that need resolution before the work is considered done. |
| **MEDIUM** | Non-trivial quality, consistency, or clarity issues worth addressing – will cause rework or confusion if shipped unaddressed, but does not block release on its own. |
| **LOW** | Worthwhile improvements, polish, or cleanup. Safe to defer; address opportunistically. |


## Per-Mode Verdict / Readiness

### Gap mode (`--mode gap`)

| Dimension | Question | Threshold |
|-----------|----------|-----------|
| Functionality | Does it work correctly for specified requirements? | >= 7 |
| Completeness | Are there stubs, TODOs, placeholders, or missing features? | >= 9 |
| Wiring | Is everything connected end-to-end? | >= 8 |

Any dimension below threshold is **FAIL**; all at threshold is **PASS**; no conditional verdicts.

### Code mode (`--mode code`)

Severity counts plus a readiness verdict:

| Readiness | When |
|-----------|------|
| **PASS** | No CRITICAL or HIGH finding, not three or more MEDIUM that collectively require rework, and no failing check load-bearing for the change; LOW/MEDIUM items are optional polish. |
| **FAIL** | Anything else. Severity and the failing check stay in the findings and the evidence, so the verdict carries no level of its own. |

### Security mode (`--mode security`)

The code-mode scale: LOW/MEDIUM items are hardening and defense-in-depth opportunities, and a failing load-bearing security scanner is `FAIL`.

### Outcome mode (`--mode outcome`)

The code-mode scale, severity anchored by the lens's own § Severity. A PRD-side finding (`spec-stale`, `ambiguous-intent`) counts toward readiness only at CRITICAL or HIGH: below that it asks the user for a PRD decision, which no `--fix` round can make.

### Mixed mode (a resolved multi-lens set)

A PASS or FAIL per lens, and **overall readiness** `FAIL` when any lens fails, else `PASS`.
