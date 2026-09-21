# Review Verdict Model

Unified severity scale and per-mode verdict/readiness definitions for every lens of the `andthen:review` skill.


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

Any dimension below threshold is **FAIL**; all at threshold is **PASS**; no conditional verdicts. In a single-lens gap report the `## Verdict` section is this block – the shape is matched on, so the dimensions, thresholds, and wording stay stable:

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

Severity counts plus a readiness label:

| Readiness | When |
|-----------|------|
| **Ready** | No CRITICAL or HIGH findings; LOW/MEDIUM items are optional polish. |
| **Needs Fixes** | Any HIGH finding, or three or more MEDIUM findings that collectively require rework. |
| **Blocked** | Any CRITICAL finding, or a failing check in verification evidence that is load-bearing for the change (not a pre-existing unrelated failure). |

### Security mode (`--mode security`)

The code-mode scale, so the mixed-mode ladder below covers it without a second vocabulary: LOW/MEDIUM items are hardening and defense-in-depth opportunities, a failing load-bearing security scanner is `Blocked`. Severity is calibrated by exposure tier, so the same defect at different exposure levels can land at different readiness verdicts.

### Outcome mode (`--mode outcome`)

The code-mode scale, severity anchored by the lens's own § Severity. Readiness counts the PRD-side findings that route `Note` too – a need the feature does not meet is not closed by being unfixable in code.

### Mixed mode (a resolved multi-lens set)

Per-lens verdicts in each lens's own label (code/security/outcome the three-level scale; gap PASS/FAIL), and **overall readiness** the **worst** across lenses: `Blocked` / `FAIL` > `Needs Fixes` > `Ready` / `PASS`. They share the report's one `## Verdict` section, the gap block demoted to a `### Gap` subheading of it with its dimensions, thresholds, and overall line otherwise unchanged: a second `## Verdict` heading breaks the shape a reader and an agent both match the verdict on. Each lens's findings stay in their own subsection; a defect surfacing in two lenses (SQLi is both a correctness bug and an injection vulnerability) merges under the strongest framing – the security section, with a back-reference from the code section.
