# Council Mode

Multi-perspective review scaled to the chain shape: **within-lens specialist councils** (5-7 reviewers per lens) deepen `code` and `security` reviews, and on any chain of 2+ lenses a **cross-lens Critic + Devil's Advocate + Synthesis Challenger pass** attacks lens-boundary surface (contradictions, silence-licenses-risk, verdict-vs-finding mismatch) over the merged finding set. Load this reference when running the `andthen:review` skill with `--council`, or when code/security mode auto-escalates to council because the scope spans multiple concerns, the surface is high-risk, or the user asked for "multi-perspective" / "adversarial" / "critic" / "skeptic" / "thorough" review.

Within-lens specialist councils apply to `code` and `security` only; on a chain that includes both, run one specialist council per lens with distinct reviewer rosters and shared calibration, then run the cross-lens pass once over all per-lens outputs.

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

The 5-7 sweet spot and specialist selection below apply to **within-lens** councils (code or security). The **cross-lens chain pass** (§ *Cross-Lens Chain Mode* below) is fixed at the 3-role spine – no additional specialists – because per-lens reviews already produced the specialist coverage.

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


## 3c. Cross-Lens Chain Mode

**Trigger**: `--council` AND chain (2+ lenses). Runs once after every per-lens review (and any within-lens council) completes, before the consolidated chain report is written.

**Roles**: the find / filter / synthesize spine only – **Cross-Lens Critic** (finder, primary finding-producing role at this scope), **Devil's Advocate** (filter), **Synthesis Challenger** (filter). No additional specialists – per-lens reviews already produced specialist coverage. Tag every finding produced here with `reviewer: Cross-Lens Critic`, `scope_relation: primary`, and `source_lens: cross-lens` so downstream routing keeps the existing scope contract while filters and the consolidated report can distinguish them from per-lens findings.

**Inputs**: target map + per-lens finding payloads tagged by source lens. Where a within-lens code or security council ran (§3a / §3b), use its **filtered** output (post-Devil's-Advocate, post-Synthesis-Challenger), not raw specialist findings.

**Phase 1 – Cross-Lens Critic** (finder): spawn the installed `review-critic` agent when available; otherwise a generic fresh-context sub-agent. Same agent persona as the within-lens Critic, different task prompt:

```markdown
You are the Cross-Lens Critic on a Review Council for: {SCOPE}

Lenses run: {ordered lens list, e.g. doc, code, gap}
Per-lens finding payloads (tagged by source lens):
{merged findings}

Read first:
- ${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md
- ${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md
- ${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md

Attack lens-boundary surface only:
- Contradictions between lens outputs (lens A passes, lens B's finding implies A should fail).
- Silence-licenses-risk – one lens's PASS is being used to license another lens's silence.
- Cross-lens coupling missed by every per-lens scope.
- Verdict-vs-finding mismatch within or across lenses.
- Intent gaps visible only when code is read against doc, or doc against code.

Do **not** re-litigate within-lens Critic findings – assume the per-lens Critic pass attacked within-lens scope already. Return findings using the Structured Finding Contract; tag `scope_relation: primary` and `source_lens: cross-lens`. If clean, return the concrete lens-boundary surfaces you attacked.
```

**Gate:** cross-lens findings (or clean-coverage statement) collected.

**Phase 2 – Devil's Advocate**: reuse the §3a / §3b Devil's Advocate task prompt verbatim. Filter posture is scope-agnostic. Inputs are the per-lens findings (already-filtered when a within-lens council ran) **plus** the cross-lens Critic findings. **Gate:** verdicts applied.

**Phase 3 – Synthesis Challenger**: reuse the §3a / §3b Synthesis Challenger task prompt verbatim. May merge duplicates across lenses, reframe around evidence already present, downgrade, withdraw, or mark disputed; must not invent unrelated findings. **Gate:** final cross-lens payload complete.

The caller (SKILL.md Step 5) renders surviving cross-lens findings in the consolidated chain report's `## Cross-Lens Synthesis` section above the per-lens sections, with a `Coverage attacked:` proof-of-work line. Per-lens sections remain intact.


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
