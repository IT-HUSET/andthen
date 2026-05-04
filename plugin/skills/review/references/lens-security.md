# Lens: Security Review

Rubric for reviewing implementation, config, infrastructure, and supply-chain artifacts for security defects. Load this reference when running `andthen:review --mode security` or when the Mixed mode resolves a `security` sub-pass.

The target is implementation, the same surface as the code lens. The difference is depth and posture: the code lens runs a thin awareness pass for obvious smells; this lens runs the OWASP-aligned checklists, security tooling, and explicit data-flow analysis that depth requires.


## Scope

Implementation files (source code, config, IaC, CI/CD workflows, lockfiles, deployment manifests). Determine scope from: explicit paths/PR/issue in arguments, current pending changes (`git diff --stat`, `git diff --name-only`), or relevant neighboring files. Exclude generated, vendored, and lockfile noise unless lockfile changes are themselves the surface (supply-chain review).

Identify the project checks relevant to the security scope by inspecting the repo's existing automation surfaces first: package scripts, Make targets, Justfiles, CI workflows, language-native config files, or documented contributor commands. Prefer the narrowest commands that still give trustworthy signal for the changed surface.


## Applicability Gate

Load only the OWASP checklists that match the surface under review. Loading all five always defaults the review into a generic posture and floods the report with noise.

| Checklist | Standard | Apply when... |
|-----------|----------|---------------|
| [SECURITY-CHECKLIST-WEB.md](../checklists/SECURITY-CHECKLIST-WEB.md) | OWASP Top 10:2025 | Web applications, server-rendered pages, or any general-purpose backend |
| [SECURITY-CHECKLIST-API.md](../checklists/SECURITY-CHECKLIST-API.md) | OWASP API Security Top 10:2023 | REST, GraphQL, gRPC, microservices, or other HTTP-exposed code |
| [SECURITY-CHECKLIST-LLM.md](../checklists/SECURITY-CHECKLIST-LLM.md) | OWASP LLM Top 10:2025 | LLM, RAG, agentic, or AI-generated-output systems |
| [SECURITY-CHECKLIST-MOBILE.md](../checklists/SECURITY-CHECKLIST-MOBILE.md) | OWASP Mobile Top 10:2024 | Native or cross-platform mobile apps |
| [SECURITY-CHECKLIST-CICD.md](../checklists/SECURITY-CHECKLIST-CICD.md) | OWASP CI/CD Risks | Pipelines, IaC, deployment workflows, build scripts, supply chain changes |

Multiple checklists may apply (e.g. a web app with an LLM backend → Web + API + LLM). Skip a checklist outright when its surface is not represented in the changed scope; do not include "for completeness."


## Trust-Boundary Analysis

Apply [`trust-boundaries.md`](${CLAUDE_PLUGIN_ROOT}/references/trust-boundaries.md) as a data-flow analysis, not just an awareness check. For each external-data source in scope (user input, browser state, scraped content, AI/agent flows, logs, stack traces, error output, tool results, third-party API responses, queue messages, file uploads), trace the data through the changed code and identify:

- Where the boundary is crossed
- What validation, sanitization, or escaping the boundary applies
- Where the data is consumed (sink): query string, HTML render, shell command, prompt template, file path, redirect target, deserialization, log line
- Whether the validation between boundary and sink is sufficient for the sink's threat model

Record one finding per source/sink pair where validation is missing, weak, or applied inconsistently. Trust-boundary findings often map to OWASP categories (injection, SSRF, XSS, prompt injection); cross-reference the relevant checklist when assigning severity.


## Tooling

Run available security scanners when applicable. The default tool is Semgrep via the helper script:

```sh
${CLAUDE_SKILL_DIR}/scripts/run-security-scan.sh <path>
```

Treat scanner output as input to the review, not as findings on its own:
- Map each scanner hit to a finding only after confirming the alleged sink, source, and threat model match the code in context
- Discard test-fixture, mock, and intentional-eval-in-admin-tooling false positives at this stage rather than passing them to Findings Filter
- When scanners are unavailable, note their absence in Verification Evidence and continue with manual review

Other security tooling that the project already wires up (`npm audit`, `pip-audit`, `cargo audit`, `trivy`, `gitleaks`, IaC scanners) should be run when present and reported alongside Semgrep in Verification Evidence.


## Critic Sub-Lens (Always On)

