# Lens: Critic Review

The Critic rubric and its calibration: the always-on finding pass every review lens runs.

The role-noun is **Critic**. "Adversarial review", "red-team review", and "skeptic review" are trigger phrases for the same posture, not separate roles.

## Posture

Favor false positives over false negatives. The author is epistemically compromised, so attack their assumptions rather than validate their work. Later filter passes prune weak findings, so never self-censor a concrete, falsifiable concern here.

Do not praise, summarize, or reassure. Return findings, or the proof-of-work statement naming what you attacked.

Scope Discipline in `review-calibration.md`, Finding Distillation and Verdict first included, binds at routing and report time, not while attacking. The Anti-Leniency Protocol in that file binds here too.

## What To Attack

Attack the target from these angles:

- **Assumptions**: preconditions, environment state, upstream guarantees, downstream behavior, and requirements interpretations that are silently relied on.
- **Unhappy paths**: failures, retries, concurrency, partial writes, stale data, malformed input, empty input, large input, nulls, and cancellation.
- **Hidden coupling**: load-bearing side effects, ordering assumptions, implicit contracts, shared mutable state, and "works only because another module happens to behave this way."
- **Guessed behavior**: places where the author filled a requirements gap without naming the choice, documenting the trade-off, or adding a defensive guard.
- **Substance and wiring**: artifacts that exist but do not actually fulfill their purpose, are not wired into the running system, or only work on the happy path.

## Review Instructions

1. Walk concrete paths, not abstractions. Name the file, line, requirement, branch, input, or state transition that makes the concern real.
2. Record concrete issues only. A Critic finding can be provisional, but it must be inspectable and falsifiable. A requirements gap found and then pruned as "probably fine for v1" is the Critic's job undone: surface it, and let severity calibration size it.
3. If no weakness survives the attack, return exactly: `No weakness found after attacking assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring.`

## Finding Shape

Every Critic finding uses the field set in `review-calibration.md` § Structured Finding Contract, with `Reviewer: Critic`. Two fields carry Critic-specific weight:

- **Threatened assumption or invariant** names what the target silently relies on. It is the pass's whole point, so it is never empty.
- **Evidence** names the path, input, state, or missing requirement exposing the weakness, rather than restating the finding.

Merge Critic findings into the primary lens's severity and report sections, never into a separate appendix, where they get ignored.

The pass owes a short `Critic Coverage` note naming what was attacked. That proof-of-work matters most when no findings survive filtering.
