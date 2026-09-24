# Ubiquitous Language

> Canonical AndThen terms for code, docs, skill prompts, and review reports. Use these exact terms; avoid the listed synonyms.
>
> **Glossary and nothing else.** A term earns a row when getting its name wrong causes a defect – ambiguity, schema drift, misrouting. A row is one sentence under 200 characters: what the term is and where it lives. Mechanism, rationale, status, and open questions stay in the document that owns them – point, don't restate. A row that needs more is a spec in a cell.

## Core Terms
| Term | Definition | Avoid |
|------|------------|-------|
| AndThen | The lightweight spec-driven development framework for AI coding agents – the product, plugin, and installed skill bundle as a whole. | workflow toolkit, agent framework |
| Project Document Index | The list in a project's root agent instruction file that maps document types to locations. | docs table, path map |
| Shard | A topic file beside an indexed document, pointed at by one index line (`learnings/<topic>.md`, an ADR in `adrs/`); the index is read whole, a shard when the task names its topic. | topic file, sub-document, split doc |
| Key Dev Commands | The project's checks contract (Project Document Index; default `docs/KEY_DEVELOPMENT_COMMANDS.md`): the one source for build, format, lint/type, test, and run commands. | dev commands doc, command reference |
| Testing Strategy | The project's testing contract (Project Document Index; default `docs/TESTING-STRATEGY.md`): levels in use, framework and fixture conventions, the before-merge bar, and known gotchas. | test plan, testing guide |
| Visual Validation | The project's capture contract (Project Document Index; default `docs/VISUAL-VALIDATION.md`): serving, capture tooling, routes, states, breakpoints, references – never how a screen is judged. | Visual Validation Workflow, screenshot guide |
| Automation mode | Non-interactive behavior enabled by `--auto`: conservative assumptions and no prompts. | headless orchestration |

## Requirements and Planning
| Term | Definition | Avoid |
|------|------------|-------|
| Intent Document | The five-section `intent.md` – hand-written, or from the `andthen:clarify` skill under `--brief` on any subject; on a feature it is folded into the next PRD. In prose: intent doc. | intake, requirements clarification, clarification doc |
| PRD | The feature-scope requirements document `prd.md` written by the `andthen:clarify` skill; the record that survives the merge. | requirements doc, spec, product spec |
| Feature Implementation Specification (FIS) | Execution-sized specification for one story or standalone feature, authored by the `andthen:spec` skill and stored in the plan bundle. | spec, feature spec, implementation spec |
| Intent (FIS) | One-sentence statement under `## Feature Overview and Goal` naming why the feature exists – the problem solved or value unlocked. | feature description, summary, feature title |
| Expected Outcome | FIS-internal, behavioral, user-/business-observable success condition under `## Feature Overview and Goal`, tagged `[OC<NN>]`. | PRD outcome, success criterion, structural criterion |
| Outcome tag | `[OC<NN>]` token on an Acceptance Scenario, anchoring it to the Expected Outcome(s) it exemplifies. | scenario tag, OC reference |
| Required Context | Optional FIS section for load-bearing upstream sources. | background, references |
| Plan Bundle | Co-located planning directory containing `plan.json`, generated FIS files, `prd.md` when the source was one, and optional supporting assets. | implementation plan, plan folder |
| plan.json | Local typed runtime plan written by the `andthen:plan` skill and read by execution, review, and routing skills; runtime state is written by the run session alone. | plan.md, markdown plan, plan table, ledger |
| Story | Vertical, bounded, verifiable unit in `plan.json` that maps 1:1 to a FIS. | task, ticket, work item |
| Dependency-ready batch | Runtime-derived set of `spec-ready` or `in-progress` stories whose `dependsOn` stories are all `done`. | phase, wave, batch field |
| sourceRefs | `plan.json` story field for PRD feature IDs, anchors, and upstream requirement references that seed FIS context; Markdown label `Source refs`. | Source Refs, citations |
| assetRefs | `plan.json` story field for wireframes, ADRs, design-system references, or other upstream assets the FIS author needs; Markdown label `Asset refs`. | Asset Refs |
| bindingConstraints | `plan.json` top-level array of pointers (`featureId` + PRD `anchor`) to the spans that bind the plan; Markdown/prose section `Binding Constraints`. | hard requirements |
| sharedDecisions | `plan.json` top-level array of inter-story interface or design contracts referenced by producing and consuming stories; Markdown/prose section `Shared Decisions`. | cross-story notes |
| FIS Provenance | The FIS header fields `**Plan**:` and `**Story-ID**:` linking a plan-backed FIS to its source plan and story. | provenance header |
| Spike | Throwaway runnable code the `andthen:spike` skill builds on a `spike/<slug>` branch to answer one named design question. | prototype, PoC branch |
| Spike Verdict | The block the `andthen:spike` skill prints answering its one question. | spike result |
| Agent Brief | The `ready-for-agent` handoff block the `andthen:backlog-triage` skill appends to an issue body. | handoff comment |
| Tracker resolution | Resolving the `Issue Tracker` document before any issue operation, stated in full by the `andthen:backlog-triage` skill. | backend switch |
| Proportionality | The `PRODUCT.md` section stating the facts a proposal is sized against: stage, scale, and standing technical non-goals. | lean mode, complexity score, simplicity principles |
| Floor option | The smallest option that still satisfies the stated criteria – do nothing, or extend what exists – carried by every alternative set. | do-nothing baseline, minimal alternative, null option |
| Preflight | Closing step of the `andthen:spec` and `andthen:plan` skills: each open item asked in one sitting with a recommendation and answered into the FIS; exec-side pre-run checks are admission. | decision closure, convergence gate, closure verdict |
| Non-Goals | The `PRODUCT.md` section of product-level scope boundaries, firmly rejected concepts included as dated bullets – checked at the concept level before one is re-proposed. | Out of Scope Registry, rejection log |
| Context Map | The `docs/CONTEXT-MAP.md` document of bounded contexts and their integration patterns, registered by the `andthen:architecture` skill in `--mode strategic-design`. | context diagram |
| Atlas model | Either typed model the `andthen:describe` skill emits under `--model` – Architecture Model or Domain Model – committed under the `Models` location. | atlas view, 3D view |
| Architecture Model | The `andthen:describe` skill's typed `architecture-model.json`: a committed projection of the code – contexts, `ref`-anchored nodes, evidence-tagged edges. | dependency dump, code map |
| Domain Model | The `andthen:describe` skill's typed `domain-model.json`: a committed projection of the Ubiquitous Language – contexts, term nodes, overloaded meanings. | glossary dump, term map |
| Single-session rule | The `andthen:plan` skill's story-sizing rule: a story plus its FIS must fit one fresh-context exec run. | story budget |
| Canonical triage roles | The `andthen:backlog-triage` skill's fixed label set – states `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`; categories `bug`, `enhancement`. | triage statuses |