Run [`lens-adversarial.md`](${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md) against the same security scope as an always-on sub-lens. Posture for the security context: assume the attacker, not just the careless developer. Walk each entry point with malicious input, partial trust, replay, race, and resource-exhaustion intent. Attack assumptions about what an upstream layer guarantees — these are the assumptions where exploitable gaps hide.

Merge Critic findings into the OWASP/trust-boundary categories before the Findings Filter runs. Do not treat the Critic as a separate mode or an optional escalation.


## Calibration

Calibrate severity with [`review-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md) (universal) and `security-review-calibration.md` (security-specific contrastive examples and false-positive traps). Load [`critic-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md) while running the always-on Critic sub-lens; use the security-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.

Security severity is more sensitive to *exposure* than code-lens severity — the same code defect can be CRITICAL on a public unauthenticated endpoint and MEDIUM behind admin-only VPN access. The calibration reference's contrastive examples make this explicit.


## Verification Evidence

Run applicable security checks that strengthen review signal:
- **Static analysis / SAST**: Semgrep (via the helper above), language-specific linters with security rules
- **Dependency scanning**: `npm audit`, `pip-audit`, `cargo audit`, language-equivalent
- **Secret scanning**: `gitleaks`, `trufflehog`, or repo-configured equivalent
- **IaC / container scanning**: `trivy`, `checkov`, repo-configured equivalent
- **Project tests**: when security-relevant tests exist (auth flows, input-validation suites)

When invoked standalone, treat those checks as part of the review evidence. When invoked by an orchestrator that already ran them, reuse fresh results when available instead of rerunning broad project checks unnecessarily. Report which scanners were run, which were skipped, and why. Do not claim a clean review if a scanner failed or could not be interpreted.


## Findings Filter

> **Findings Filter**: see [`lens-findings-filter.md`](lens-findings-filter.md).

Lens-specific placeholder values:
- **Role**: `Findings Filter reviewing security review findings`
- **Skill calibration**: `security-review-calibration.md`
- **Context block**: `Review target context: {implementation paths and applicable OWASP checklists from Step 0}`
- **Questions**: Is the source/sink path real? Is the exposure level (public / authenticated / internal / admin / VPN) accurately reflected in the severity? Could there be an existing mitigation upstream or downstream of the changed code? Is this a known false-positive shape (test fixture, intentional eval, framework-provided escape)?
- **Findings payload**: `{all findings from OWASP checklists, trust-boundary analysis, scanner hits, and Critic walkthrough}`

Apply verdicts before scoring.


## Findings Output

Categorize findings using the unified severity scale from `review-verdict.md`:
- **CRITICAL**: actively exploitable on an exposed surface (public endpoint, untrusted input reaching dangerous sink, secret committed to the repo, auth bypass)
- **HIGH**: significant security defect with a clear exploitation path requiring weak preconditions (authenticated user with low-privilege role can escalate, missing rate limit on auth endpoint, weak crypto primitive for non-trivial data)
- **MEDIUM**: defect with limited exposure or high preconditions (admin-only endpoint without input validation, unsafe pattern that requires another bug to exploit, hardening gap)
- **LOW**: defense-in-depth opportunity, security-relevant cleanup, missing best practice without a concrete threat model

**Pre-existing-issue calibration**: an "out of scope" or "did not touch pre-existing X" disclaimer applied to security issues sitting *inside the changed files* is itself a finding (default HIGH for any auth/injection/secret issue, MEDIUM otherwise). Issues in *unchanged* files remain out of scope.

**Readiness label**: `Ready` / `Needs Fixes` / `Blocked` — per the verdict reference (security mode reuses the code-mode readiness scale; CRITICAL findings → `Blocked`).


## Report Sections

```markdown
## Summary
[2-3 sentence overview, including which OWASP checklists were applied]

## CRITICAL ISSUES
[Title, OWASP category, source/sink, location, fix required]

## HIGH PRIORITY
[Title, OWASP category, source/sink, location, recommendation]

## MEDIUM
[Title, OWASP category, location, recommendation]

## LOW
[Brief list]

## Trust-Boundary Map
- [Source → validation → sink, per analyzed flow]

## Verification Evidence
- Scanners run: [with result]
- Scanners skipped/unavailable: [with reason]

## Readiness
Ready / Needs Fixes / Blocked — with severity counts

## Next Steps
1. [Prioritized action items, sequenced by exposure level]
```


## Report Output Conventions

Filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This lens contributes:
- **`<feature-name>` token**: the feature or primary changed-area name (e.g. `payments`, `auth-refresh`, `webhook-handler`)
- **Report suffix**: `security-review` (canonical source: the `andthen:review` skill's mode table)
- **Target nature**: source-code. The location reference's source-code subdirectory guard applies — tier-2 "next to target" is disabled, so without a resolvable spec directory, current feature directory, or `--output-dir`, the report lands in `<agent-temp>/reviews/`.
