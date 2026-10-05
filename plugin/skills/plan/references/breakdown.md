# Several-Story Breakdown

Turn a written source into `plan.json` per `plan-schema.md` and one reviewed, preflighted FIS per story. Never author a FIS yourself: Step 4 gives each story its own subagent. Integrating a Preflight answer or an `ASSUMPTION:` line is not authoring.

## Workflow

### 1. Read the source

`OUTPUT_DIR` is the directory the skill's Output names for the source. Route each asset the stories build on – beside the source, or at the `Decisions`, `Design System` and `Wireframes` entries – to the `assetRefs` of the stories that need it, so no story's spec re-reads every ADR. Module and context boundaries are in the `Models` Index entry's `architecture-model.json` and the `Context Map` document, where present.

Ask every gap the cut or a story's intent turns on, at requirements altitude – the outcome or user-visible end state, an actor, a threshold, an unhappy path – in one round per `preflight.md`'s sitting before any story is authored, since story subagents cannot ask. An answer is a requirement the stories are cut from: it goes into `prd.md` through the `andthen:clarify` skill's amendment for a `prd.md` source, else into `sharedDecisions` or the story's brief, since those are all a story subagent reads.

### 2. Cut the stories

Cut the fewest stories that cover the source, none overlapping, each a vertical slice demoable through every layer.

- **Single-session rule**: a story fits one fresh-context exec run with headroom, the measure in the skill's step 3. An oversized story splits into thinner vertical slices, never into layers.
- **Module fan-out**: where module boundaries are strong, a feature crossing modules splits along the seam into per-module stories, each vertical within its module, the interface pinned in `sharedDecisions`.
- Merge stories that touch substantially the same files, or that chain with no independent demo ("define endpoint", "wire handler", "surface in UI").
- `dependsOn` holds causal edges only: a predecessor whose artifact, contract or decision the story consumes.
- A story entry is a brief its authoring subagent reads once before the FIS supersedes it. Keep out what the FIS will state (scenarios, criteria, approach, file paths) and the source's rationale. Cite the source through `sourceRefs`; a story no source covers carries `provenance` saying why.

### 3. Write `plan.json`

Write `OUTPUT_DIR/plan.json` per `plan-schema.md`, with its two optional arrays:

- `sharedDecisions`: one entry per real cross-story contract, an interface, name or abstraction two stories must agree on. Zero or one is normal, and an invented entry binds every story downstream.
- `bindingConstraints`: a pointer to each at-risk "must" or "must not" span in the source, never its text.

Check each candidate against `plan.schema.json`, and never write one that fails.

### 4. Author the FIS

Launch, in source order, stories whose `dependsOn` stories already have their FIS, about five per batch so one re-read verifies it, and recompute after each batch. For each story, spawn a fresh implementer subagent that invokes the `andthen:plan` skill with `--auto --batch story {story_id} of {OUTPUT_DIR}/plan.json`, `--auto` because nobody watches a story subagent. It returns the `--batch` report: the FIS path, `PHANTOM_SCOPE` entries, any `OVERSIZE:` line, and its open items.

**Size signal**: an `OVERSIZE:` story is too broad. Re-cut it at Step 2, or trade the requirement its Architecture Decision names at Step 6, and author the resulting stories in its place.

A reported path is model output. Await every return, since a turn ended mid-batch writes no row, then check each against the story's canonical target (`plan-schema.md` § FIS identity) and the FIS's `**Plan**:` / `**Story-ID**:` header, and write the batch's rows in one pass, `status` staying `pending`: `fis` the basename, or literal `null` for invalid or missing output.

**Gate**: every story has a FIS, and every `OVERSIZE:` story is re-cut or a Step 6 trade item. A story left without one stops the run before Step 5 on a partial-bundle summary naming each story ID and its evidence.

### 5. Review the bundle

Spawn one fresh reviewer subagent as in the skill's step 7. Its prompt names `self-review.md` § FIS and § Bundle, `fis-authoring-guidelines.md` and `fis-contract.md` by absolute path, `plan.json`, every FIS path, and the source as Intent Context.

A chain leg no story owns opens a story through Steps 2–4. Anything else the review leaves open – residual Notes, `Scope trades:`, a cross-story contract change – is a Step 6 item naming its stories.

**Gate**: every `stories[].fis` is on the returned per-FIS roster. A FIS the roster omits went unreviewed, whatever the return says.

### 6. Preflight

Run `preflight.md` once over the whole bundle, even when nothing is open. Its items are Step 1's unasked gaps, every open item a `--batch` report returned, and Step 5's residue. A batch `ASSUMPTION:` is a question the story subagent could not ask, not an answer: outside an unattended run, ask it like any other item.

Integrate each answer yourself where it is owned:

- Requirement-level → `prd.md` through the `andthen:clarify` skill's amendment for a `prd.md` source, else `sharedDecisions`; and each FIS it changes.
- Cross-story contract → `sharedDecisions`.
- Story-local → its FIS.

A stop Preflight settles for a person's look lives in the follow-up line, never a plan status.

**Gate**: every item decided or assumed; every story has a FIS.

## Follow-up

Close on Preflight's Ending, when it ran, with the `plan.json` path before its one `Next (fresh session):` line, for the first case that applies. `<PLAN_DIR>` is `OUTPUT_DIR`, relative to the project root.

- **Preflight settled a stop for a person's look** – the `andthen:exec-plan` skill on that story's FIS path (its dependencies first); look at the result, then run it on `<PLAN_DIR>`.
- **Otherwise** – the `andthen:exec-plan` skill on `<PLAN_DIR>`, with `--worktree` to run independent stories in parallel, one worktree each, when the dependency graph lets two or more stories run at once.