## Execution and Review
| Term | Definition | Avoid |
|------|------------|-------|
| Stop-the-Line | Execution discipline that treats objective red gates as work to finish before advancing or claiming completion. | fail-fast, stop work |
| Objective Red Gate | Binary failing check such as build, test, lint, type-check, wiring check, or task Verify line. | blocker |
| Subjective Finding | Review or visual-validation finding that requires judgment rather than a binary check. | review issue |
| Verification tier | `Key Dev Commands` tier: `fast` for each plan story; `full` for direct FIS execution or a plan run at convergence. | quick tests, full suite |
| Traceability Gate | Requirement that tests and motivated code changes trace to FIS requirements or explicitly appended discovered requirements. | trace check |
| Discovered Requirement | Requirement found during execution and appended through the sanctioned FIS channel before dependent tests or code are written. | inferred requirement |
| Finding | Concrete review issue with severity, evidence, and remediation guidance. | comment, issue |
| Findings Filter | Calibration pass that challenges candidate findings before final severity and report inclusion. | triage pass |
| Self-review | The fresh-context reviewer pass an authoring skill runs over the document it just wrote (`clarify`, `spec`, `plan`), loading a rubric rather than a review lens. | doc review, document review |
| Gap Review | Review lens comparing implementation against a requirements baseline and emitting the PASS/FAIL contract. | requirement review |
| Outcome Review | Review lens validating a finished feature against its PRD's problem, users, and success metrics by walking it as those users; readiness on the code-mode scale. | product review, acceptance review, retrospective |
| Per-story review | The one review inside a story: a fresh reviewer subagent invoking the `andthen:review` skill with `--quick` over the changed paths, on every run. | gate verdict, coordinator diff pass |
| Task progress | Stable task IDs in `stories[].completedTaskIds`, appended as each task's `Verify` passes. | checked tasks, FIS state |
| Proof lines | The story's evidence, produced by `exec-spec` where it runs: one line per `Proof` or `Verify` id – what ran and its exit code, or what was seen. | verifier, verifier report, proof report |
| Completion transition | The run session's write of `status: "done"` together with `verified: {at, summary}`, whose summary quotes executed proof output. | mark done, status write |
| Close-out | Deleting the branch-scoped `plan.json` and FIS files before the merge, after landing each FIS's Implementation Observations in Learnings or Decisions; no verb, and `prd.md` stays. | plan cleanup, archive the plan, teardown |
| FIS head | The three-to-eight-line summary of a FIS – `Story-ID`, `Intent`, and up to five `Expected Outcomes` – carried into the squash-merge message, where it survives the bundle's deletion. | commit summary, merge blurb |
| plan.schema.json | The machine form of `plan-schema.md` (JSON Schema draft 2020-12), a shared canonical in `plugin/references/`. | plan schema file, the JSON schema |
| `Reviewed:` line | The completion report's one review signal: what reviewed the change, which findings were fixed, and what stays open. Prose for the reader, never parsed. | gate result, story verdict |
| Scope Discipline | The `review-calibration.md` counterweight to the Anti-Leniency Protocol – Analysis Paralysis, Finding Distillation, Verdict first. | proportionality, going easy |
| Follow-up review | A `review` run the request scopes to the latest report's findings and their fixes; a full run with its own report and verdict. | closure pass, review campaign, re-review round |
| Anchor move | A routing decision `intent-and-rules-context.md` defines against the Intent bundle, named in one cited clause. | intent check, guardrail rule |
| Implement Fix | Workflow run by the `andthen:implement-fix` skill to turn a request or a review report's findings into re-validated minimal fixes, verify them, and update workflow state. | quick implement, address comments, remediate findings |
| Tech Debt Backlog | Durable backlog for deferred validated findings that cannot be fixed in the current remediation pass. | parking lot |
| Admission test | The agent's judgment before a durable-store write, never a script check: does a frontier model already know this, does code or git history carry it, does it outlive the initiative? | quality bar, entry filter |
| Drift Note | One line under `#### DRIFT` in a FIS `## Implementation Observations`, recording deliberate code↔FIS divergence and any upstream doc it leaves stale. | reconciliation ledger, drift log |
| Run Ledger | In-memory aggregate (`completed`/`failed`/`skipped`/`blocked_by`) the `andthen:exec-plan` skill keeps during a multi-story run to feed the aggregate report. | run log |

