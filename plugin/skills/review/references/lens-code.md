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
5. **Security** — select the applicable checklist(s):

| Checklist | Standard | Apply when... |
|-----------|----------|---------------|
| [SECURITY-CHECKLIST-WEB.md](../checklists/SECURITY-CHECKLIST-WEB.md) | OWASP Top 10:2025 | Web applications, server-rendered pages, or any general-purpose backend |
| [SECURITY-CHECKLIST-API.md](../checklists/SECURITY-CHECKLIST-API.md) | OWASP API Security Top 10:2023 | REST, GraphQL, gRPC, microservices, or other HTTP-exposed code |
| [SECURITY-CHECKLIST-LLM.md](../checklists/SECURITY-CHECKLIST-LLM.md) | OWASP LLM Top 10:2025 | LLM, RAG, agentic, or AI-generated-output systems |
| [SECURITY-CHECKLIST-MOBILE.md](../checklists/SECURITY-CHECKLIST-MOBILE.md) | OWASP Mobile Top 10:2024 | Native or cross-platform mobile apps |
| [SECURITY-CHECKLIST-CICD.md](../checklists/SECURITY-CHECKLIST-CICD.md) | OWASP CI/CD Risks | Pipelines, IaC, deployment workflows, build scripts, supply chain changes |

Run available security tooling such as Semgrep (`../scripts/run-security-scan.sh <path>`) when possible.

When the review touches browser state, AI/agent flows, logs, stack traces, error output, scraped content, tool results, or other external-data flows, apply `${CLAUDE_PLUGIN_ROOT}/references/trust-boundaries.md`.


## Red-Team Sub-Lens (Always On)

Run `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md` against the same code scope as an always-on sub-lens. This is the finding pass for fragile assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring that constructive review can miss.

When code review delegates multiple specialist lenses to sub-agents, each specialist applies the Red-Team sub-lens to its own focus area. The final synthesis merges red-team findings into the normal severity sections before any Findings Filter runs.


## Calibration

Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` (universal) and `code-review-calibration.md` (code-specific). Load `${CLAUDE_PLUGIN_ROOT}/references/red-team-calibration.md` while running the always-on Red-Team sub-lens; use the code-specific calibration to assign final severity after findings are collected. Use the unified severity scale defined in `review-verdict.md`: CRITICAL / HIGH / MEDIUM / LOW.


## Verification Evidence

Run applicable project checks that strengthen review signal:
- **Build**: project's applicable build/package checks
- **Tests**: applicable test suites
- **Lint/types**: applicable static analysis, linting, type checks
- **Formatting**: formatter/compile sanity checks when relevant

When invoked standalone, treat those checks as part of the review evidence. When invoked by an orchestrator that already ran them, reuse fresh results when available instead of rerunning broad project checks unnecessarily. Report which verification commands were run, which were skipped, and why. Do not claim a clean review if a critical available check failed or could not be interpreted.


## Parallelization

When the review applies two or more lenses from the list above and sub-agents are supported, delegate each applicable lens to a parallel sub-agent. Otherwise run the same lenses sequentially inline.


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
- Security best practices: [Assessment]
- [UI/UX if applicable]: [Assessment]

## Verification Evidence
- Commands run: [with result]
- Commands skipped/unavailable: [with reason]

## Readiness
Ready / Needs Fixes / Blocked — with severity counts

## Next Steps
1. [Prioritized action items]
```


## Report Output Conventions

When writing a report file (not `--inline-findings`):
- **Filename**: `<feature-name>-code-review-<agent>-<YYYY-MM-DD>.md` — on collision append `-2`, `-3`. `<agent>` is your agent short name (`claude`, `codex`, etc.; fall back to `agent`).
- **Directory priority**:
  1. **Spec directory** — when the files being reviewed correspond to a feature that has an associated spec directory from the Project Document Index
  2. **Target directory** — next to the primary review target (the specific file or localized directory)
  3. **Fallback** — `{AGENT_TEMP}/reviews/` (default `.agent_temp/reviews/`)
- On completion, print the report's relative path from the project root.
