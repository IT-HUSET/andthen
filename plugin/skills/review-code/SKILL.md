---
description: Perform thorough code reviews covering code quality, security, architecture, and UI/UX. Use when reviewing code changes, PRs, implementations, or when asked to review, audit, or assess code quality. Generate detailed reports with prioritized findings.
user-invocable: true
argument-hint: "[scope/files] [--to-issue] [--to-pr <number>]"
---

# Code Review Skill

Comprehensive code review covering correctness, security, architecture, maintainability, and UI/UX where relevant.

## VARIABLES
ARGUMENTS: $ARGUMENTS

### Optional Output Flags
- `--to-issue` → PUBLISH_ISSUE
- `--to-pr <number>` → PUBLISH_PR

## INSTRUCTIONS
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Analysis only. Do not modify code.
- Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and `references/code-review-calibration.md`.
- Read project learnings if they exist.
- Exclude generated, vendored, and lockfile noise.

## GOTCHAS
- Over-reporting nits
- Forgetting Semgrep when it is available
- Reviewing generated output instead of human-authored code

### Helper Scripts
- `${CLAUDE_PLUGIN_ROOT}/scripts/run-security-scan.sh <path>`

## ORCHESTRATION
When supported, delegate parallel reviewers for:
1. Code quality
2. Security
3. Architecture
4. Domain language
5. UI/UX

If sub-agents are unavailable, run the same lenses sequentially.

## WORKFLOW

### 1. Scope
Determine scope from conversation context, explicit paths, PR number, or current pending changes. Build a quick codebase overview, identify affected files, choose the applicable review lenses, and verify external technical claims against authoritative sources when needed.

**Gate**: Scope and applicable review lenses are clear

### 2. Review
- **Code quality** — use [CODE-REVIEW-CHECKLIST.md](checklists/CODE-REVIEW-CHECKLIST.md): correctness, edge cases, readability, naming, maintainability, performance, duplication
- **Architecture** — use [ARCHITECTURAL-REVIEW-CHECKLIST.md](checklists/ARCHITECTURAL-REVIEW-CHECKLIST.md): pattern adherence, coupling/cohesion, CUPID, DDD where relevant, resilience/performance trade-offs
- **Domain language** — use [DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md](checklists/DOMAIN-LANGUAGE-REVIEW-CHECKLIST.md) when `UBIQUITOUS_LANGUAGE.md` exists: terminology consistency
- **UI/UX** — use [UI-UX-REVIEW-CHECKLIST.md](checklists/UI-UX-REVIEW-CHECKLIST.md) when UI changed: usability, responsiveness, accessibility, interaction quality

#### Security Review
Select the applicable checklist(s):

| Checklist | Standard | Apply when... |
|-----------|----------|---------------|
| [SECURITY-CHECKLIST-WEB.md](checklists/SECURITY-CHECKLIST-WEB.md) | OWASP Top 10:2025 | Web applications, server-rendered pages, or any general-purpose backend |
| [SECURITY-CHECKLIST-API.md](checklists/SECURITY-CHECKLIST-API.md) | OWASP API Security Top 10:2023 | REST, GraphQL, gRPC, microservices, or other HTTP-exposed code |
| [SECURITY-CHECKLIST-LLM.md](checklists/SECURITY-CHECKLIST-LLM.md) | OWASP LLM Top 10:2025 | LLM, RAG, agentic, or AI-generated-output systems |
| [SECURITY-CHECKLIST-MOBILE.md](checklists/SECURITY-CHECKLIST-MOBILE.md) | OWASP Mobile Top 10:2024 | Native or cross-platform mobile apps |
| [SECURITY-CHECKLIST-CICD.md](checklists/SECURITY-CHECKLIST-CICD.md) | OWASP CI/CD Risks | Pipelines, IaC, deployment workflows, build scripts, supply chain changes |

Assess input validation, injection risks, authz/authn, crypto, secret handling, API security, and supply-chain integrity. Run available security tooling such as Semgrep when possible.

**Gate**: Applicable review lenses complete

### 3. Findings and Report
Categorize findings as:
- **CRITICAL**: security vulnerabilities, data loss, or broken core behavior
- **HIGH**: significant maintainability, performance, or correctness issues
- **SUGGESTIONS**: worthwhile improvements or cleanup

Also flag obsolete files, unmotivated complexity, and cleanup candidates.

Generate a markdown report:

```markdown
# Review Report - [Date]

## Summary
[2-3 sentence overview]

## CRITICAL ISSUES
[Title, impact, location, fix required]

## HIGH PRIORITY
[Title, impact, location, recommendation]

## SUGGESTIONS
[Brief list]

## Cleanup Required
- [Obsolete or temporary files]
- [Dead code]

## Compliance
- Guidelines adherence: [Assessment]
- Architecture patterns: [Assessment]
- Security best practices: [Assessment]
- [UI/UX if applicable]: [Assessment]

## Next Steps
1. [Prioritized action items]
```

**Report output conventions**: Follow `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md` with:
- **Report suffix**: `code-review`
- **Scope placeholder**: `feature-name`
- **Spec-directory rule**: the files being reviewed correspond to a feature that has an associated spec directory from the Project Document Index
- **Target-directory rule**: the review target is a specific file or localized directory, so the report belongs next to the primary review target

### Publish to GitHub
If PUBLISH_ISSUE is `true`:
1. Follow the optional GitHub publishing flow in `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
   Title template: `[Code Review] {scope}: Review Report`
2. Print the issue URL

If PUBLISH_PR is set:
1. Follow the optional GitHub publishing flow in `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
   Publish target: typed PR comment. If the posting command does not return a direct comment URL, resolve it via follow-up GitHub lookup before completing
2. Print the direct comment URL
