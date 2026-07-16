---
description: First-stop router – inspects project state (init'd? greenfield? brownfield? mid-flow?) and routes to the right AndThen skill. Trigger on 'where do I start', 'now what', "I'm stuck", 'is this a PRD or a spec'.
argument-hint: "[--auto] [--no-handoff] [brief description of what you want to do]"
---

# Now What

Reads project state, routes to the right skill – heavy onboarding for first-time setup, lighter touch mid-flow.


## VARIABLES

ARGUMENTS: $ARGUMENTS _(optional – what the user wants to do, e.g. "build a todo app", "should I use Postgres or SQLite", "I'm stuck", or empty)_

### Optional Flags
- `--no-handoff` → Emit recommendation only; do not invoke the downstream skill. For users who want to read before committing.


## INSTRUCTIONS

- **Detect first, ask second.** State already tells you most of what you need. Only ask the user what state cannot reveal (their actual idea or framing).
- **Two questions max; never a menu.** One question to hear the idea, one to disambiguate if genuinely ambiguous – then commit to a route. Never a numbered "Choose-Your-Own-Adventure" menu of skills.
- **One handoff per invocation.** If a route involves a sequence (e.g. `architecture --mode advise` → `clarify`), recommend the first hop and ask the user to re-invoke `now-what` after, rather than auto-chaining.
- **Do not re-implement downstream work.** Mention each recommended skill in one line; let its description and prompt do the rest.
- **Use the user's words, not workflow vocabulary.** A first-time user does not yet know "FIS" or "PRD" – match them where they are, then introduce the term when handing off.
- **Automation mode.** Under `--auto`, skip the open-question step in Phase 3 and the disambiguation question in Phase 4's freshness gate; if `$ARGUMENTS` is empty or state-detection plus a single silent classification pass cannot commit to a route, exit with `BLOCKED: now-what cannot route headlessly without an idea or unambiguous mid-flow state`.


## GOTCHAS
- This skill must hand off in-place, so it intentionally omits `context: fork` from frontmatter – do not add it.


## WORKFLOW

### Phase 1 – State Detection

Read these signals **in order; stop at the first state-determining match.** Most paths are deterministic (no question); one row has a fallback question for genuinely ambiguous codebase volume – when used, it counts as the one disambiguation question allowed by the two-question budget, so do not also ask in Step 3. Reuse `init`'s vocabulary (`New project` / `Partial setup` / `Brownfield`) where it overlaps so terms stay consistent across skills.

| Signal | How to read | Outcome |
|---|---|---|
| `CLAUDE.md` or `AGENTS.md` at project root? | File exists | If no → `setup: not-started` |
| `## Project Document Index` and `## Project-Specific Guidelines and Rules` in the root agent instruction file(s)? | Check every existing root instruction file. A single existing file may carry the contract; when both `CLAUDE.md` and `AGENTS.md` exist, both must carry the shared workflow sections. | If no → `setup: partial` |
| Source code beyond config/README? | `git ls-files` count + extension distribution. Rough cut: >50 tracked files with substantive code extensions. **If genuinely unclear** (small repo, mixed signals), ask one question: "Is this a fresh project or are we working with existing code?" | If yes & no map → `codebase: brownfield-unmapped` |
| Map-codebase output present? | Files matching `project-state-templates.md` outputs (Architecture, Stack, etc.) per **Project Document Index** | If yes → `codebase: brownfield-mapped` |
| Any in-flow artifact at indexed paths? | Read the **Project Document Index** and check for `requirements-clarification.md`, `prd.md`, `plan.json` (or legacy `plan.md`), standard plan-story FIS files (`s[0-9][0-9]-*.md`), standalone FIS docs by shape (`## Feature Overview and Goal` + `## Acceptance Scenarios`), `STATE.md` / `STATE.local.md` (the gitignored per-developer state – a mid-flow signal even when shared state is absent), the most recent architecture-report (`*-architecture-*.md`<sup>†</sup>), the most recent triage-report (`*-triage-*.md`), and the most recent ui-ux-design output (wireframes / design-system / design-review). | If any → `workflow: mid-flow` (and infer where in flow from the artifact type) |

<sup>†</sup> The `andthen:architecture` skill emits the single suffix `architecture` for all 7 modes; differentiate trade-off / strategic-design / event-storming etc. by reading the report's H1/H2, not the filename.

**Output**: a state vector like `setup: done | codebase: greenfield | workflow: nothing-in-progress`. This drives Phase 2.


### Phase 2 – Branch Selection

| State vector | Branch |
|---|---|
| `setup: not-started` or `setup: partial` | **A – Setup / Onboarding** |
| `setup: done | codebase: brownfield-unmapped` | **B – Brownfield Mapping** |
| `setup: done | workflow: nothing-in-progress` | **C – Starting a Feature** (the heart of the skill) |
| `setup: done | workflow: mid-flow` | **D – Mid-Flow Navigation** |


### Phase 3 – Onboarding Flow (Branches A / B / C)

When the user is new to AndThen on this project, they need a mental model **before** a routing decision – but in layers, not as a dump.

#### Branch A – Setup not done

Open with the mental model in three lines, no more:

> AndThen guides features through a disciplined chain: **clarify → (spec → exec-spec) or (prd → plan → exec-plan) → review**. There are also optional design tools (architecture, UI/UX, glossary, diagrams). First we need to set up the workflow structure in this project.

Recommend the `andthen:init` skill and offer to invoke, passing `$ARGUMENTS` through as project name when relevant. After `init` returns the invocation ends – tell the user to invoke the `andthen:now-what` skill again to continue.

#### Branch B – Brownfield codebase, no map yet

> This codebase has substantial existing code that AndThen has not analyzed yet. Mapping it first means later skills (clarify, spec, architecture) can reason about what already exists rather than treating the repo as empty.

Recommend and offer the `andthen:map-codebase` skill; on accept hand off (invocation ends, user re-invokes after), on decline note the trade-off briefly and fall through to Branch C in the same invocation.

#### Branch C – Starting a feature (the most important onboarding path)

This is where users get lost: AndThen is set up, they have an idea, but they do not yet know whether they need `clarify`, `prd`, `spec`, `quick-implement`, `architecture`, `ui-ux-design`, or some combination.

**Step 1 – Hear the idea (1 question max).** If `$ARGUMENTS` is empty, ask one open question (_"What do you want to build, change, or figure out?"_); skip if it already has content.

**Step 2 – Classify the request shape silently** against the table and commit – do not ask the user to pick.

| Request shape | Cue phrases | Route |
|---|---|---|
| Product vision / overall product | "product vision", "overall product", "what should this product be", "before we plan features", "positioning" | → the `andthen:clarify` skill in `--mode product` |
| Build a single feature | "add X", "implement Y", "I want users to be able to Z" | → the `andthen:clarify` skill (default feature mode) |
| Build a bigger initiative | "build a whole X", multiple capabilities mentioned, "platform", "system" | → the `andthen:clarify` skill (default feature mode; entry point for the multi-feature `prd → plan → exec-plan` chain). If the framing carries architectural ambiguity ("multi-tenant", "real-time", "how should I structure a..."), use Step 3 to disambiguate between `clarify` and the `andthen:architecture` skill in `--mode advise`. |
| Quick fix / small change | "fix typo", "rename X", "bump version" | → the `andthen:quick-implement` skill |
| Simplify existing code | "simplify this code", "clean this up", "refactor this", "reduce complexity" | → the `andthen:simplify-code` skill |
| How should I structure X? | "how do I organize", "what's the right pattern for" | → the `andthen:architecture` skill in `--mode advise` |
| Compare two approaches | "X vs Y", "should we use A or B" | → the `andthen:architecture` skill in `--mode trade-off` |
| Module split / merge decision | "should we split this", "decompose", "boundaries" | → the `andthen:architecture` skill in `--mode decompose` |
| Domain discovery / subdomain mapping / context boundaries | "bounded contexts", "subdomains", "domain map", "what are our domains", "model the domain", "event storming" | → the `andthen:architecture` skill in `--mode strategic-design` _(or `--mode event-storming` when "event storming" is the explicit cue)_ |
| UI screens or flow | "screens", "wireframes", "user flow" | → the `andthen:ui-ux-design` skill in `--mode wireframes` |
| Design system / tokens | "style guide", "colors and typography", "design tokens" | → the `andthen:ui-ux-design` skill in `--mode design-system` |
| Domain language / glossary | "glossary", "terminology", "what should we call" | → the `andthen:ubiquitous-language` skill |
| Something is broken | "bug", "error", "build failing", "test failure" | → the `andthen:triage` skill |

**Step 3 – Disambiguate only when needed.** If the framing is genuinely ambiguous between two shapes, ask **one** question. Examples:

- "Sounds like a single feature. Want me to dig into requirements first (`clarify`), or is the design question more pressing (`architecture --mode advise`)?"
- "This sounds bigger than one feature – multiple capabilities. Treat it as a multi-feature initiative (PRD + plan), or focus on one slice first?"

If still ambiguous after one question, commit to the most likely route; the downstream skill redirects if wrong.

**Step 4 – Surface the optional tools, once.** After committing to a route, mention in two lines what *else* exists, so the user knows the toolkit:

> "You're going into `clarify` next. Heads up that AndThen also has the `andthen:architecture`, `andthen:ui-ux-design`, `andthen:ubiquitous-language`, and `andthen:excalidraw-diagram` skills – useful as you go deeper. Use the `andthen:now-what` skill any time you're unsure what's next."

Then hand off via the Skill tool with the user's idea passed through.


### Phase 4 – Mid-Flow Navigation (Branch D, light touch)

When state shows the user is mid-flow, do not onboard. Just route. Output: 1–3 lines max, no recap.

**Freshness gate**: if the user's framing suggests new work ("I want to add a new feature", "let's start something new") and the mid-flow signal is from an old artifact (stale `STATE.md`, paused FIS), treat as Branch C instead. When in doubt, ask one question: "Continuing previous work, or starting something new?"

**Match rule**: read top-down; first matching row wins – rows are ordered most-specific to most-generic (e.g. an architecture report *plus* pasted visual review notes fires before architecture report alone).

| Detected state | Recommended next |
|---|---|
| `requirements-clarification.md` just produced, before `prd` / `spec` | offer the `andthen:visualize` skill as a review checkpoint, or route to the next workflow skill |
| `prd.md` exists, no `plan.json` | the `andthen:plan` skill (or offer the `andthen:visualize` skill as a review checkpoint first) |
| `plan.json` exists, FIS files missing | the `andthen:plan` skill to resume the bundle and fill missing FIS files (or offer the `andthen:visualize` skill first when the user wants to inspect the incomplete bundle) |
| Legacy `plan.md` exists, no `plan.json` | the `andthen:plan` skill – re-running migrates `plan.md` → `plan.json` and preserves existing FIS files |
| All FIS exist, implementation incomplete | the `andthen:exec-plan` skill (multi) or the `andthen:exec-spec` skill (single), with the `andthen:visualize` skill as an optional plan review checkpoint first. When stories carry `owner` claims, surface them and steer toward an unclaimed dependency-ready story (claim via the `andthen:ops` skill `update-plan-owner`; under `--from-issue`, claim on the issue's Owner cell instead) |
| Implementation done, no review on this branch | the `andthen:review` skill |
| Review done, findings unaddressed | the `andthen:remediate-findings` skill |
| Triage report (`andthen:triage --plan-only`) present, fix not yet applied | re-invoke the `andthen:triage` skill to apply the fix, or the `andthen:remediate-findings` skill if the report has actionable findings rather than a single fix |
| Architecture report present AND user signals visual review notes ("notes copied", pasted markdown payload starting with `# andthen:architecture visual review notes for …`) | re-invoke the `andthen:architecture` skill in the matching mode (read the report's H1/H2 to identify trade-off / strategic-design / etc.) with the notes pasted as conversational input |
| Architecture report present (review / decompose / fitness / trade-off / strategic-design / event-storming), no obvious follow-on | offer the `andthen:visualize` skill as a review checkpoint, then ask one question to scope the next step – formalize as ADR (a fresh `andthen:architecture` invocation in `--mode trade-off` for the decision; *skip if the report is itself a trade-off run – Step 6 already produced the ADR unless the user opted out*), feed into `andthen:clarify` (when discovery surfaced requirement gaps), or chain to `--mode strategic-design` / `--mode decompose` (when boundaries are still contested) |
| FIS present, not yet executed | the `andthen:exec-spec` skill (or offer the `andthen:visualize` skill as a scenario/task review checkpoint first) |
| Review report present (any lens), findings unaddressed | the `andthen:remediate-findings` skill (or offer the `andthen:visualize` skill first for severity-coded triage) |
| UI/UX wireframes or design-system output present, no implementation | the `andthen:exec-spec` skill (single screen / FIS) or the `andthen:exec-plan` skill (full plan) |
| UI/UX wireframes implemented, no design-review on this branch | the `andthen:ui-ux-design` skill in `--mode review` |
| User says "stuck" with mid-flow state | Ask one question: "What did you last do, and what's not behaving as expected?" |

Format: _"You're at X – next is the `andthen:<skill>` skill. Run it? (Y/n)"_


## Handoff Contract

- **Invoke** the recommended skill via the Skill tool unless the user declines or `--no-handoff` is set; pass `$ARGUMENTS` through as downstream context so the user does not repeat themselves.
- **Answer "what does X do?" from `references/skill-reference.md`**, then offer to invoke; for behavioral depth read the target skill's SKILL.md – never answer from generic memory.
