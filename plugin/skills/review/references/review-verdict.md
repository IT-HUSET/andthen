# Review Verdict Model

Unified severity scale and per-mode verdict/readiness definitions used across all `andthen:review` modes (including `--council`) and the peer `andthen:architecture` skill.


## Severity Scale

Four levels, normalised across all modes:

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | Security vulnerabilities, data loss, broken core behavior, contradictory requirements that make implementation impossible, or any issue that blocks shipping. |
| **HIGH** | Significant maintainability, performance, or correctness issues; major missing-requirement or implementation-drift gaps that need resolution before the work is considered done. |
| **MEDIUM** | Non-trivial quality, consistency, or clarity issues worth addressing – will cause rework or confusion if shipped unaddressed, but does not block release on its own. |
| **LOW** | Worthwhile improvements, polish, or cleanup. Safe to defer; address opportunistically. |


## Per-Mode Verdict / Readiness

### Gap mode (`--mode gap`)

**PASS/FAIL verdict is a byte-level compatibility contract.** Downstream skills (`andthen:exec-plan`, `andthen:remediate-findings`) parse this table directly – keep the dimensions, thresholds, and canonical summary block stable.

| Dimension | Question | Threshold |
|-----------|----------|-----------|
| Functionality | Does it work correctly for specified requirements? | >= 7 |
| Completeness | Are there stubs, TODOs, placeholders, or missing features? | >= 9 |
| Wiring | Is everything connected end-to-end? | >= 8 |

- If any dimension is below threshold → **FAIL**
- If all dimensions meet threshold → **PASS**
- No conditional verdicts

Canonical summary block (reproduce verbatim in the report's Executive Summary):

```markdown
## Verdict

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | X/10  | >= 7      | PASS/FAIL |
| Completeness  | X/10  | >= 9      | PASS/FAIL |
| Wiring        | X/10  | >= 8      | PASS/FAIL |

**Overall: PASS / FAIL**
```


### Code mode (`--mode code`)

Severity counts + a readiness label:

| Readiness | When |
|-----------|------|
| **Ready** | No CRITICAL or HIGH findings; LOW/MEDIUM items are optional polish. |
| **Needs Fixes** | Any HIGH finding, or three or more MEDIUM findings that collectively require rework. |
| **Blocked** | Any CRITICAL finding, or a failing check in verification evidence that is load-bearing for the change (not a pre-existing unrelated failure). |

Readiness is a summary – callers still read the severity counts and individual findings.


### Security mode (`--mode security`)

Reuses the code-mode readiness scale (`Ready` / `Needs Fixes` / `Blocked`) so the unified ladder in mixed mode (below) covers it without a separate vocabulary:

| Readiness | When |
|-----------|------|
| **Ready** | No CRITICAL or HIGH findings; LOW/MEDIUM items are hardening / defense-in-depth opportunities. |
| **Needs Fixes** | Any HIGH finding (real exploitation path with weak preconditions), or three or more MEDIUM findings that collectively require rework. |
| **Blocked** | Any CRITICAL finding (actively exploitable on an exposed surface, secret committed, auth bypass), or a failing security scanner check that is load-bearing for the change. |

Severity is calibrated by exposure tier (per `security-review-calibration.md`), so the same defect at different exposure levels can land at different readiness verdicts – that is the lens working as designed, not an inconsistency.


### Doc mode (`--mode doc`)

Readiness label:

| Readiness | When |
|-----------|------|
| **Ready** | No CRITICAL or HIGH findings; no blocking ambiguity. |
| **Needs Minor Updates** | Localised clarity/completeness gaps (typically LOW/MEDIUM) that do not change the document's shape. |
| **Needs Significant Rework** | HIGH findings or structural gaps that would cause an implementer to build the wrong thing. |
| **Not Ready** | CRITICAL findings, or the document is too ambiguous to hand to an implementer. |


### Mixed mode (`--mode mixed`)

Runs the resolved lens chain (subset of {doc, code, security, gap}). Report:
- Per-sub-mode verdicts using each sub-mode's own readiness label (doc: 4-level scale; code/security: 3-level scale; gap: PASS/FAIL)
- **Overall readiness** = **worst** across all lenses: `Not Ready` / `Blocked` / `FAIL` > `Needs Significant Rework` > `Needs Fixes` > `Needs Minor Updates` > `Ready` / `PASS`

> This ladder intentionally merges three readiness vocabularies (doc: `Ready` / `Needs Minor Updates` / `Needs Significant Rework` / `Not Ready`; code & security: `Ready` / `Needs Fixes` / `Blocked`; gap: `PASS` / `FAIL`) into a single precedence order. When comparing across vocabularies, doc `Needs Significant Rework` ranks worse than code `Needs Fixes` because HIGH-severity structural gaps in a document tend to produce more downstream rework than the localised fixes tracked by code `Needs Fixes`. Gap `FAIL` and code/security `Blocked` are equivalent at the top of the ladder – both mean "do not ship."

Keep findings from each sub-pass in distinct subsections. Merge overlapping findings and use the strongest framing as canonical. Security findings often overlap with code-quality findings (e.g. SQLi is both a correctness bug and an injection vuln); when the same defect surfaces in both lenses, keep it in the security section with a back-reference from the code section.


## Publishing

Reports that publish to GitHub as typed artifacts must include the verdict/readiness in the report body so consumers (`andthen:remediate-findings`) can parse it without opening companion files. For gap mode specifically, the canonical PASS/FAIL verdict block above is the authoritative machine-readable surface – other prose summaries are supplementary.
