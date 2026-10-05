---
description: First-stop router – inspects project state and routes to the right AndThen skill. Trigger on 'where do I start', "I'm stuck", 'is this a PRD or a spec'.
argument-hint: "[brief description of what you want to do]"
---

# Now What

Inspect project state and route the user to the one AndThen skill that fits next.

## Input

`$ARGUMENTS` is what the user wants to do (`REQUEST`), possibly empty.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Detect first, ask second.** Ask only what state cannot reveal: the user's actual idea or framing.
- **Two questions at most, never a menu.** One to hear the idea, one to disambiguate, then commit.
- **One handoff per invocation.** For a sequenced route, recommend the first hop and have the user invoke the `andthen:now-what` skill again; never auto-chain.
- **One line per recommended skill.**
- **Use the user's words, not workflow vocabulary.** A first-time user does not know "FIS" or "PRD": introduce the term at handoff.

## Workflow

**1. Detect state.** Compute setup, codebase, and workflow **independently**: none decides another, so a stub never hides an active plan. Ends on the state vector, such as `setup: done | codebase: greenfield | workflow: nothing-in-progress`.

- **Setup** – the host loads the root instruction file into your context; never read it from disk. None reached you → `setup: not-started`. It lacks the `## Project Document Index` or `## Project-Specific Guidelines and Rules` heading → `setup: partial`.
- **Codebase** – `git ls-files` count and extension distribution; the rough cut is >50 tracked files with substantive code extensions. Substantial code and no map → `codebase: brownfield-unmapped`. A map at its **Project Document Index** location – a filled-in `Architecture` document, or `requirements-discovered.md` / `decisions-discovered.md` – → `codebase: brownfield-mapped`.
- **Workflow** – read the **Project Document Index** and check its paths for any of these; any → `workflow: mid-flow`, the position inferred from the artifact type:
  - `intent.md`, `prd.md`, `plan.json`, FIS files (`s[0-9][0-9]-*.md`)
  - review reports with unaddressed findings (`*-review-*.md`; a clean or remediated report alone is retained evidence, not active state)
  - the most recent architecture report (`*-architecture-*.md`) and ui-ux-design output (wireframes, design system)

**2. Pick the branch.** First matching row wins; ends on one branch:

| State vector | Branch |
|---|---|
| `workflow: mid-flow` | **D – Mid-flow** – active work first; a `setup: partial` gap is one advisory line, not a detour |
| `setup: not-started` or `setup: partial` | **A – Setup** |
| `codebase: brownfield-unmapped` | **B – Brownfield mapping** |
| `workflow: nothing-in-progress` | **C – Starting a feature** |

**3. Route.** Ends on one route, printed in the Output format.

### A – Setup not done

Name the chain once – clarify (optional) → plan → exec-plan → review --fix → ship – then offer the `andthen:init` skill.

### B – Brownfield codebase, no map yet

Offer the `andthen:describe` skill in `--mode codebase`; on decline, fall through to Branch C.

### C – Starting a feature

**Hear the idea.** If `REQUEST` is empty, ask one open question: _"What do you want to build, change, or figure out?"_

**Classify the request silently, and commit.** Match the framing against the skills' frontmatter `description` fields. They leave two things unsettled:

- **Scope and completeness.** Requirements still open (vague outcome, unnamed users, unsettled scope) → the `andthen:clarify` skill. Settled requirements – inline, a `prd.md`, a requirements file, or a tracker item → the `andthen:plan` skill whatever the size.
- **Genuine ambiguities** – one phrasing, two skills:
  - "X vs Y", "which is better/faster", "decide between", "write an ADR" – settleable by analysis → the `andthen:decide` skill; only measurement settles it → the `andthen:spike` skill.
  - "model the domain" – naming and term consistency → the `andthen:describe` skill in `--mode domain`; context boundaries and subdomain carving → the `andthen:architecture` skill in `--mode strategic-design`, or `--mode event-storming` on that explicit cue.

**Disambiguate only when needed.** When the framing is genuinely ambiguous between two shapes, ask **one** question: requirements or technical decisions (`clarify` vs `decide`), whole initiative or one slice. Then commit to the likeliest route; the downstream skill redirects if it is wrong.

### D – Mid-flow

Mid-flow, do not onboard: no recap.

**Freshness gate.** When the framing suggests new work ("let's start something new") and the mid-flow signal is a stale artifact (a paused FIS, a plan whose stories have not moved), take Branch C. When in doubt, ask: "Continuing, or starting something new?"

First match wins, top-down. *The plan review* is the latest review report beside `plan.json` whose `**Target**:` is `plan <plan.json>`.
When every plan story is `done` or `skipped`, read [`plan-schema.md`](../../references/plan-schema.md) § Shipping for readiness.

- **`intent.md` present, no sibling `prd.md` or `plan.json`** – the `andthen:clarify` skill, which folds it into the PRD.
- **`prd.md` exists, no `plan.json`** – the `andthen:decide` skill when it leaves open a design fork the `Decisions` document does not settle; else the `andthen:ui-ux-design` skill when its `Decisions Log` puts design before planning and no wireframes cover it yet; else the `andthen:plan` skill.
- **`plan.json` with a story neither `done` nor `skipped`** – the `andthen:exec-plan` skill: on the FIS for a one-story plan, else on the plan directory.
- **Review report present (any lens) with findings and no `## Remediation Status`** – the `andthen:implement-fix` skill.
- **Every plan story `done` or `skipped`, and no plan review yet, or its `## Remediation Status` marks a CRITICAL or HIGH finding RESOLVED or a Fix finding PARTIALLY RESOLVED or UNRESOLVED** – the `andthen:review` skill on `<plan.json>` with `--fix`, because fixes need a reading their own session did not write.
- **Every plan story `done` or `skipped`, and the plan review has a CRITICAL or HIGH finding `DEFERRED`** – `Next: blocked –`; once the user decides, the `andthen:implement-fix` skill on the report, carrying that decision.
- **Every plan story `done` or `skipped`, and the plan review reports a failing load-bearing check** – name the check and route to the `andthen:triage` skill with the failure and review report.
- **Every plan story `done` or `skipped`, otherwise** – if § Shipping holds, the branch is ready: the `andthen:ship` skill. Else `Next: blocked –` with the unmet condition.
- **Architecture report present (any mode), no obvious follow-on** – the `andthen:decide` skill on the report.
- **UI/UX wireframes or design-system output, no plan** – the `andthen:plan` skill on the requirements they were drawn from.
- **UI/UX wireframes implemented, no visual validation on this branch** – the `andthen:visual-validation` skill.
- **User says "stuck" with mid-flow state** – ask: "What did you last do, and what's not behaving as expected?"

## Output

Name the workflow position, print the recommended invocation on its own line, then ask `Run it? (Y/n)`.

Two routes print in place of that format and end the run:

- **`Next: blocked –`** and what keeps the plan from meeting § Shipping, each deferred finding with its blocker: clearing it is the user's decision.
- **`Next (fresh session):`** and the `andthen:ship` skill on `<plan.json>`.

## Follow-up

- **Invoke** the recommended skill, passing `REQUEST` through where its input takes it, never to the `andthen:init` skill, whose argument is a project name. When the user declines, or the request asks for a recommendation only, print the route and stop there.
- **Answer "what does X do?" from the target skill's frontmatter `description`**, or its SKILL.md when the question needs flag or mode depth, then offer to invoke. Never from memory.
