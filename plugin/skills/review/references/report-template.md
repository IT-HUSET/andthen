# Review Report Template

> The one shape every report takes, single lens or chain, written in this order. `{{…}}` is filled in; a `>` note is guidance, never report text. A section marked for a lens appears only when that lens ran; every other section is always present, an empty one stating `None.` – except `## Findings`, whose empty lens states `No findings.` and what was attacked.
>
> Downstream tooling parses the section headings, the finding heading, the field labels as spelled (`**Label**:`, colon outside the bold), the verdict lines, and `## Remediation Status` as the last section, so changing any of those is a breaking change. Their separators are the ASCII ` - `, never an en or em dash, because that is the character the parser matches. Fenced code is never report structure: a heading or field quoted inside a fence is evidence text.

# {{Code|Gap|Security|Outcome|Mixed}} Review: {{feature title}}

**Review mode**: {{code|gap|security|outcome|mixed}}
**Resolved chain**: {{lenses in declared order}}
**Target**: {{plan <plan.json> | story <ID> in <plan.json> | PR <number> | range <base>..<head> | paths <comma-separated>}}
**Revision**: {{short HEAD sha the find-passes read}}{{-dirty when uncommitted changes were in scope}}
**Follows**: {{filename of the most recent earlier report on this target}}

> `Resolved chain` only when the mode is `mixed`; `Follows` only when an earlier report exists, and that report is not edited to point forward. The `andthen:implement-fix` skill later appends a `**Remediated**:` line here; the review never writes one.

## Executive Summary

{{The verdict line exactly as `## Verdict` states it, then two or three sentences: what the findings establish about readiness – for a chain, what they establish jointly, and an evidenced failure pattern stated once with its consequence and the findings that show it.}}

{{Scope, one line. `Intent Context:` its source or `none discoverable`. `Drift Notes:` those recorded, or `none recorded`. On a follow-up, each earlier finding and open FIS observation with its state now – resolved, still open, or regressed.}}

Guardrails Coverage: {{N}} checked, {{M}} findings
Filter summary: {{N}} validated, {{N}} downgraded, {{N}} withdrawn

> Fan-out adds its `Partition strategy:` and `Partition map:` lines here.

## Coverage Matrix

| Surface | Evidence read | Positive proof | Falsifier attempted | Result |
|---|---|---|---|---|
| {{surface}} | {{evidence read}} | {{positive proof}} | {{falsifier attempted}} | {{covered / finding / not reviewed}} |

## Findings

> Numbered 1…N across the whole report, CRITICAL first within each lens. A chain puts each lens under its own `### {{Code|Gap|Security|Outcome}}` subheading in chain order, findings one level deeper at `####`. A defect two lenses surface is one finding, under the strongest framing – the security lens over code – and the other lens carries a plain line naming it, never a second finding block. In the gap, outcome, and security lenses the `Finding` field opens with the lens's category: the failure mode, or the OWASP category and source/sink. Severity lives in the heading only, so a downgrade edits one place. `Class:` and `Routing:` stay backticked – the literal tags the Structured Finding Contract names and the `andthen:implement-fix` skill reads – and appear only inside a finding block, never in a summary, a next step, or a back-reference line.

### Finding {{N}} - {{CRITICAL|HIGH|MEDIUM|LOW}} - {{title}}

- **Reviewer**: {{reviewer}}
- **Confidence**: {{0|25|50|75|100}}
- **Location**: `{{path:line}}`
- **Scope relation**: {{primary|secondary|pre_existing}}
- **Finding**: {{what is wrong}}
- **Threatened assumption or invariant**: {{…}}
- **Evidence**: {{…}}
- **Impact**: {{…}}
- **Suggested fix**: {{…}}
- **Verification needed**: {{…}}
- `Class:` {{code-defect|spec-stale|design-changed|ambiguous-intent}}
- `Routing:` {{Fix|Note}} - {{one-line rationale}}

## Compliance

> Code lens. Guidelines adherence, architecture patterns, security awareness (obvious smells only), UI/UX when applicable – one line each, observations rather than findings.

## Trust-Boundary Map

> Security lens. One line per analyzed flow: source → validation → sink.

## Critic Coverage

{{What each lens's Critic pass attacked – the outcome lens adds personas walked, narrowings hunted, unhappy paths attacked.}}

## Verification Evidence

- {{command or scanner}} – {{result, or why it was skipped or unavailable}}

## Verdict

> The shape per lens, by mode – `review-verdict.md` owns what each label means:
>
> - `code`, `security`, `outcome` – `**Readiness: {{Ready|Needs Fixes|Blocked}}** - {{severity counts}}`
> - `gap` – the dimension table below, then its `**Overall: {{PASS|FAIL}}**` line
> - `mixed` – `**Overall readiness: {{Blocked|FAIL|Needs Fixes|Ready|PASS}}** - {{each lens and its label}}`, the worst label across lenses, then the gap table under a `### Gap` subheading when gap ran; never a second `## Verdict`

> Gap lens only, under `### Gap` in a mixed report:

| Dimension     | Score | Threshold | Status |
|---------------|-------|-----------|--------|
| Functionality | {{X}}/10  | >= 7      | {{PASS/FAIL}} |
| Completeness  | {{X}}/10  | >= 9      | {{PASS/FAIL}} |
| Wiring        | {{X}}/10  | >= 8      | {{PASS/FAIL}} |

**Overall: {{PASS|FAIL}}**

## Next Steps

{{Sequenced actions. Gap: the remediation plan by severity, with dependencies and acceptance criteria. Security: sequenced by exposure. Outcome: one line – the skill, the PRD path, the trigger.}}

> `## Remediation Status` follows, written only by the `andthen:implement-fix` skill, one bullet per finding keyed by its number:
>
> `- **Finding {{N}} - {{title}}** - {{RESOLVED|PARTIALLY RESOLVED|UNRESOLVED|DEFERRED|SURFACED}} - {{evidence}}`
