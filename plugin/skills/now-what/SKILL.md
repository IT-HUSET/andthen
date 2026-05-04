---
description: Use when getting started with AndThen on a project, picking a starting skill, or unsure what to do next. Inspects project state (init'd? greenfield? brownfield? mid-flow?) and routes to the right skill — `init`, `map-codebase`, `clarify`, `prd`, `architecture`, `ui-ux-design`, etc. Trigger on 'where do I start', "I'm new to AndThen", "what's next", 'next step', "I'm stuck", 'now what', 'help me get started', 'is this a PRD or a spec', 'guide me'.
argument-hint: "[brief description of what you want to do]"
---

# Now What

The first stop for users new to AndThen or unsure which skill to pick. Reads project state, asks at most one or two short questions, and routes to the right skill — heavy hand-holding for first-time setup, lighter touch mid-flow.


## VARIABLES

ARGUMENTS: $ARGUMENTS _(optional — what the user wants to do, e.g. "build a todo app", "should I use Postgres or SQLite", "I'm stuck", or empty)_

### Optional Flags
- `--no-handoff` → Emit recommendation only; do not invoke the downstream skill. For users who want to read before committing.


## INSTRUCTIONS

- **Detect first, ask second.** State already tells you most of what you need. Only ask the user what state cannot reveal (their actual idea or framing).
- **Two questions max** before committing to a route — one to hear the idea, one to disambiguate if genuinely ambiguous. Never present a numbered menu of skills.
- **One handoff per invocation.** If a route involves a sequence (e.g. `architecture --mode advise` → `clarify`), recommend the first hop and ask the user to re-invoke `now-what` after, rather than auto-chaining.
- **Do not re-implement downstream work.** Mention each recommended skill in one line; let its description and prompt do the rest.
- **Use the user's words, not workflow vocabulary.** A first-time user does not yet know "FIS" or "PRD" — match them where they are, then introduce the term when handing off.
- **Automation mode.** The skill is interactive by design — its core value is the question budget. Under `--auto` / `--headless`, skip the open-question step in Phase 3 and the disambiguation question in Phase 4's freshness gate; if `$ARGUMENTS` is empty or state-detection plus a single silent classification pass cannot commit to a route, exit with `BLOCKED: now-what cannot route headlessly without an idea or unambiguous mid-flow state`. Never present a menu in any mode.


## GOTCHAS
- Becoming a Choose-Your-Own-Adventure with branching menus instead of a router that commits.
- Onboarding mid-flow users who already have a `prd.md` — detect and skip the mental-model recap.
- Repeating the optional-tools surface on every Branch C route in this conversation. Surface once per session — the model has no cross-session memory, so do not pretend to remember prior runs.
- Forking context (`context: fork` in frontmatter) — this skill must hand off in-place, so it intentionally does not fork.


## WORKFLOW

### Phase 1 — State Detection

Read these signals **in order; stop at the first state-determining match.** Most paths are deterministic (no question); one row has a fallback question for genuinely ambiguous codebase volume — when used, it counts as the one disambiguation question allowed by the two-question budget, so do not also ask in Step 3. Reuse `init`'s vocabulary (`New project` / `Partial setup` / `Brownfield`) where it overlaps so terms stay consistent across skills.

| Signal | How to read | Outcome |
|---|---|---|
| `CLAUDE.md` (or `AGENTS.md`) at project root? | File exists | If no → `setup: not-started` |
| `## Project Document Index` section in CLAUDE.md? | Heading match | If no → `setup: partial` |
| Source code beyond config/README? | `git ls-files` count + extension distribution. Rough cut: >50 tracked files with substantive code extensions. **If genuinely unclear** (small repo, mixed signals), ask one question: "Is this a fresh project or are we working with existing code?" — never present a menu. | If yes & no map → `codebase: brownfield-unmapped` |
| Map-codebase output present? | Files matching `project-state-templates.md` outputs (Architecture, Stack, etc.) per **Project Document Index** | If yes → `codebase: brownfield-mapped` |
| Any in-flow artifact at indexed paths? | Read the **Project Document Index** and check for `requirements-clarification.md`, `prd.md`, `plan.md`, `*.fis.md`, `STATE.md`, the most recent architecture-report (`*-architecture-*.md`<sup>†</sup>), the most recent triage-report (`*-triage-*.md`), and the most recent ui-ux-design output (wireframes / design-system / design-review). | If any → `workflow: mid-flow` (and infer where in flow from the artifact type) |

<sup>†</sup> The `andthen:architecture` skill emits the single suffix `architecture` for all 7 modes; differentiate trade-off / strategic-design / event-storming etc. by reading the report's H1/H2, not the filename.

**Output**: a state vector like `setup: done | codebase: greenfield | workflow: nothing-in-progress`. This drives Phase 2.


### Phase 2 — Branch Selection

| State vector | Branch |
|---|---|
| `setup: not-started` or `setup: partial` | **A — Setup / Onboarding** |
| `setup: done | codebase: brownfield-unmapped` | **B — Brownfield Mapping** |
| `setup: done | workflow: nothing-in-progress` | **C — Starting a Feature** (the heart of the skill) |
| `setup: done | workflow: mid-flow` | **D — Mid-Flow Navigation** |


### Phase 3 — Onboarding Flow (Branches A / B / C)

When the user is new to AndThen on this project, they need a mental model **before** a routing decision — but in layers, not as a dump.

#### Branch A — Setup not done

Open with the mental model in three lines, no more:

> AndThen guides features through a disciplined chain: **clarify → (spec → exec-spec) or (prd → plan → exec-plan) → review**. There are also optional design tools (architecture, UI/UX, glossary, diagrams). First we need to set up the workflow structure in this project.

Then recommend the `andthen:init` skill (one line on what it does — creates CLAUDE.md, Document Index, folder layout) and offer to invoke it now. If the user accepts, hand off via the Skill tool with `$ARGUMENTS` passed through as project name when relevant. After `init` returns, the invocation ends — tell the user to re-invoke `/andthen:now-what` (with their idea, or no argument) to continue. The "one handoff per invocation" rule keeps the user in control.

Note: `init` itself handles New / Partial / Brownfield classification at fine granularity, so do not duplicate that logic here.

#### Branch B — Brownfield codebase, no map yet

> This codebase has substantial existing code that AndThen has not analyzed yet. Mapping it first means later skills (clarify, spec, architecture) can reason about what already exists rather than treating the repo as empty.

Recommend the `andthen:map-codebase` skill and offer to invoke it. If the user accepts, hand off via the Skill tool — the invocation ends, tell the user to re-invoke `/andthen:now-what` after to continue. If they decline, note the trade-off briefly ("downstream skills will work but with less context") and proceed to Branch C in the same invocation (no handoff yet, so no rule violation).

#### Branch C — Starting a feature (the most important onboarding path)

This is where users get lost: AndThen is set up, they have an idea, but they do not yet know whether they need `clarify`, `prd`, `spec`, `quick-implement`, `architecture`, `ui-ux-design`, or some combination.

**Step 1 — Hear the idea (1 question max).** If `$ARGUMENTS` is empty, ask one open question: _"What do you want to build, change, or figure out?"_ Skip the question if `$ARGUMENTS` already has content.

**Step 2 — Classify the request shape silently.** Match the user's framing to the most likely shape and commit. Do not ask the user to pick from this table.

| Request shape | Cue phrases | Route |
|---|---|---|
| Build a single feature | "add X", "implement Y", "I want users to be able to Z" | → the `andthen:clarify` skill |
| Build a bigger initiative | "build a whole X", multiple capabilities mentioned, "platform", "system" | → the `andthen:clarify` skill (entry point for the multi-feature `prd → plan → exec-plan` chain). If the framing carries architectural ambiguity ("multi-tenant", "real-time", "how should I structure a..."), use Step 3 to disambiguate between `clarify` and the `andthen:architecture` skill in `--mode advise`. |
| Quick fix / small change | "fix typo", "rename X", "bump version" | → the `andthen:quick-implement` skill |
| How should I structure X? | "should I split", "how do I organize", "what's the right pattern for" | → the `andthen:architecture` skill in `--mode advise` |
| Compare two approaches | "X vs Y", "should we use A or B" | → the `andthen:architecture` skill in `--mode trade-off` |
| Module split / merge decision | "should we split this", "decompose", "boundaries" | → the `andthen:architecture` skill in `--mode decompose` |
| Domain discovery / subdomain mapping / context boundaries | "bounded contexts", "subdomains", "domain map", "what are our domains", "model the domain", "event storming" | → the `andthen:architecture` skill in `--mode strategic-design` _(or `--mode event-storming` when "event storming" is the explicit cue)_ |
| UI screens or flow | "screens", "wireframes", "user flow" | → the `andthen:ui-ux-design` skill in `--mode wireframes` |
| Design system / tokens | "style guide", "colors and typography", "design tokens" | → the `andthen:ui-ux-design` skill in `--mode design-system` |
| Domain language / glossary | "glossary", "terminology", "what should we call" | → the `andthen:ubiquitous-language` skill |
| Something is broken | "bug", "error", "build failing", "test failure" | → the `andthen:triage` skill |

**Step 3 — Disambiguate only when needed.** If the framing is genuinely ambiguous between two shapes, ask **one** question — never two. Examples:

- "Sounds like a single feature. Want me to dig into requirements first (`clarify`), or is the design question more pressing (`architecture --mode advise`)?"
- "This sounds bigger than one feature — multiple capabilities. Treat it as a multi-feature initiative (PRD + plan), or focus on one slice first?"

If still ambiguous after one question, commit to the most likely route — the downstream skill will redirect if wrong.

**Step 4 — Surface the optional tools, once.** After committing to a route, mention in two lines what *else* exists, so the user knows the toolkit:

> "You're going into `clarify` next. Heads up that AndThen also has the `andthen:architecture`, `andthen:ui-ux-design`, `andthen:ubiquitous-language`, and `andthen:excalidraw-diagram` skills — useful as you go deeper. Type `/andthen:now-what` any time you're unsure what's next."

This is the moment to surface optional tools. After this, never repeat unless asked.

**Step 5 — Hand off** via the Skill tool with the user's idea passed through.


### Phase 4 — Mid-Flow Navigation (Branch D, light touch)

When state shows the user is mid-flow, do not onboard. Just route. Output: 1–3 lines max, no recap.

**Freshness gate**: if the user's framing suggests new work ("I want to add a new feature", "let's start something new") and the mid-flow signal is from an old artifact (stale `STATE.md`, paused FIS), treat as Branch C instead. When in doubt, ask one question: "Continuing previous work, or starting something new?"

**Match rule**: read top-down; first matching row wins. Order rows from most-specific to most-generic so a more-specific match (e.g. an architecture report *plus* pasted visualize notes) fires before a generic one (architecture report alone).

| Detected state | Recommended next |
|---|---|
| `requirements-clarification.md` just produced, before `prd` / `spec` | offer the `andthen:visualize` skill (review checkpoint) → then the next workflow skill |
| `prd.md` exists, no `plan.md` | the `andthen:plan` skill (or offer the `andthen:visualize` skill as a review checkpoint first) |
| `plan.md` exists, FIS files missing | the `andthen:spec` skill per story (re-running `andthen:plan` would regenerate `plan.md` and clobber it) |
| All FIS exist, implementation incomplete | the `andthen:exec-plan` skill (multi) or the `andthen:exec-spec` skill (single) |
| Implementation done, no review on this branch | the `andthen:review` skill |
| Review done, findings unaddressed | the `andthen:remediate-findings` skill |
| Triage report (`andthen:triage --plan-only`) present, fix not yet applied | re-invoke the `andthen:triage` skill to apply the fix, or the `andthen:remediate-findings` skill if the report has actionable findings rather than a single fix |
| Architecture report present AND user signals visualize notes ("notes copied", pasted markdown payload starting with `# andthen:visualize notes for …`) | re-invoke the `andthen:architecture` skill in the matching mode (read the report's H1/H2 to identify trade-off / strategic-design / etc.) with the notes pasted as conversational input |
| Architecture report present (review / decompose / advise / fitness / trade-off / strategic-design / event-storming), no obvious follow-on | ask one question to scope the next step — formalize as ADR (a fresh `andthen:architecture` invocation in `--mode trade-off` for the decision), feed into `andthen:clarify` (when discovery surfaced requirement gaps), or chain to `--mode strategic-design` / `--mode decompose` (when boundaries are still contested) |
| UI/UX wireframes or design-system output present, no implementation | the `andthen:exec-spec` skill (single screen / FIS) or the `andthen:exec-plan` skill (full plan) |
| UI/UX wireframes implemented, no design-review on this branch | the `andthen:ui-ux-design` skill in `--mode review` |
| User says "stuck" with mid-flow state | Ask one question: "What did you last do, and what's not behaving as expected?" |

Format: _"You're at X — next is the `andthen:<skill>` skill. Run it? (Y/n)"_


## Handoff Contract

- **Always invoke** the recommended skill via the Skill tool unless the user declines or `--no-handoff` is set.
- **Pass user input through** — `$ARGUMENTS` becomes context for the downstream skill so the user does not repeat themselves.
- **One handoff per invocation.** If the route involves a sequence (e.g. `advise → clarify`), recommend the first hop and ask the user to re-invoke `now-what` after.
- **Answer "what does X do?" from the Skill Reference section below** (purpose, produces, workflow position), then offer to invoke. For behavioral depth (flag mechanics, mode internals), read the target skill's SKILL.md — never answer from generic memory.


## Skill Reference

Brief reference for skills `andthen:now-what` recommends. Each entry covers purpose, output, and workflow position. For behavioral depth (flag mechanics, mode internals, decision logic), read the target skill's `SKILL.md` directly — depth lives there, not here. Maintenance contract: see `CLAUDE.md` "Skill Reference maintenance" — entries are updated whenever a skill's purpose, output, or workflow position changes.

### `andthen:init`
Sets up the AndThen workflow structure: `CLAUDE.md`, Project Document Index, folder layout, optional starter docs (Learnings, Stack, Key Dev Commands, guidelines). Detects new / partial-setup / brownfield projects and adapts non-destructively. Run once per project; re-running fills gaps without overwriting.
**Typical next step:** re-invoke `andthen:now-what` to route the first feature.

### `andthen:now-what`
This skill — first-stop router for users new to AndThen or unsure what to do next. Inspects project state and routes to the right skill, with heavy onboarding on first-time setup and terse routing mid-flow.
**Use when:** unsure which skill to invoke next, or starting fresh on a project.

### `andthen:map-codebase`
Analyzes an existing codebase to produce structured documentation (Architecture, Stack, conventions) plus a discovered-requirements doc. Read-only — no code changes.
**Use when:** starting work on a brownfield codebase before committing to feature work, so downstream skills can reason about what already exists. **Typical next step:** re-invoke `andthen:now-what` to route the user's actual feature intent.

### `andthen:clarify`
Refines a fuzzy idea into clarified requirements through systematic discovery — gaps, edge cases, scope boundaries. Interactive.
**Use when:** the user has an idea but the requirements aren't yet pinned down. **Typical next step:** `andthen:spec` for one feature, `andthen:prd` for a multi-feature initiative.

### `andthen:prd`
Creates a Product Requirements Document (`prd.md`) from clarified requirements, a draft PRD, an inline description, a file, a URL, or a GitHub issue.
**Use when:** scoping a multi-feature initiative. **Typical next step:** `andthen:plan` to break the PRD into stories with FIS specs.

### `andthen:plan`
Consumes an existing `prd.md` and produces the full plan bundle: `plan.md` (story breakdown), one FIS file per story, and a shared `.technical-research.md`. With `--skip-specs`, produces `plan.md` alone.
**Use when:** turning a PRD into an executable, story-by-story plan. **Typical next step:** `andthen:exec-plan` to implement the bundle.

### `andthen:spec`
Produces a single Feature Implementation Specification (FIS) for one execution-sized feature. If the feature exceeds size thresholds, escalates — standalone inputs route to the `andthen:prd → andthen:plan → andthen:exec-plan` chain; plan-story inputs go upstream for plan decomposition.
**Use when:** a single feature is clear enough to specify but isn't part of a multi-feature plan. **Typical next step:** `andthen:exec-spec` to implement the FIS.

### `andthen:exec-spec`
Implements code from a single FIS — code, tests, and verification. Honors the FIS contract (Required Context, Scenarios, Success Criteria) and surfaces named blocks (`CONFUSION:`, `NOTICED BUT NOT TOUCHING:`, `MISSING REQUIREMENT:`) when stuck.
**Typical next step:** `andthen:review` (or `andthen:quick-review` mid-flow) before committing.

### `andthen:exec-plan`
Implements a fully-specced plan bundle story-by-story. Runs a fixed pipeline per story (`exec-spec` + `quick-review`) plus a final gap review on the whole plan.
**Typical next step:** `andthen:review` for the whole plan; `andthen:remediate-findings` if findings need addressing.

### `andthen:quick-implement`
Fast implementation path for small features, bug fixes, or GitHub issues — bypasses the FIS workflow. Includes verification (build, tests, lint).
**Use when:** the change is small enough that authoring a FIS would be overhead. For larger features, prefer the `andthen:clarify → andthen:spec → andthen:exec-spec` chain.

### `andthen:architecture`
Architecture design and analysis. Seven modes — `review`, `decompose`, `advise`, `fitness`, `trade-off`, `strategic-design`, `event-storming`. Outputs vary by mode (review reports, ADRs, fitness functions, trade-off analyses, strategic-design reports, event-storming boards). No code changes.
**Use when:** structural questions, comparing options, mapping a domain end-to-end, or before committing to a decomposition. **Typical next step:** back to `andthen:now-what` once the design question is resolved.

### `andthen:ui-ux-design`
UI/UX work across the lifecycle. Four modes — `research`, `design-system` (tokens, style guide), `wireframes` (screens, user flows), `review` (validate implementation).
**Use when:** any design work upstream of UI implementation. **Typical next step:** `andthen:exec-spec` or `andthen:exec-plan` to build the designed work.

### `andthen:visual-validation`
Validates UI screenshots and implementations against visual, responsive, and design expectations. Produces Summary / Detailed Findings / Recommended Fixes / Next Steps with prioritized P1/P2/P3 issues.
**Use when:** checking implemented UI, screenshots, wireframes, or visual regressions against a design reference. **Typical next step:** fix P1/P2 findings, then re-run validation or `andthen:ui-ux-design --mode review`.

### `andthen:ubiquitous-language`
Extracts and maintains the project's `Ubiquitous Language` document (glossary) using the codebase, documentation, and conversation.
**Use when:** domain terms are inconsistent or undefined — useful before committing to API names or schema vocabulary.

### `andthen:excalidraw-diagram`
Creates high-quality Excalidraw diagrams — workflows, architectures, concepts. Output is JSON renderable in any Excalidraw editor.
**Use when:** visualizing structure or flow as part of design or documentation.

### `andthen:visualize`
Renders a PRD, `requirements-clarification.md`, architecture trade-off report, or architecture strategic-design report as a self-contained HTML view (inline CSS+JS+SVG, no external deps), opens it in the user's browser, and exports section-anchored notes via clipboard as a markdown payload that downstream skills (`prd`, `clarify`, `architecture`) consume as conversational input. Open-loop: emits HTML, opens browser, exits.
**Use when:** at workflow inflection points (post-`clarify`, post-`architecture --mode trade-off`, post-`architecture --mode strategic-design`, on an existing PRD) to spot scope and edge-case issues a markdown view obscures. **Typical next step:** paste the copied notes into the next workflow skill's chat as conversational input.

### `andthen:review`
The default review skill. Lenses: `code` (correctness, patterns), `doc` (clarity, completeness), `gap` (spec-vs-implementation), `security` (OWASP, exposure tier), `mixed` (chain). Multi-perspective `--council` mode runs multiple reviewer roles in debate.
**Use when:** before committing or merging significant changes. **Typical next step:** `andthen:remediate-findings` if findings need addressing.

### `andthen:quick-review`
Lightweight mid-conversation review of recent changes, dispatched to a fresh-context sub-agent (or `--inline` when the calling conversation is itself fresh). Read-only by default; `--fix` applies accepted findings.
**Use when:** sanity-check before moving on, mid-flow.

### `andthen:remediate-findings`
Implements actionable findings from a review report — code, specs, plans, PRDs, or docs — with minimal, guideline-aligned fixes. Re-validates the result and updates plan / FIS status.
**Use when:** a review left findings to address.

### `andthen:testing`
Test strategy, coverage assessment, test authoring, and TDD discipline (Prove-It bugfix flow, FIS scenario → test mapping). Covers unit and integration; defer end-to-end suites to `andthen:e2e-test`.
**Use when:** writing new tests, improving coverage, or applying red-green-refactor.

### `andthen:e2e-test`
End-to-end browser testing for web apps. Discovers user journeys, runs interactive tests, validates responsive behavior.
**Use when:** validating a running web app against full user flows.

### `andthen:triage`
Investigates and fixes issues — build failures, configuration errors, runtime bugs, regressions, test failures. With `--plan-only` produces a fix plan without applying; with `--to-issue` files the diagnosis as a GitHub issue.
**Use when:** something is broken and the root cause isn't obvious. **Typical next step:** verify the fix; commit when stable.

### `andthen:refactor`
Improves, simplifies, and refactors code for clarity, consistency, and maintainability without changing behavior.
**Use when:** code is becoming hard to maintain, or after a feature lands and a cleanup pass is warranted.

### `andthen:ops`
Deterministic operations on workflow state — `STATE.md` updates, plan status, FIS checkboxes, standardized commits.
**Use when:** transitioning between workflow phases or marking progress. Often invoked automatically by other skills.


## Anti-Patterns

1. **Choose-Your-Own-Adventure menus.** Never present a numbered list of skills and ask the user to pick. State + at most one disambiguating question, then commit.
2. **Re-summarizing internal mechanics.** Decision logic and how flags / modes work belong in the target skill's prompt. Naming flags / modes in a Skill Reference entry is fine when they gate routing (different output, modify-vs-report); enumerating every flag is not.
3. **Asking >2 questions before routing.** If state + input still does not disambiguate after one question, commit to the most likely route and let the downstream skill redirect if wrong.
4. **Onboarding mid-flow users.** A user with a `prd.md` does not need the mental-model recap. Branch D is terse by design.
5. **Repeating the optional-tools surface every Branch C route.** Surface once per session, in Branch A or first-time Branch C — there is no cross-session memory, so do not pretend to remember.
6. **Auto-chaining downstream skills.** One handoff per invocation keeps the user in control and the contract clean.
