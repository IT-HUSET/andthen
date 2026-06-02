# Security Review Calibration

Domain-specific calibration for reviewing implementation through a security lens. Load [`review-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md) first for universal calibration principles (anti-leniency protocol, finding quality, over-leniency patterns), then apply the domain-specific calibration below.

Security severity is driven by **exposure**: the same defect sits at different severity depending on who can reach the sink, with what preconditions, behind what auth/trust gate. The examples below pin severity to exposure, not to defect shape.

## Contents
- Severity Calibration – Contrastive Examples (Critical · High · Medium · Low)
- Exposure Modifiers
- False Positive Traps


## Severity Calibration – Contrastive Examples

Each pair shows what IS and is NOT that severity level.

### Critical

**IS Critical:**
> The `/api/products/:id` GET handler concatenates `req.params.id` directly into a raw SQL string passed to `pool.query`. The route is public (no auth middleware), and `id` is reflected into a `WHERE` clause. A union-based injection lifts the `users.password_hash` column. – `routes/products.ts:42`

Why: Exploitable on a public endpoint, with a clear path to the most sensitive data in the system. Source (untrusted public input) → sink (raw SQL) with no escape, no parameterization, no allowlist.

**IS Critical:**
> AWS access key and secret are committed in `config/dev.env` and the file is tracked by git. The keys grant `s3:*` on the production bucket per the IAM policy attached to that user. – `config/dev.env:4-5`

Why: Secret with broad production access committed to the repo. Exposure = anyone with read access to the repo (or anyone who clones from a fork that re-pushes the file's history).

**is NOT Critical (common over-escalation):**
> Missing CSRF token check on `/admin/internal/cache-flush`. The route requires admin SSO, sits behind a corporate VPN, and the only effect is clearing an in-memory cache.

Why: Exposure is internal admin only, with two trust gates (VPN + SSO) and a low-impact effect. This is MEDIUM – defense-in-depth gap, not an exploitable critical.

**is NOT Critical:**
> The login endpoint returns a slightly different error message for "user does not exist" vs "wrong password", enabling username enumeration.

Why: Information disclosure, not an exploit. Without rate limiting on the same endpoint, this could chain into a credential-stuffing concern (raise severity); on its own, this is HIGH at most, and often MEDIUM depending on whether the system already publishes usernames elsewhere (e.g. `@username` mentions).


### High

**IS High:**
> The webhook signature verification in `verifyStripeSignature` compares `expected !== received` with `!==` instead of a constant-time comparator. An attacker with network access can timing-attack the signature byte-by-byte. – `lib/webhooks/stripe.ts:67`

Why: Real exploitation path with concrete preconditions (network observability of the webhook endpoint). Constant-time comparison is the standard mitigation; the gap is named, well-understood, and not academic.

**IS High:**
> The `<img src={user.profileUrl}>` JSX renders a user-controlled URL without scheme validation. A `javascript:` URL turns into stored XSS the next time the profile is viewed. – `components/Profile.tsx:23`

Why: Stored injection on an authenticated surface. Exposure is "any user who can view another user's profile"; the sink is a DOM context that historically permits `javascript:` URLs unless framework-escaped (and React does not escape `src` attributes for the `javascript:` scheme automatically – verified, not assumed).

**is NOT High (common over-escalation):**
> The `package-lock.json` shows a transitive dependency at a version with a known CVE. The CVE describes a denial-of-service in a parser, but the project never calls the affected code path.

Why: CVE without an exploitable path is HIGH-noise / MEDIUM at most. Note the dependency, recommend the bump, but do not escalate without a real path. Track it as a hardening item, not as an active risk.

**is NOT High:**
> The `/health` endpoint returns the running version string and commit hash.

Why: Information disclosure on an endpoint that is by design publicly readable. Unless the version string itself is a secret (it isn't) or it correlates to an unpatched CVE the attacker would not otherwise know about, this is LOW.


### Medium

**IS Medium:**
> The admin user-creation form accepts a `role` field directly from the request body without an allowlist. Only admin SSO can reach this form, so privilege escalation requires another admin first; but a compromised admin session could mint a backdoor admin in one request. – `routes/admin/users.ts:55`

Why: Real defect with a concrete (though narrow) exploitation path. Exposure is admin-only, but the impact (backdoor admin creation) means it deserves a real fix.

**IS Medium:**
> Logged user objects in `logger.info('user authenticated', user)` include `user.email` and `user.passwordHash` (bcrypt). The hash is computationally expensive to crack, but its presence in log files widens the secret-storage surface. – `auth/login.ts:34`

Why: Defense-in-depth gap. The hash is not directly exploitable (bcrypt with a good cost factor), but log files often have wider read access than the auth database, so removing it tightens the trust boundary.


### Low

**IS Low:**
> `Strict-Transport-Security` header is missing on responses. The site is HTTPS-only by ALB redirect, but a first-visit downgrade attack is still possible.

Why: Hardening gap with a narrow preconditions (active MITM on first visit). Worth addressing, not blocking.

**IS Low:**
> JWT `aud` claim is not validated, but the issuer (`iss`) is, and tokens are minted by a single internal service for this single audience.

Why: Defense-in-depth – `aud` validation is the right pattern, but the practical exposure is zero today.


## Exposure Modifiers

Apply these as severity multipliers after assessing the raw defect:

| Exposure tier | Modifier |
|---|---|
| **Public unauthenticated** | Base severity stands. Most CRITICAL findings live here. |
| **Authenticated low-privilege** | Hold severity for defects that enable privilege escalation; downgrade by one tier for defects that only affect the actor's own data. |
| **Authenticated high-privilege / admin** | Downgrade by one tier unless the defect creates persistence (backdoor admin, key in storage, scheduled job). Persistence holds severity. |
| **Internal-only / VPN-gated** | Downgrade by one tier; do not go below LOW for any real defect. Treat as hardening. |
| **Build/CI/supply-chain** | Hold severity. Compromise here often grants the worst possible blast radius (every future build) and is not visible from the running app. |


## False Positive Traps

Common patterns that look like security issues but aren't. Check for these before recording a finding:

1. **Test fixtures triggering scanners.** Example: Semgrep flagging `password = "test123"` in `__fixtures__/users.ts`. Fixtures are intentionally minimal; verify the file path, not just the substring.

2. **Intentional eval / shell in admin tooling.** Example: a developer-only diagnostic endpoint that runs `child_process.exec` against a controlled allowlist. The allowlist is the security control; flagging the `exec` call alone misreads the threat model. Read the surrounding validation before flagging.

3. **Framework-provided escapes mistaken for absent escapes.** Example: flagging `{userInput}` rendered in JSX as XSS – React escapes interpolated children by default. The bug exists for `dangerouslySetInnerHTML`, `href` schemes, `src` attributes, and `style` strings. Verify the framework's actual escape behavior for the specific sink before flagging.

4. **CVE-by-vulnerability-database without an exploitable path.** Example: flagging a transitive dependency CVE when the affected function is never imported. Note as MEDIUM hardening, not as HIGH active risk.

5. **Security tooling output treated as findings.** Example: Semgrep produced 47 hits on a 2000-line PR; reporting all 47 is review-by-tooling. Map each hit to a real source/sink first, discard test-fixture / framework-escape false positives, and report only the survivors.

6. **Defense-in-depth flagged as gap.** Example: flagging the absence of CSP headers on a JSON-only API. CSP is a browser-rendering control; on a JSON API the header has no enforcement target. Hardening rec, not a finding.

7. **Severity inflation from category, not exploitation.** Example: tagging every input-validation gap as HIGH because "input validation = security." Severity is per finding's exposure and impact, not per category label. A missing length cap on an admin-only internal field is MEDIUM, not HIGH.

(Cumulative severity inflation – "five LOWs are not one HIGH" – is rule 9 of the universal Anti-Leniency Protocol; it is not repeated here.)
