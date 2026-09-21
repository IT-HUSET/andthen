---
description: First-stop router – inspects project state and routes to the right AndThen skill. Trigger on 'where do I start', 'now what', "I'm stuck", 'is this a PRD or a spec'.
argument-hint: "[brief description of what you want to do]"
---

# Now What

`REQUEST` is `$ARGUMENTS` – what the user wants to do, possibly empty.

## INSTRUCTIONS

- **Detect first, ask second.** Only ask what state cannot reveal – the user's actual idea or framing.
- **Two questions max; never a menu.** One to hear the idea, one to disambiguate, then commit.
- **One handoff per invocation.** For a sequenced route, recommend the first hop and have the user invoke the `andthen:now-what` skill again; never auto-chain.
- **Do not re-implement downstream work.** One line per recommended skill.
- **Use the user's words, not workflow vocabulary.** A first-time user does not know "FIS" or "PRD" – introduce the term at handoff.


## WORKFLOW

### Phase 1 – State Detection

Compute setup, codebase, and workflow **independently** – none decides another, so a stub never hides an active plan. Only the codebase-volume signal may ask – do not also ask in Step 3.

- **Project instructions loaded?** – the host loads the root instruction file into your context; never read it from disk. If none reached you → `setup: not-started`.
- **`## Project Document Index` and `## Project-Specific Guidelines and Rules` in them?** – section headings in what was loaded. If missing → `setup: partial`.
- **Source code beyond config/README?** – `git ls-files` count + extension distribution; rough cut >50 tracked files with substantive code extensions. Substantial code and no map (next signal) → `codebase: brownfield-unmapped`. **If unclear**, ask: "Is this a fresh project or existing code?"
- **Map-codebase output present?** – at its **Project Document Index** location: a filled-in `Architecture` or `Key Dev Commands` document (an init stub is not a map) or `requirements-discovered.md` / `decisions-discovered.md`. If yes → `codebase: brownfield-mapped`.
- **Any in-flow artifact at indexed paths?** – read the **Project Document Index** and check for `intent.md`, `prd.md`, `plan.json`, plan-story FIS files (`s[0-9][0-9]-*.md`), standalone FIS docs by shape (`## Feature Overview and Goal` + `## Acceptance Scenarios`), review reports with unaddressed findings (`*-review-*.md`; a clean or remediated report is retained evidence, not active state), and the most recent architecture-report (`*-architecture-*.md`) and ui-ux-design output (wireframes / design-system). If any → `workflow: mid-flow`, position inferred from the artifact type.

**Output**: a state vector like `setup: done | codebase: greenfield | workflow: nothing-in-progress`.


### Phase 2 – Branch Selection

First matching row wins:

| State vector | Branch |
|---|---|
| `workflow: mid-flow` | **D – Mid-Flow Navigation** – active work first; a `setup: partial` gap is one advisory line, not a detour |
| `setup: not-started` or `setup: partial` | **A – Setup / Onboarding** |
| `codebase: brownfield-unmapped` | **B – Brownfield Mapping** |
| `workflow: nothing-in-progress` | **C – Starting a Feature** |


### Phase 3 – Onboarding Flow (Branches A / B / C)

#### Branch A – Setup not done

> AndThen has one workflow – **clarify → plan → exec-plan → review --fix → PR** (skip `clarify` when the PRD already exists as an issue or a document), where `exec-plan` runs one `exec-spec` per story – plus a quick track (**spec → exec-spec**) for a single feature and optional design tools (architecture, UI/UX, glossary). Setup comes first.

Offer the `andthen:init` skill, passing `REQUEST` through as project name when relevant. When `init` returns, tell the user to invoke the `andthen:now-what` skill again.

#### Branch B – Brownfield codebase, no map yet

> This codebase has substantial code AndThen has not analyzed. Mapping it first lets later skills reason about what exists rather than treat the repo as empty.

Offer the `andthen:describe` skill in `--mode codebase`. On accept hand off; on decline note the trade-off and fall through to Branch C.

#### Branch C – Starting a feature

**Step 1 – Hear the idea.** If `REQUEST` is empty, ask one open question (_"What do you want to build, change, or figure out?"_).

**Step 2 – Classify the request shape silently** and commit. Match the framing against the skills' frontmatter `description` fields: those are the routing canon, and a cue list here would drift from what the host matches on. Three things they do not settle:

**Scope and completeness.** Route on what the input settles: one capability whose acceptance a reader could list → the `andthen:spec` skill, the quick track straight to `exec-spec`; a complete initiative whose requirements a PRD source already carries – a `prd.md`, a requirements file, or a tracker item – → the `andthen:plan` skill, which decomposes it into stories; requirements still open (vague outcome, unnamed users, unsettled scope) → the `andthen:clarify` skill. Whole-product framing ("what should this product be", "positioning") goes there too – `clarify` infers product scope from it.

