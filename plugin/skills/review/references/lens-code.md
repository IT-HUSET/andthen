# Lens: Code Review

Rubric for reviewing implementation, config, tests, and code changes. Load this reference when running the `andthen:review` skill with `--mode code` or when the Mixed mode's code sub-pass runs.

## Contents
- Scope · Coverage Focus · Lenses (applicable subset) · Critic Sub-Lens · Calibration
- Verification Evidence · Parallelization · Refactor Invariants · Large-Diff Fan-Out
- Findings Output · Report Sections · Report Output Conventions


## Scope

Implementation files (source code, config, tests). Determine scope from: explicit paths/PR/issue in arguments, current pending changes (`git diff --stat`, `git diff --name-only`), or relevant neighboring files. Exclude generated, vendored, and lockfile noise.

Identify the project checks relevant to the review scope by inspecting the repo's existing automation surfaces first: package scripts, Make targets, Justfiles, CI workflows, language-native config files, or documented contributor commands. Prefer the narrowest commands that still give trustworthy signal for the changed scope.


## Coverage Focus

Before judging readiness, identify the code surfaces whose failure would matter: changed behavior, changed tests/proofs, public APIs, callers/consumers, integration seams, persistence/config boundaries, user-facing copy, trust boundaries, and project-rule surfaces. Each high-risk surface needs evidence and a falsifier. A code review that only reads the happy-path diff is incomplete.

When any proof-bearing artifact changed – tests, parsers, validators, release registers, sign-off artifacts, generated artifacts, locale-paired content, migrations, workflows, or public APIs – run a **test-contract falsification** pass: name the bad state each important assertion should reject. Extra/duplicate/malformed rows, omitted locale siblings, stale copy, timezone boundaries, wrong fallback selection, and weak set/contains assertions are typical failures. If a test can pass while the protected behavior is wrong, record a finding even when the suite is green.


## Lenses (applicable subset)

Run only the lenses that actually apply to the changed scope. Use the checklists under `../checklists/`:

1. **Code quality** – [CODE-REVIEW-CHECKLIST.md](../checklists/CODE-REVIEW-CHECKLIST.md): correctness, edge cases, readability, naming, maintainability, performance, duplication, and the baseline smell scan. Smells are heuristic findings, not hard violations; documented project standards override the baseline, and tooling-enforced issues stay with tooling.
2. **Architecture** – [ARCHITECTURAL-REVIEW-CHECKLIST.md](../checklists/ARCHITECTURAL-REVIEW-CHECKLIST.md): pattern adherence, coupling/cohesion, CUPID, DDD where relevant, resilience/performance trade-offs. When the `Architecture` document (see **Project Document Index**) exists, use it as the system-shape baseline – flag changes that drift from documented component boundaries or patterns as architectural findings rather than code-quality nits.
3. **Domain language** – [DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md](../checklists/DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md) when the `Ubiquitous Language` document (see **Project Document Index**) exists: terminology consistency
4. **UI/UX** – [UI-UX-REVIEW-CHECKLIST.md](../checklists/UI-UX-REVIEW-CHECKLIST.md) when UI changed: usability, responsiveness, accessibility, interaction quality
5. **Security awareness (thin pass)** – flag obvious security smells visible during ordinary code review: hardcoded secrets, raw SQL or shell string concatenation with untrusted input, unvalidated user input reaching dangerous sinks, missing auth/authz checks on new endpoints, broken or absent error handling in security-sensitive paths. Do **not** load OWASP checklists or run security scanners here – that is the security lens's job. When the changed surface materially touches auth, payments, network-exposed handlers, user input parsing, secret/credential handling, crypto, LLM/agent flows, native/cross-platform mobile (iOS/Android/React Native/Flutter/Expo) surfaces, or IaC/CI/CD, the review skill auto-routes the security lens into the chain – but only when `--mode` is absent. If `--mode code` (or any chain that explicitly omits `security`) was passed, auto-routing is suppressed; flag the surface as a HIGH finding ("surface warrants security lens – consider `--mode code,security`") rather than attempting OWASP-depth analysis here.

