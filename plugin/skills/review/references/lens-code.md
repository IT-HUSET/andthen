# Lens: Code Review

Rubric for reviewing implementation, config, tests, and code changes. Load this reference when running `andthen:review --mode code` or when the Mixed mode's code sub-pass runs.


## Scope

Implementation files (source code, config, tests). Determine scope from: explicit paths/PR/issue in arguments, current pending changes (`git diff --stat`, `git diff --name-only`), or relevant neighboring files. Exclude generated, vendored, and lockfile noise.

Identify the project checks relevant to the review scope by inspecting the repo's existing automation surfaces first: package scripts, Make targets, Justfiles, CI workflows, language-native config files, or documented contributor commands. Prefer the narrowest commands that still give trustworthy signal for the changed scope.


## Lenses (applicable subset)

Run only the lenses that actually apply to the changed scope. Use the checklists under `../checklists/`:

1. **Code quality** — [CODE-REVIEW-CHECKLIST.md](../checklists/CODE-REVIEW-CHECKLIST.md): correctness, edge cases, readability, naming, maintainability, performance, duplication
2. **Architecture** — [ARCHITECTURAL-REVIEW-CHECKLIST.md](../checklists/ARCHITECTURAL-REVIEW-CHECKLIST.md): pattern adherence, coupling/cohesion, CUPID, DDD where relevant, resilience/performance trade-offs
3. **Domain language** — [DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md](../checklists/DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md) when the `Ubiquitous Language` document (see **Project Document Index**) exists: terminology consistency
4. **UI/UX** — [UI-UX-REVIEW-CHECKLIST.md](../checklists/UI-UX-REVIEW-CHECKLIST.md) when UI changed: usability, responsiveness, accessibility, interaction quality
5. **Security awareness (thin pass)** — flag obvious security smells visible during ordinary code review: hardcoded secrets, raw SQL or shell string concatenation with untrusted input, unvalidated user input reaching dangerous sinks, missing auth/authz checks on new endpoints, broken or absent error handling in security-sensitive paths. Do **not** load OWASP checklists or run security scanners here — that is the security lens's job. When the changed surface materially touches auth, payments, network-exposed handlers, user input parsing, secret/credential handling, crypto, LLM/agent flows, native/cross-platform mobile (iOS/Android/React Native/Flutter/Expo) surfaces, or IaC/CI/CD, the review skill auto-routes the security lens into the chain — but only when `--mode` is absent. If `--mode code` (or any chain that explicitly omits `security`) was passed, auto-routing is suppressed; flag the surface as a HIGH finding ("surface warrants security lens — consider `--mode code,security`") rather than attempting OWASP-depth analysis here.

When the review touches browser state, AI/agent flows, logs, stack traces, error output, scraped content, tool results, or other external-data flows, apply [`trust-boundaries.md`](${CLAUDE_PLUGIN_ROOT}/references/trust-boundaries.md). The trust-boundary reference is broader than security — it informs domain language, integration, and resilience review too — and stays in the code lens regardless of whether the security lens is also running.


## Critic Sub-Lens (Always On)

Run `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` against the same code scope as an always-on sub-lens. This is the finding pass for fragile assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring that constructive review can miss.

When code review delegates specialist lenses to sub-agents, each specialist runs the Critic sub-lens against its own focus area, **and** a single sub-agent runs the Critic sub-lens against the **whole** change set in parallel. Specialists optimize for depth-within-concern; the generalist catches cross-concern issues that fall between specialist scopes — e.g. a security-shaped quirk inside an architecture slice that neither lens claims as theirs. Without the generalist pass, the find-time isolation the `andthen:quick-review` skill relies on is absent from the bigger review. The generalist is an **additional** sub-agent — not a replacement for any specialist (see *Parallelization* below for fan-out accounting). The synthesis merges all Critic findings into the normal severity sections before any Findings Filter runs.


## Calibration

Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) and `code-review-calibration.md` (code-specific). Load `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md` while running the always-on Critic sub-lens; use the code-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## Verification Evidence

Run applicable project checks that strengthen review signal. The `Key Dev Commands` document (see **Project Document Index**; default: `docs/KEY_DEVELOPMENT_COMMANDS.md`) is the canonical source for these commands when present; fall back to discovery (package.json scripts, Makefile targets, language conventions) only when the document is missing.

- **Build**: project's applicable build/package checks
- **Tests**: applicable test suites
- **Lint/types**: applicable static analysis, linting, type checks
- **Formatting**: formatter/compile sanity checks when relevant

When invoked standalone, treat those checks as part of the review evidence. When invoked by an orchestrator that already ran them, reuse fresh results when available instead of rerunning broad project checks unnecessarily. Report which verification commands were run, which were skipped, and why. Do not claim a clean review if a critical available check failed or could not be interpreted.


## Parallelization

When the review applies two or more lenses from the list above and sub-agents are supported, delegate each applicable lens to a parallel sub-agent. Otherwise run the same lenses sequentially inline. The security awareness pass is light enough to run inline; deep security review runs in its own lens (`andthen:review --mode security`) and parallelizes there.

Total fan-out is N specialists **plus one** generalist Critic sub-agent (per *Critic Sub-Lens (Always On)* above) — the generalist adds to the parallel set, it does not displace a specialist.


## Findings Output

Categorize findings using the unified severity scale from `review-verdict.md`:
- **CRITICAL**: security vulnerabilities, data loss, or broken core behavior
- **HIGH**: significant maintainability, performance, or correctness issues
- **MEDIUM**: non-trivial quality/consistency issues worth addressing
- **LOW**: worthwhile improvements or cleanup

Also flag obsolete files, unmotivated complexity, and cleanup candidates.

**Pre-existing-issue calibration**: an "out of scope" or "did not touch pre-existing X" disclaimer applied to issues that sit *inside the changed files* is itself a finding (default MEDIUM; raise to HIGH for correctness/security). Issues in *unchanged* files remain out of scope.

**Readiness label**: `Ready` / `Needs Fixes` / `Blocked` — per the verdict reference.


## Report Sections

```markdown
## Summary
[2-3 sentence overview]

## CRITICAL ISSUES
[Title, impact, location, fix required]

## HIGH PRIORITY
[Title, impact, location, recommendation]

## MEDIUM
[Title, impact, location, recommendation]

## LOW
[Brief list]

## Cleanup Required
- [Obsolete or temporary files]
- [Dead code]

## Compliance
- Guidelines adherence: [Assessment]
- Architecture patterns: [Assessment]
- Security awareness: [Assessment]
- [UI/UX if applicable]: [Assessment]

_Security awareness covers obvious smells only; defer to the security lens for depth when applicable._

## Verification Evidence
- Commands run: [with result]
- Commands skipped/unavailable: [with reason]

## Readiness
Ready / Needs Fixes / Blocked — with severity counts

## Next Steps
1. [Prioritized action items]
```


## Report Output Conventions

Filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This lens contributes:
- **`<feature-name>` token**: the feature or primary changed-area name (e.g. `payments`, `auth-refresh`)
- **Report suffix**: `code-review` (canonical source: the `andthen:review` skill's mode table)
- **Target nature**: source-code. The location reference's source-code subdirectory guard applies — tier-2 "next to target" is disabled, so without a resolvable spec directory, current feature directory, or `--output-dir`, the report lands in `<agent-temp>/reviews/`.
