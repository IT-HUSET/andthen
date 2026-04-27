# Shared Findings Filter Templates

Use this reference when a review skill needs a fresh-context sub-agent to filter previously collected findings. This pass cannot find new issues; that is the Red-Team Lens's job (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`).

## Generic Findings-Filter Template

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

Do NOT add new findings. Your job is to filter, not expand.

{optional_extra_rules}

Findings to filter:
{findings_payload}
```

## Review-Council Variants

### Devil's Advocate
- Reuse the generic template.
- Typical verdicts: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, and optional `DISPUTED`.
- Typical context: council scope plus the full findings set from specialist reviewers.
- This is a findings-filter role. It pressure-tests the Red-Team and specialist findings for false positives, weak severity, and missing context.

### Synthesis Challenger
- Reuse the generic template's structure, but change the instructions from per-finding filtering to holistic synthesis.
- Typical questions: severity consistency, merged systemic issues, missed patterns, false positives in context, and overall assessment accuracy.
- Do not add new findings. You may merge, split, reframe, downgrade, or withdraw existing findings when that improves accuracy.