## Protocols
| Term | Definition | Avoid |
|------|------------|-------|
| Interactive-by-Contract | Rule that every `andthen:clarify` run includes user-answered discovery questions and a confirmed shared understanding before producing its artifact; there is no unattended form. | optional interactivity, headless clarify |
| Recommend, don't decide | Clarification posture: offer a defensible recommended answer while requiring the user to ratify or redirect it. | assume the recommendation |
| ASSUMPTION: | Record of the safest defensible reading where nobody decided – in a FIS, a Preflight item left unanswered or settled under `--auto`. | silent default |
| Next-step decision | The one command an authoring skill closes on, once every open item is closed. | follow-up menu, next steps list |
| Proof-of-Work | FIS rule that each Acceptance Scenario has an articulated contract and a concrete proof path, and each Structural Criterion is proved by a task Verify line. | proof note |
| Prove-It Pattern | Test-first bugfix flow where a failing test proves the defect before the fix makes it pass. | regression test after fix |
| Anti-Cheat Invariant | TDD rule that a proof test cannot be deleted, disabled, or weakened to make the build green. | weaken the test |

## Distribution
| Term | Definition | Avoid |
|------|------------|-------|
| Shared Plugin Asset | Canonical file under `plugin/references/` consumed by multiple skills and inlined during generic/user-tier installs. | shared reference, shared doc |
| Generic Subagent | The one delegation shape AndThen uses: a host-provided general subagent whose prompt invokes a skill or loads a reference. | custom agent, persona agent, docs agent, sub-agent |
| Role Agent | One of four opt-in subagent definitions – `oracle`, `implementer`, `reviewer`, `worker` – shipped as templates by the `andthen:init` skill and installed at user or project level. | tier agent, model agent, oracle skill, reviewer agent |
| Live Eval Run | One eval case dispatched to a real model through DartClaw – a cell per case and host under the `smoke` or `full` tier; the user is asked before it starts. | paid run, paid cell, paid eval, benchmark |

## Overloaded Terms
| Term | Context A | Meaning A | Context B | Meaning B |
|------|-----------|-----------|-----------|-----------|
| spec | General discussion | Any specification-like document | AndThen planning | Prefer FIS for the execution artifact generated by the `andthen:spec` skill |
| plan | Skill/prose | The `andthen:plan` skill or planning act | Artifact | `plan.json`, the typed local runtime plan |
| story | Product requirements | User story in a PRD or Intent Document | Plan bundle | A `stories[]` entry that maps 1:1 to a FIS |
| review | Skill | The unified workflow run by the `andthen:review` skill | Report content | Findings, verdict, and evidence produced by a lens or chain |
| agent | User environment | An AI coding agent such as Claude Code, Codex, Aider, or Cursor | AndThen delegation | A generic subagent spawned by a skill |
| Intent | FIS field | The one-sentence `Intent` under `## Feature Overview and Goal` – why this feature exists | Artifact | `intent.md`, the Intent Document that precedes the PRD |
| Intent | Review/remediation loader | `Intent Context` – the governing-artifact bundle collected as falsifiers per `intent-and-rules-context.md` | Artifact | `intent.md` is at most one member of that bundle, never the bundle itself |
| context | Prompt/runtime | Model context or fresh-session context | FIS | The Required Context section carrying upstream intent |
| context | Domain design | Bounded Context in DDD | Project discovery | Project context loaded from root agent instructions |
| state | Workflow artifact | Runtime fields in the schema v2 `plan.json` governing the story – a standalone feature has a one-story plan of its own | Plan status | `stories[].status` values inside `plan.json` |
| owner | Plan coordination | `stories[].owner` in `plan.json` – who is executing a story; advisory, not a lock | Code ownership | Reserve `owner` for story claiming, not file/CODEOWNERS semantics |
| issue | GitHub integration | A GitHub issue read as a requirements or scope source | Review | A finding; prefer Finding |
| asset | Install system | Shared Plugin Asset under `plugin/references/` | Plan schema | `assetRefs` pointing to upstream assets |