When the review touches browser state, AI/agent flows, logs, stack traces, error output, scraped content, tool results, or other external-data flows, apply [`trust-boundaries.md`](${CLAUDE_PLUGIN_ROOT}/references/trust-boundaries.md). The trust-boundary reference is broader than security – it informs domain language, integration, and resilience review too – and stays in the code lens regardless of whether the security lens is also running.


## Critic Sub-Lens (Always On)

Run `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` against the same code scope as an always-on sub-lens. This is the finding pass for fragile assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring that constructive review can miss.

Dispatch per `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` § Sub-agent dispatch (prefer the `review-critic` agent for the whole-change-set pass with a read-first task prompt for the three calibration files; else a generic fresh-context sub-agent; inline fallback requires a `Critic Coverage` note).

When code review delegates specialist lenses to sub-agents, each specialist runs the Critic sub-lens against its own focus area, **and** a single sub-agent runs the Critic sub-lens against the **whole** change set in parallel. Specialists optimize for depth-within-concern; the generalist catches cross-concern issues that fall between specialist scopes – e.g. a security-shaped quirk inside an architecture slice neither lens claims. It is an **additional** sub-agent (fan-out accounting in *Parallelization* below). The synthesis merges all Critic findings into the normal severity sections before any Findings Filter runs.


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

When the review applies two or more lenses from the list above and sub-agents are supported, delegate each applicable lens to a parallel sub-agent. Otherwise run the same lenses sequentially inline. The security awareness pass is light enough to run inline; deep security review runs through the `andthen:review` skill with `--mode security` and parallelizes there.

Total fan-out is N specialists **plus one** generalist Critic sub-agent (per *Critic Sub-Lens (Always On)* above) – the generalist adds to the parallel set, it does not displace a specialist.


## Refactor Invariants

When the diff matches any trigger in [`refactor-invariants.md`](refactor-invariants.md) (deletion, rename, lifecycle relocation, cache introduction, codegen, schema migration, parameter threading), load that reference and run the triggered subset as a finding pass. Targets cross-file invariants no individual hunk hosts – the class of issue hunk-by-hunk review structurally misses on refactor-shaped change sets. Findings merge into the severity sections below – this is not a separate report section or mode.


## Large-Diff Fan-Out

When the diff exceeds the threshold or the review surface is semantically wide per [`large-diff-fanout.md`](large-diff-fanout.md), partition the diff into 2–5 vertical (feature/concern) slices – never horizontal layers – dispatch one lens sub-agent per partition, then run a boundary pass attacking cross-partition surface. Composes with `--council` and chain dispatch – see the fan-out reference for partition strategy and concurrency.


## Findings Output

Categorize findings using the unified severity scale from `review-verdict.md` (CRITICAL / HIGH / MEDIUM / LOW). Also flag obsolete files, unmotivated complexity, and cleanup candidates.

**Pre-existing-issue calibration**: an "out of scope" or "did not touch pre-existing X" disclaimer applied to issues that sit *inside the changed files* is itself a finding (default MEDIUM; raise to HIGH for correctness/security). Issues in *unchanged* files remain out of scope.

**Readiness label**: `Ready` / `Needs Fixes` / `Blocked` – per the verdict reference.


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

## Coverage Matrix
[High-risk code/test surfaces with evidence, positive proof, falsifier attempted, result]

## Critic Coverage
[Assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring attacked. Required when Critic ran inline; concise when a sub-agent produced findings.]

## Verification Evidence
- Commands run: [with result]
- Commands skipped/unavailable: [with reason]

## Readiness
Ready / Needs Fixes / Blocked – with severity counts

## Next Steps
1. [Prioritized action items]
```


## Report Output Conventions

Filename and directory resolve per [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md). This lens contributes:
- **`<feature-name>` token**: the feature or primary changed-area name (e.g. `payments`, `auth-refresh`)
- **Report suffix**: `code-review` (canonical source: the `andthen:review` skill's mode table)
- **Target nature**: source-code. The location reference's source-code subdirectory guard applies – tier-2 "next to target" is disabled, so without a resolvable spec directory, current feature directory, or `--output-dir`, the report lands in `<agent-temp>/reviews/`.