**Mode**, when the route depends on it: "should we split this", "decompose", "boundaries" → the `andthen:architecture` skill in `--mode decompose`. Otherwise pass the user's wording through and let the skill infer: "how do I organize" / "what's the right pattern for" → the `andthen:architecture` skill; screens, user flows, style guide, colors, typography, or design tokens → the `andthen:ui-ux-design` skill.

**Genuine ambiguities** – one phrasing, two skills:

- "triage" – failing build, test, or runtime bug → the `andthen:triage` skill; untriaged tracker items → the `andthen:backlog-triage` skill.
- "prototype this", "just try it" – a change meant to ship → the `andthen:implement-fix` skill; throwaway evidence for a decision → the `andthen:spike` skill.
- "X vs Y", "which is better/faster" – settleable by analysis → the `andthen:architecture` skill in `--mode trade-off`; only measurement settles it → the `andthen:spike` skill.
- "model the domain" – naming and term consistency → the `andthen:describe` skill in `--mode domain`; context boundaries and subdomain carving → the `andthen:architecture` skill in `--mode strategic-design`, or `--mode event-storming` on that explicit cue.

**Step 3 – Disambiguate only when needed.** If the framing is genuinely ambiguous between two shapes, ask **one** question – requirements or design (`clarify` vs `architecture`), whole initiative or one slice. Then commit to the likeliest route; the downstream skill redirects if wrong.

**Step 4 – Name the optional tools once**, in one line before handing off: the `andthen:architecture`, `andthen:describe`, and `andthen:ui-ux-design` skills, plus `andthen:now-what` to re-route.


### Phase 4 – Mid-Flow Navigation (Branch D, light touch)

Mid-flow, do not onboard: route in 1–3 lines, no recap.

**Freshness gate**: if the framing suggests new work ("let's start something new") and the mid-flow signal is a stale artifact (paused FIS, plan whose stories have not moved), treat as Branch C. When in doubt ask: "Continuing, or starting something new?"

**Match rule**: first match wins, top-down.

- **`intent.md` present, no sibling `prd.md`** (an intent doc, hand-written or from `clarify --brief`) – the `andthen:clarify` skill, which folds it into the PRD; the interview has not run yet.
- **`prd.md` exists, no `plan.json`** – the `andthen:plan` skill.
- **`plan.json` schemaVersion ≠ `"2"`** – the `andthen:plan` skill; skip story shape.
- **v2 `plan.json`, FIS files missing** – the `andthen:plan` skill to resume.
- **v2 `plan.json`, every schedulable story `blocked` with its FIS present** – the `andthen:spec` skill on the held FIS path, or the `andthen:plan` skill when several are held; `exec-plan` skips blocked stories, so nothing else settles the hold.
- **All FIS exist, implementation incomplete** – the `andthen:exec-plan` skill (multi) or `andthen:exec-spec` skill (single). Steer to an unclaimed dependency-ready story; the run session claims it in the story's `owner`.
- **Every plan story `done`/`skipped`, no `*-mixed-review-*.md` beside `plan.json`** – the `andthen:review` skill with `--mode code,gap,security,outcome --fix <plan.json>`; the bundle goes with the merge.
- **Implementation done, no review on this branch** – the `andthen:review` skill.
- **Architecture report present AND visual review notes signalled** ("notes copied", or a pasted payload starting `# andthen:architecture visual review notes for …`) – re-invoke the `andthen:architecture` skill in the report's mode (from its H1/H2), passing the notes through.
- **Architecture report present (any mode), no obvious follow-on** – one question to scope the next step: formalize as ADR (fresh `andthen:architecture` run in `--mode trade-off`; *skip when the report is itself a trade-off run, unless the user opted out of its ADR*), feed into `andthen:clarify` (requirement gaps), or chain to the `andthen:architecture` skill in `--mode strategic-design` / `--mode decompose` (contested boundaries).
- **A standalone FIS carrying no `Plan` / `Story-ID` provenance** (0.x, pre-migration) – the `andthen:spec` skill on its requirements source, the FIS as evidence; execution is plan-backed, so re-specification is the migration hop.
- **A FIS whose one-story `plan.json` is nonterminal** – the `andthen:exec-spec` skill; the story's completed task IDs resume.
- **Review report present (any lens), findings unaddressed** – the `andthen:implement-fix` skill.
- **UI/UX wireframes or design-system output, no implementation** – the `andthen:exec-spec` skill (single screen / FIS) or the `andthen:exec-plan` skill (full plan).
- **UI/UX wireframes implemented, no visual validation on this branch** – the `andthen:visual-validation` skill.
- **User says "stuck" with mid-flow state** – ask: "What did you last do, and what's not behaving as expected?"

Format: _"You're at X – next is the `andthen:<skill>` skill. Run it? (Y/n)"_


## Handoff Contract

- **Invoke** the recommended skill via the Skill tool, passing `REQUEST` through. When the user declines, or the request asks for a recommendation only, print the route and stop there.
- **Answer "what does X do?" from the target skill's frontmatter `description`** – its SKILL.md when the question needs flag or mode depth – then offer to invoke. Never from memory.
