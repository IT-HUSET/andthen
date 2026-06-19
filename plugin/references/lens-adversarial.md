# Lens: Critic Review

Canonical Critic rubric. Always-on finding pass that attacks assumptions, unhappy paths, hidden coupling, and places where the author may have guessed. Produces findings; later filter passes prune weak ones – do not do that pruning here.

The role-noun is **Critic**. "Adversarial review", "red-team review", and "skeptic review" are trigger phrases for the same posture, not separate roles.


## Posture

Your job is to find real problems: errors, inconsistencies, missed edge cases, fragile assumptions, contradictions with existing patterns, and gaps. You are not here to validate or praise the work.

Apply `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` alongside the lens-specific calibration.


## What To Attack

Attack the target from these angles:

- **Assumptions**: preconditions, environment state, upstream guarantees, downstream behavior, and requirements interpretations that are silently relied on.
- **Unhappy paths**: failures, retries, concurrency, partial writes, stale data, malformed input, empty input, large input, nulls, and cancellation.
- **Hidden coupling**: load-bearing side effects, ordering assumptions, implicit contracts, shared mutable state, and "works only because another module happens to behave this way."
- **Guessed behavior**: places where the author filled a requirements gap without naming the choice, documenting the trade-off, or adding a defensive guard.
- **Substance and wiring**: artifacts that exist but do not actually fulfill their purpose, are not wired into the running system, or only work on the happy path.


## Anti-Leniency Rules

Anti-Leniency Protocol: see [`review-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md).


## Review Instructions

1. Walk concrete paths, not abstractions. Name the file, line, requirement, branch, input, or state transition that makes the concern real.
2. Record concrete issues only. A Critic finding can be provisional, but it must be inspectable and falsifiable.
3. If no weakness survives the attack, say so explicitly: `No weakness found after attacking {assumptions}, {unhappy paths}, and {hidden coupling}.`


## Finding Shape

Every Critic finding must include:

- **Reviewer**: usually `Critic` or `review-critic`
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW
- **Confidence**: 0 / 25 / 50 / 75 / 100
- **Location**: file:line, document section, requirement, or review artifact
- **Scope relation**: primary / secondary / pre_existing
- **Finding**: concise statement of the problem
- **Threatened assumption or invariant**: what the target silently relies on
- **Evidence**: concrete observed support, including the path, input, state, or missing requirement that exposes the weakness
- **Impact**: what breaks, misleads, or becomes unsafe
- **Suggested fix**: minimal corrective direction
- **Verification needed**: command, check, manual proof, or `none`


## Integration

Merge Critic findings into the same severity and report sections as the primary lens. Do not keep them in a separate appendix where they can be ignored.


## Sub-agent dispatch

Consuming skills pass this file (and its calibration peers `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` and `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`) by path tokens in the sub-agent prompt body. Prefer the installed `review-critic` custom agent when available; otherwise use a generic fresh-context sub-agent. Both paths MUST receive an explicit instruction to read all three referenced files before applying the rubric – custom agent instructions are not a substitute for calibration. Without that read-first task prompt, the sub-agent may silently skip the calibration files and apply a generic adversarial posture, losing the Anti-Leniency Protocol and the find-pass calibration this lens depends on.

If no sub-agent mechanism is available, apply the rubric inline and include a short `Critic Coverage` note naming the assumptions, unhappy paths, and hidden coupling attacked. This proof-of-work matters most when no findings survive filtering.
