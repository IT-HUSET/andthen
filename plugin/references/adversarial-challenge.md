# Shared Findings Filter Templates

Use this reference when a review skill needs a fresh-context sub-agent to filter previously collected findings. This pass cannot find new issues; that is the Critic Lens's job (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`).

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

**Verdict discipline** — when verdicts include `WITHDRAWN`, withdrawal requires a concrete falsifier of one of these shapes:
- **Observed mitigation in the artifact under review** — for code/security: a guard, escape, or check that demonstrably handles the path the finding names; for docs: text that already addresses what the finding flagged as missing.
- **Explicit upstream citation** — the requirements baseline (mandatory source for gap-review citations — *not* the implementation under review), an authoritative external source (RFC, vendor SDK doc, ADR, standards document), or an established project convention. The citation must be *explicit*, not inferred from silence.
- **Calibration example the finding clearly matches** — a contrastive example in the lens-specific or universal calibration that the finding is patterned on and would be classified the same way.

"Low impact" or "probably fine" is `DOWNGRADED`, not `WITHDRAWN`. The Filter prunes unsupported findings — it does not relabel doubt as dismissal. This floor binds **every variant below** — Devil's Advocate, Synthesis Challenger, and any council-mode debate that withdraws findings — so the merge/reframe license in Synthesis Challenger does not read as a withdrawal-without-falsifier exception. The same floor applies to lens-level inline self-checks that withdraw findings in lieu of running the full filter. Without it, the Filter becomes the place where real findings get talked away — exactly the failure mode `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (*Anti-Leniency Protocol*) is calibrated against.

## Review-Council Variants

### Devil's Advocate
- Reuse the generic template.
- Typical verdicts: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, and optional `DISPUTED`.
- Typical context: council scope plus the full findings set from specialist reviewers.
- This is a findings-filter role. It pressure-tests the Critic and specialist findings for false positives, weak severity, and missing context.

### Synthesis Challenger
- Reuse the generic template's structure, but change the instructions from per-finding filtering to holistic synthesis.
- Typical questions: severity consistency, merged systemic issues, missed patterns, false positives in context, and overall assessment accuracy.
- Do not add new findings. You may merge, split, reframe, downgrade, or withdraw existing findings when that improves accuracy.
