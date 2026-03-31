# Review Calibration Reference

Calibration examples and anti-leniency protocol for review skills. Load this reference before assigning severity to findings.

> **Purpose**: Checklists tell you *what* to look for; this reference shows *how rigorously* to look.
> Models trend toward leniency — identifying real issues then rationalizing them away. This reference counteracts that bias.


## Anti-Leniency Protocol

Apply these rules when evaluating findings:

1. **If you identified a problem, it IS a problem.** Do not talk yourself into deciding it "isn't a big deal" or "probably works fine." Your first instinct that something is wrong is usually correct.
2. **"Works on happy path" is not a pass.** Verify edge cases, error paths, boundary conditions, and integration points. A feature that works in the simplest case but breaks on real-world input is a real gap.
3. **A stub that compiles is still a stub.** Substance means real logic — a function body with `return null`, a TODO comment, a placeholder response, or an empty handler is incomplete implementation regardless of whether it builds.
4. **Apply the PR-review standard.** If you would flag this in a code review for a team you respect, flag it here. Do not lower your standards because this is an automated review.
5. **Probe deeply, not broadly.** Don't just check that each requirement has a corresponding file. Verify that event handlers actually fire, that data flows end-to-end, that error states are handled, that routes are registered in the correct order.
6. **Do not dismiss findings you've already identified.** If your analysis found an issue, record it at the severity it deserves. The remediation plan can deprioritize it — your job is accurate identification, not triage.


## Severity Calibration — Contrastive Examples

Each pair shows what IS and is NOT that severity level. Use these to calibrate your severity assignments.

### Critical

**IS Critical:**
> Auth middleware (`requireAuth.ts`) exists and correctly validates JWT tokens, but is not applied to any of the `/api/payments/*` routes. All payment endpoints are publicly accessible without authentication. — `routes/payments.ts:12-45`

Why: Security bypass affecting a critical data path. The code exists but the wiring is missing, making the vulnerability invisible to a surface-level check.

**IS Critical:**
> The `deleteProject` handler executes `DELETE FROM projects WHERE id = ?` but has no confirmation step, no soft-delete flag, and no cascade protection. Child records (tasks, files, comments) are left orphaned via `ON DELETE SET NULL`, silently corrupting data relationships. — `handlers/project.ts:89`

Why: Data loss risk with silent corruption. The operation succeeds but leaves the database in an inconsistent state.

**is NOT Critical (common over-escalation):**
> Missing input length validation on the admin-only internal configuration endpoint `/admin/settings`. Only accessible to authenticated admin users behind VPN.

Why: Low exposure surface (authenticated admins, VPN-only). This is Medium severity — worth noting but not a blocker.

**is NOT Critical:**
> The error response for 404 cases returns `{ error: "Not found" }` instead of the standard `{ error: { code: "NOT_FOUND", message: "..." } }` format used elsewhere.

Why: Inconsistency, not a security or functionality issue. This is Low severity — a consistency gap.


### High

**IS High:**
> The `processPayment` handler catches all exceptions with a bare `catch (e) {}` block — errors from the payment gateway (declined cards, network timeouts, duplicate charges) are silently swallowed. The user sees a success response regardless of whether payment actually processed. — `handlers/payment.ts:67-82`

Why: Silent failure in a critical business path. The feature appears to work but silently fails in foreseeable error scenarios.

**IS High:**
> The search results component fetches all matching records with no pagination. On the demo dataset (50 records) this works, but the production dataset has 2M+ records. No `LIMIT`, no cursor, no pagination UI. — `components/SearchResults.tsx:23`, `api/search.ts:15`

Why: Works in development, breaks in production. A functional gap that will only surface under real conditions.

**is NOT High (common over-escalation):**
> `console.log("debug: user data", userData)` left in the registration handler. The log contains the user's name and email.

Why: Should be removed, but logging to server stdout is not a security vulnerability (unlike logging to client-side console). This is Medium — code quality issue, not a data breach.

**is NOT High:**
> The `UserProfile` component re-renders on every keystroke in the search bar due to shared parent state. No memoization.

