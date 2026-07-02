# `--to-issue` Mode (GitHub Output)

GitHub-output sibling of Step 4 in the `andthen:plan` skill. Load when running with `--to-issue`, or when changing the plan-issue body shape.

**No durable local artifacts are written** – no `plan.json`, no FIS. The in-memory plan object (built in Steps 2–3) renders to a GitHub issue body per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). A transient `.agent_temp/` body file may be written for `gh --body-file`. Steps 5–6 are skipped.


## 1. Build the plan-issue body

Render the in-memory plan using [`templates/plan-template-issue.md`](../templates/plan-template-issue.md) per the **Single-Issue Shape** skeleton in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). This is the GitHub-transport view; the canonical local artifact remains JSON.

`sharedDecisions` / `bindingConstraints` come straight from the in-memory plan – same extraction feeds both the local path (Step 4) and here. Omit either section when its array is empty.

Story Catalog columns and brief fields render `stories[]` per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) Plan Issue Catalog. `Dependencies` cells use `-` or comma-separated Story IDs. `FIS` cells stay `-` (JIT in the `andthen:exec-plan` skill's `--from-issue` mode). **Republish preservation**: when `OUTPUT_DIR` already holds a `plan.json`, carry its `stories[].owner` and `status` into the rendered catalog for matching story `id`s that pass the **Preservation predicate** (never graft stale status/claims onto redefined stories). When the prior plan issue is known (caller-named or linked from the run's input), also read its catalog: its non-empty `Owner` cells win over a local `null` or a conflicting local owner (claims live on the issue); name any displaced local value in the publish output. When no prior issue is identifiable, state in the publish output that the superseded issue's claims were not carried.


## 2. Create the plan issue (single-issue mode, default)

When `--create-story-issues` is **not** set, publish per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `[Plan] <feature-name>`. Labels: `plan`, `andthen-artifact`. Body temp file: `.agent_temp/plan-issue-<feature-slug>.md`.

Success → **Stop**.


## 3. Create plan + story issues (granular mode, `--create-story-issues`)

Use the **granular shape** from [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Each create follows **Pattern A**:

1. **Build the plan-issue body** per the granular **Parent Plan Issue Body Skeleton** in `plan-issue-shape.md` (inlined-PRD H2 collisions downshift to H3 per its Shape Detection note; `## Story Issues` starts as placeholder bullets – rewritten in step 4).
2. **Create the plan issue first** (Pattern A – title `[Plan] <feature-name>`, labels `plan` + `andthen-artifact` + **`andthen-finalizing`**). Capture `<plan-N>`. The `andthen-finalizing` label is the consumer race-window gate – the `andthen:exec-plan` skill's `--from-issue` mode refuses to parse issues carrying it.
3. **For each story (catalog order)**: build the story-issue body per granular Story Issue Body Skeleton. Create with title `S0N: <story name>`, labels `story` + `andthen-artifact`. Capture each issue number.
4. **Rewrite the plan issue's `## Story Issues` section** with resolved story issue references via `gh issue edit <plan-N> --body-file <updated-body-path>` – one bullet per story in catalog order: `- #<story-issue-N> – <story name> – <one-line scope>`, where `<story-issue-N>` is the numeric GitHub issue number. Optional inter-story `Depends on` navigation follows the **Two-pass `Depends on` resolution** note in `plan-issue-shape.md`.
5. **Remove `andthen-finalizing`** from the plan issue: `gh issue edit <plan-N> --remove-label andthen-finalizing`. If this call fails, surface and leave the label in place (consumers refuse to parse – safe default).
6. Print the plan issue URL and a one-line `<N> story issues created` summary with URLs.
7. **Stop**.

On `gh` failure mid-creation, Pattern A's "surface and stop" applies. Already-created issues stay – surface URLs for manual cleanup. The `andthen-finalizing` label remaining is the consumer block preventing partial state from being read as final.


## Gate

Plan issue (and story issues, if granular) created; no durable local artifacts written; printed URLs match the resolved shape.
