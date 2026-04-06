# Review Calibration Reference

Universal calibration principles for all review skills. Load this reference before assigning severity to findings, then load the domain-specific calibration for your review type.

> **Purpose**: Checklists tell you *what* to look for; this reference shows *how rigorously* to look.
> Models trend toward leniency — identifying real issues then rationalizing them away. This reference counteracts that bias.

**Domain-specific calibration** (load after this file):
- Code/implementation review: `code-review-calibration.md` in `review-code/references/`
- Document review (specs, plans, PRDs): `doc-review-calibration.md` in `review-doc/references/`


## Anti-Leniency Protocol

Apply these rules when evaluating findings:

1. **If you identified a problem, it IS a problem.** Do not talk yourself into deciding it "isn't a big deal" or "probably works fine." Your first instinct that something is wrong is usually correct.
2. **"Works on the happy path" is not a pass.** Whether reviewing code or documents — verify edge cases, error paths, boundary conditions, and integration points. A feature that only works in the simplest scenario is incomplete; a spec that only covers the simplest scenario is incomplete.
3. **Substance over surface.** Check that things are actually complete, not just present. A stub that compiles is still a stub. A requirement that says "handle errors appropriately" is still vague. Existence is not sufficiency.
4. **Apply the peer-review standard.** If you would flag this in a review for a team you respect, flag it here. Do not lower your standards because this is an automated review.
5. **Probe deeply, not broadly.** Don't just check that each item has a corresponding artifact. Verify that the artifact actually fulfills its purpose — that implementations work end-to-end, that specifications are actually implementable, that requirements are actually testable.
6. **Do not dismiss findings you've already identified.** If your analysis found an issue, record it at the severity it deserves. The remediation plan can deprioritize it — your job is accurate identification, not triage.


## Over-Lenient Review Calibration

The most dangerous evaluator failure is identifying real issues then approving anyway. Study this example:

**Over-lenient review that wrongly approved (annotated):**
> Review of a checkout flow implementation. The reviewer found:
> - "The `processOrder` handler doesn't validate the cart total against the server-calculated total before charging. Could be an issue." -> Severity: Medium
> - "No rate limiting on the `/api/checkout` endpoint. Should probably add that." -> Severity: Low
> - "The Stripe webhook handler uses `req.body` directly instead of the raw body for signature verification. Might cause issues." -> Severity: Medium
>
> Reviewer conclusion: "Overall the implementation is solid. The checkout flow works correctly on the happy path. Three medium/low issues found — none are blockers. **PASS**."

Why this review failed:
1. **Cart total validation gap is Critical, not Medium** — a client can send any total to the server and get charged that amount. This is a payment integrity vulnerability.
2. **Webhook signature verification is Critical, not Medium** — using parsed `req.body` instead of raw body means Stripe signature verification will always fail or can be bypassed. The webhook handler is effectively unauthenticated.
3. **The reviewer identified both issues then downplayed them.** "Could be an issue" and "might cause issues" are hedging language that signals the reviewer is already talking itself into approval.
4. **"Works on happy path" drove the verdict.** The reviewer tested the simplest case and let that override the specific issues it found.

A calibrated reviewer would have rated both as Critical and returned **FAIL**.


## Finding Quality Calibration

A finding's value depends on specificity. Compare:

**Vague finding (ineffective):**
> The fill tool seems to have some issues with how it handles the drawing area.

Problems: No specific behavior described, no code location, no reproduction path, no impact assessment. The recipient cannot act on this.

**Rigorous finding (effective):**
> **FAIL** — Rectangle fill tool only places tiles at drag start/end points instead of filling the entire enclosed region. `fillRectangle()` at `canvas.ts:142` is defined but is never called from the `mouseUp` handler at `canvas.ts:89`. The handler dispatches to `drawLine()` for all tool types. Impact: the fill tool is non-functional despite appearing in the toolbar. — Verification: select fill tool, drag a rectangle, observe only corner tiles placed.

Why this works: specific behavior, exact locations, root cause identified, impact stated, verification steps included. The recipient can go directly to the fix.