Why: Performance optimization, not a functionality gap. Unless profiling shows a measurable impact or the requirement specifies performance targets, this is a Suggestion/Low finding.


### Completeness Calibration

**IS a completeness gap:**
> `calculateShipping()` in `services/shipping.ts:34` has the function signature and JSDoc, but the body is `return 0; // TODO: implement shipping calculation`. This is the only shipping cost function and is called by the checkout flow. The checkout will process orders with $0 shipping.

Why: Core business logic path with a stub. The feature is fundamentally incomplete.

**is NOT a completeness gap:**
> `// TODO: add unit tests for edge cases` comment in `utils/formatter.ts:12`. The formatter function has full implementation logic and passes existing tests.

Why: The TODO is aspirational — the implementation is complete. Missing tests are a separate finding (test coverage gap), not an implementation completeness gap.


### Wiring Calibration

**IS a wiring gap:**
> `NotificationBanner` component is exported from `components/NotificationBanner.tsx` and appears in the component index, but is never imported or rendered by any page or layout. The notification system has no visible UI. — `grep -r "NotificationBanner" src/` returns only the definition file.

Why: The component exists and is substantive, but isn't connected to the running application. A user would never see it.

**is NOT a wiring gap:**
> `ErrorBoundary` wraps the main `App` component but is not applied to every individual route. Some routes would show the default browser error on crash instead of the custom error UI.

Why: The component IS wired — it's rendered at the app level. Whether it should also wrap individual routes is a design decision, not a missing wire. This might be a functionality gap if error resilience was a requirement, but it's not a wiring gap.


## Over-Lenient Review Calibration

The most dangerous evaluator failure is identifying real issues then approving anyway. Study this example:

**Over-lenient review that wrongly approved (annotated):**
> Review of a checkout flow implementation. The reviewer found:
> - "The `processOrder` handler doesn't validate the cart total against the server-calculated total before charging. Could be an issue." → Severity: Medium
> - "No rate limiting on the `/api/checkout` endpoint. Should probably add that." → Severity: Low
> - "The Stripe webhook handler uses `req.body` directly instead of the raw body for signature verification. Might cause issues." → Severity: Medium
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

Problems: No specific behavior described, no code location, no reproduction path, no impact assessment. The implementer cannot act on this.

**Rigorous finding (effective):**
> **FAIL** — Rectangle fill tool only places tiles at drag start/end points instead of filling the entire enclosed region. `fillRectangle()` at `canvas.ts:142` is defined but is never called from the `mouseUp` handler at `canvas.ts:89`. The handler dispatches to `drawLine()` for all tool types. Impact: the fill tool is non-functional despite appearing in the toolbar. — Verification: select fill tool, drag a rectangle, observe only corner tiles placed.

Why this works: specific behavior, exact code locations, root cause identified, impact stated, reproduction steps included. The implementer can go directly to the fix.


## False Positive Traps

Common patterns that look like issues but aren't. Check for these before recording a finding:

1. **Framework conventions mistaken for missing code.** Example: flagging Next.js pages for "missing explicit route registration" when file-based routing handles this automatically. Always verify whether the framework provides the behavior before flagging its absence.

2. **Intentional trade-offs documented in ADRs or comments.** Example: flagging a synchronous database call when an ADR explicitly chose this over async for simplicity in a low-traffic admin tool. Check for architectural decision records before escalating design choices.

3. **Test utilities flagged as stubs.** Example: marking a test helper that returns `{ id: 1, name: "test" }` as a "stub implementation." Test fixtures and factories are intentionally minimal — they are not production code.

4. **Optional features flagged as missing.** Example: flagging the absence of dark mode support when the requirements don't mention it. Verify that a finding maps to an actual requirement before recording it as a gap.

5. **Cross-cutting severity inflation.** Example: finding 5 Low-severity style inconsistencies and escalating the group to High because "there are many issues." Severity is per-finding, not cumulative. Five Low issues are five Low issues, not one High issue.
