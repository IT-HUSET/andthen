# Lens: Security Review

Rubric for reviewing implementation, config, infrastructure, and supply-chain artifacts for security defects – source, config, IaC, CI/CD workflows, lockfiles, and deployment manifests, excluding generated and vendored noise unless lockfile changes are themselves the surface (supply-chain review).

Where the code lens flags the smells visible in passing, this lens runs OWASP-aligned coverage and explicit data-flow analysis over authn/authz, secrets, injection, trust boundaries, and LLM/agent flows.


## Escalation Triggers

Any one pulls `security` into a lens set resolved without `--mode`:

- auth/session/authz (login, JWT, OAuth, RBAC, password); payments/money; secrets/credentials/keys/crypto.
- network-exposed handlers (HTTP/GraphQL/gRPC/webhooks/consumers) and user-input/file-upload parsing; LLM/agent/RAG/tool-call flows.
- IaC/CI-CD/deploy/lockfile/supply-chain; native or cross-platform mobile surface (keychain/keystore, deep links, cert pinning, biometric, IAP).


## Coverage Focus

The security surfaces are each external-data source/sink pair, auth/authz boundary, secret-handling path, and OWASP-aligned attack surface in scope, each with an attacker-shaped falsifier; a primary surface left unattacked is a finding. A checklist the project supplies applies only to matching surfaces – unmatched ones create generic noise.


## Trust-Boundary Analysis

External-data trust is a data flow, not an awareness check. For each source in scope (user input, browser state, scraped content, AI/agent flows, logs, stack traces, error output, tool results, third-party API responses, queue messages, file uploads), trace the data through the changed code: where the boundary is crossed, what validation, sanitization, or escaping it applies, which sink consumes it (query string, HTML render, shell command, prompt template, file path, redirect target, deserialization, log line), and whether the validation between them is sufficient for the sink's threat model. One finding per source/sink pair where validation is missing, weak, or inconsistently applied, filed under its OWASP category (injection, SSRF, XSS, prompt injection) when assigning severity.


## Critic Posture

Assume the attacker, not just the careless developer. Walk each entry point with malicious input, partial trust, replay, race, and resource-exhaustion intent, attacking what an upstream layer is assumed to guarantee – that is where exploitable gaps hide, each finding filed under its OWASP/trust-boundary category.


## Verification Evidence

Run the security checks the project already wires up – SAST or security-ruled linters, dependency audit, secret scanning, IaC/container scanning, security-relevant test suites – reusing an orchestrator's fresh results, and report which ran and which were skipped and why. Their hits are input to the trust-boundary analysis, never findings. A scanner that failed or could not be interpreted forbids a clean review.


## Findings Filter Values

Role `Findings Filter reviewing security review findings`; calibration this lens's § Findings Output; questions: is the source/sink path real, does the severity reflect the exposure level (public / authenticated / internal / admin / VPN), could a mitigation exist upstream or downstream of the changed code, is this a known false-positive shape (test fixture, intentional eval, framework-provided escape)?


## Findings Output

Exposure calibration on the unified scale:
- **CRITICAL**: public endpoint, untrusted input reaching a dangerous sink, secret committed to the repo, auth bypass
- **HIGH**: a low-privilege authenticated user can escalate, missing rate limit on an auth endpoint, weak crypto primitive for non-trivial data
- **MEDIUM**: admin-only endpoint without input validation, an unsafe pattern that needs another bug to exploit, a hardening gap
- **LOW**: defense-in-depth opportunity, security-relevant cleanup, missing best practice without a concrete threat model

Exposure then modifies what the scale placed, because the same defect is not the same risk at every tier – who reaches the sink, through how many trust gates:

| Exposure tier | Modifier |
|---|---|
| Public unauthenticated | Base severity stands; most CRITICAL findings live here. |
| Authenticated low-privilege | Holds where the defect escalates privilege; one tier down where it reaches only the actor's own data. |
| Authenticated high-privilege / admin | One tier down, unless the defect creates persistence – backdoor admin, key written to storage, scheduled job. Persistence holds. |
| Internal-only / VPN-gated | One tier down, never below LOW for a real defect; file it as hardening. |
| Build / CI / supply-chain | Holds. A compromise here owns every future build and is invisible from the running app. |

Two shapes get over-escalated on category rather than exposure, and both are MEDIUM:

- **A missing CSRF check on `/admin/internal/cache-flush`** – admin SSO and a corporate VPN in front of it, and the effect is flushing an in-memory cache. Two trust gates and a low-impact sink make it a hardening gap, not a CRITICAL; the same missing check on a public state-changing endpoint is one.
- **A transitive CVE in the lockfile whose affected function the project never calls** – name the dependency and recommend the bump, but severity follows a traced call path, not the advisory's own rating. Trace one and the finding is HIGH.

A disclaimer-as-finding (`review-calibration.md` § Anti-Leniency Protocol) on an auth, injection, or secret issue inside the changed files defaults to HIGH here. The report's `<feature>` token is the feature or primary changed-area name (`payments`, `auth-refresh`, `webhook-handler`); the target is source code, so the report never sits beside it.
