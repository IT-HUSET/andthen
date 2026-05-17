# Council Mode

Multi-perspective code or security review: 5-7 specialized reviewers find issues, a Critic Reviewer attacks assumptions, Devil's Advocate filters weak findings, and Synthesis Challenger produces the final low-noise report. Load this reference when running the `andthen:review` skill with `--council`, or when code/security mode auto-escalates to council because the scope spans multiple concerns, the surface is high-risk, or the user asked for "multi-perspective" / "adversarial" / "critic" / "skeptic" / "thorough" review.

Council mode augments **code mode** and **security mode** only. In a chain that includes both, run one council per applicable lens with distinct reviewer rosters and shared calibration.

Companion references:
- `reviewer-roster.md` – reviewer catalog, installed-agent mapping, and selection examples.
- `lens-code.md` – code-review rubric each code-mode specialist applies.
- `lens-security.md` – security-review rubric each security-mode specialist applies.
- [`lens-adversarial.md`](${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md), [`critic-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md), and [`review-calibration.md`](${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md) – Critic Reviewer posture and anti-leniency calibration.
- [`adversarial-challenge.md`](${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md) – Findings Filter prompt templates for Devil's Advocate and Synthesis Challenger.


## Gotchas

- Three roles are always included: Critic Reviewer, Devil's Advocate, Synthesis Challenger. Total sweet spot is 5-7 reviewers, so add 2-4 scope-relevant specialists on top. Above 7 dilutes debate quality.
- Skipping the Critic Reviewer under context pressure removes the primary assumption-attack pass.
- Skipping Devil's Advocate under context pressure removes the findings filter.
- Clean results still need proof of work. No surviving findings is acceptable only when `Coverage Attacked` names the assumptions, failure paths, and high-risk surfaces actually challenged.
- Devil's Advocate and Synthesis Challenger are filters. Devil's Advocate never adds findings. Synthesis Challenger may merge, split, reframe around evidence already present, downgrade, withdraw, or mark disputed, but must not invent unrelated findings.
- Forcing `--team` when Agent Teams are unavailable – fall back to sub-agents unless `--team` was explicit.


## Structured Finding Contract

Every specialist finding should use these fields so filters can compare results deterministically:

- `reviewer`
- `severity`: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- `confidence`: `0`, `25`, `50`, `75`, or `100`
- `location`
- `scope_relation`: `primary`, `secondary`, or `pre_existing`
- `finding`
- `threatened_assumption_or_invariant`
- `evidence`
- `impact`
- `suggested_fix`
- `verification_needed`


## 1. Determine Execution Mode

Prefer the strongest available execution path:

1. **Agent Teams available** or `--team` flag – Agent Teams path (§3a). Use installed custom review agents when the host supports naming them inside teams; otherwise spawn team members with inline persona prompts from `reviewer-roster.md`.
2. **Agent Teams unavailable, no `--team`** – sub-agent path (§3b). Prefer installed custom agents named in `reviewer-roster.md`; fall back to generic sub-agents with inline persona prompts; fall back to inline review only if sub-agents are unavailable.
3. **Agent Teams unavailable, `--team` present** – inform the user that Agent Teams are required and exit.


## 2. Select Council Members

Choose 5-7 reviewers from `reviewer-roster.md`. Always include **Critic Reviewer**, **Devil's Advocate**, and **Synthesis Challenger**.

For **security-mode councils**, always include **Security Sentinel** and choose 1-3 more specialists from `reviewer-roster.md` matched to the OWASP applicability gate: Correctness Reviewer for API, browser, backend, or data-flow behavior; Architecture Strategist for trust-boundary structure; Project Standards Reviewer for supply-chain, CI/CD, or local convention risk; Test Strategist for security verification gaps; Agent Workflow Reviewer for LLM/agent/tool-call flows.

For **code-mode councils**, select 2-4 specialists matched to the code-lens applicable subset: correctness, architecture, product/requirements, tests, project standards, UI/UX, prompt/agent workflow, or performance. Security Sentinel is optional in code mode because the code lens runs only thin security awareness; use a security-mode council for depth.

When a chain runs council on both lenses, run code council first and security council second. The rosters may differ, but each council keeps the Critic / Devil's Advocate / Synthesis Challenger spine.

**Gate:** 5-7 reviewers selected per lens.


## 3a. Agent Teams Path

Use Agent Teams so reviewers can share task state and debate in real time.

1. Create the team, e.g. `review-council`.
2. Create tasks for specialist review, findings filter, and synthesis.
3. Spawn each reviewer into the team. Prefer the installed custom agent mapped in `reviewer-roster.md`; still supply the same read-first task prompt below. Custom agent instructions are persona defaults, not a replacement for lens calibration.
4. Track assignments and completion.
5. Use inter-agent messaging for the filter debate.
6. Shut down team members and delete the team when finished.

**Reviewer task prompt:**

```markdown
Review Council for: {SCOPE}
Lens: {code|security}
Role: {reviewer name and focus areas from reviewer-roster.md}

Read the relevant lens rubric before reviewing:
- code council: references/lens-code.md
- security council: references/lens-security.md
- Critic Reviewer: ${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md plus ${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md and ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md

Apply your persona and the Critic posture inside your focus area. Return findings using the Structured Finding Contract from council-mode.md. If clean, return the concrete coverage you attacked.
```

**Phase 1 – Specialist Reviews:** wait for all specialists, including Critic Reviewer. **Gate:** specialist findings and clean-coverage statements collected.

**Phase 2 – Devil's Advocate Findings Filter:** Devil's Advocate filters every finding using `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md`. Verdicts: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, `DISPUTED`. Max 2-3 debate rounds per finding. **Gate:** verdicts applied.

**Phase 3 – Synthesis Review:** Synthesis Challenger reviews surviving and disputed findings holistically. It may merge, split, reframe around existing evidence, downgrade, withdraw, or mark disputed. It must not add unrelated new findings. **Gate:** final report payload complete.


## 3b. Sub-Agent Path

Run specialist reviews using parallel sub-agents where possible.

**Phase 1 – Specialist Reviews:** spawn one sub-agent per specialist, excluding Devil's Advocate and Synthesis Challenger. Critic Reviewer is a specialist and must be included. Prefer the installed custom agent mapped in `reviewer-roster.md`; still supply the same read-first task prompt. If custom agents are unavailable, spawn a generic sub-agent with this prompt:

```markdown
You are the {reviewer name} on a Review Council for: {SCOPE}

Focus areas: {focus areas from reviewer-roster.md}
Lens: {code|security}

Read the relevant rubric before reviewing:
- code council: references/lens-code.md
- security council: references/lens-security.md
- Critic Reviewer: ${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md plus ${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md and ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md

Apply your persona and the Critic posture inside your focus area. Return findings using the Structured Finding Contract from council-mode.md. If clean, return the concrete assumptions, flows, failure paths, and surfaces you attacked.
```

**Gate:** specialist findings and clean-coverage statements collected.

**Phase 2 – Devil's Advocate Findings Filter:** spawn `review-devils-advocate` when installed; otherwise use a generic sub-agent with `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` and this task:

- **Role**: `Devil's Advocate on a Review Council for: {SCOPE}`
- **Context block**: `You have received {N} findings from specialist reviewers.`
- **Questions**: Is this actually a problem? Is severity justified? Could this be a false positive? Is there an existing mitigation?
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`, `DISPUTED`
- **Findings payload**: `{all collected findings}`
- **Boundary**: filter only; do not add findings.

Apply verdicts to the findings list. **Gate:** findings filtered.

**Phase 3 – Synthesis Review:** spawn `review-synthesis-challenger` when installed; otherwise use a generic sub-agent with `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` and this task:

- **Role**: `Synthesis Challenger on a Review Council for: {SCOPE}`
- **Context block**: `You are the final quality gate. Review all findings that survived Devil's Advocate filtering.`
- **Questions**: Are severity ratings consistent? Are related findings one larger issue? Do validated findings imply a systemic pattern already evidenced by the payload? Are any survivors false positives in context?
- **Boundary**: may merge, split, reframe around existing evidence, downgrade, withdraw, or mark disputed; must not add unrelated new findings.
- **Findings payload**: `{validated, downgraded, and disputed findings from Phase 2 plus clean-coverage statements}`

**Gate:** synthesis complete.


## 4. Report Structure

When the caller writes a consolidated report, use this structure. Only findings that survived both filter phases appear in severity sections.

```markdown
# Review Council Report: {Scope}
Date: {YYYY-MM-DD}

## Executive Summary
{What was reviewed, lens, total findings, surviving findings, clean-result proof when applicable}

## Council Members
{Reviewers, installed-agent names when used, and focus areas}

## Coverage Attacked
{Assumptions, flows, failure paths, trust boundaries, requirements, and high-risk surfaces challenged}

## Guardrails
{Caller-supplied `Guardrails Coverage: N checked, M findings` line plus any guardrail-violation findings with rule sources}

## CRITICAL Severity (Validated)
## HIGH Severity (Validated)
## MEDIUM Severity (Validated)
## LOW Severity (Validated)

## Downgraded or Withdrawn Findings
{Finding, verdict, final severity when downgraded, concrete falsifier or severity rationale}

## Disputed Findings
{Finding and unresolved point of disagreement}

## Verification Gaps
{Commands, checks, documentation lookups, scans, or manual proofs still needed or unavailable}
```
