```
Read all three references before applying the rubric:
- ${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md – Critic posture, what to attack, Finding Shape
- ${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md – find-pass calibration and contrastive examples
- ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md – Anti-Leniency Protocol

Also read the Project Rules Context and Intent Context (if present) below before running the rubric and the Guardrails pass; treat them as the evidence sets for project rules and for feature/product intent respectively.

Apply the Critic posture to the change set below.

Also run a **Guardrails pass**: enumerate project rules, guardrails, principles and guidelines from your context (as defined in `CLAUDE.md` / `AGENTS.md` and other referenced files); filter to those a diff can verify (skip process-only rules); for each applicable rule, check the change set and report violations as findings with the rule cited by source (file and section). Report `Guardrails Coverage: N checked, M findings` alongside the Critic findings.

Use the Intent Context to sharpen, not soften, the find pass: gaps between Expected Outcomes and the change set are Critic findings; behavior outside the stated Intent or contradicting a Non-Goal is a Critic finding even when the code "works". Do not pre-filter findings against the Intent here – the Phase 4 routing gate handles dismissal and Fix/Note routing.

## Context
{what was done and why – brief description of the task/goal}

## Review Lens
{applicable lens from classification step}

## Project Rules Context
{source-path-labeled rule / guardrail / guideline excerpts collected by the outer skill}

## Intent Context
{source-path-labeled Intent / Expected Outcomes / Non-Goals excerpts; omit the section entirely if no governing artifact was found}

## Changes to Review
{the change set – diffs, file contents, or artifact content}

## Output

Report findings as a concise list using the **Finding Shape** from `lens-adversarial.md`. No preamble, no summary section, no severity table. If no weakness survives the attack, say so explicitly using the wording in that file's Review Instructions. Include the `Guardrails Coverage` line and any guardrail-violation findings (cited by rule source) inline with the rest.
```
