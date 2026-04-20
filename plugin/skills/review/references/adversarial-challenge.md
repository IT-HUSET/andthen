# Shared Adversarial Challenge Templates

Use this reference when a review skill needs a fresh-context sub-agent to challenge previously collected findings.

## Generic Findings-Challenger Template

Fill every placeholder. Omit `{optional_extra_rules}` unless the calling workflow needs more.

```text
You are {role}.

Read the shared review calibration: {shared_calibration}
Then read the skill-specific calibration: {skill_calibration}

Context: {context_block}

For each finding, evaluate:
{questions}

For each finding, assign a verdict:
{verdicts}

Do NOT add new findings — your job is to filter, not expand.

{optional_extra_rules}

Findings to challenge:
{findings_payload}
```

## Review-Council Variants

### Devil's Advocate
- Reuse the generic template.
- Typical verdicts: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, and optional `DISPUTED`.
- Typical context: council scope plus the full findings set from specialist reviewers.

### Synthesis Challenger
- Reuse the generic template's structure, but change the instructions from per-finding filtering to holistic synthesis.
- Typical questions: severity consistency, merged systemic issues, missed patterns, false positives in context, and overall assessment accuracy.
- Only allow adding new findings when the workflow explicitly expects systemic synthesis.
