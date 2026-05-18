# `--to-issue` Mode (GitHub Output)

GitHub-output sibling of Step 4 in `andthen:plan`. Load when running with `--to-issue`, or when changing the plan-issue body shape.

**Nothing is written to disk** – no `plan.json`, no FIS. The in-memory plan object (built in Steps 2–3) renders to a GitHub issue body per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Steps 5–6 are skipped.


## 1. Build the plan-issue body

Render the in-memory plan using [`templates/plan-template-issue.md`](../templates/plan-template-issue.md). This is the GitHub-transport view; the canonical local artifact remains JSON. Body skeleton: `> **PRD**:` header (`github://issue/<input-issue-N>` for issue input, else local PRD path) → plan summary → optional `## Shared Decisions` → optional `## Binding Constraints` → `## Story Catalog` → one `### Story S0N: <name>` per story → `Refs #<input-issue-N>` footer (when an input issue was supplied).

`sharedDecisions` / `bindingConstraints` come straight from the in-memory plan – same extraction feeds both the local path (Step 4) and here. Omit either section when its array is empty.

Story Catalog columns and brief fields render `stories[]` per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) Plan Issue Catalog. `Dependencies` cells use `-` or comma-separated Story IDs. `FIS` cells stay `-` (JIT in `exec-plan --from-issue`).


## 2. Create the plan issue (single-issue mode, default)

When `--create-story-issues` is **not** set, publish per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `[Plan] <feature-name>`. Labels: `plan`, `andthen-artifact`. Body temp file: `.agent_temp/plan-issue-<feature-slug>.md`.

Success → **Stop** (Steps 5–6 do not run; no local files).


## 3. Create plan + story issues (granular mode, `--create-story-issues`)

Use the **granular shape** from [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Each create follows **Pattern A**:

1. **Build the plan-issue body** (granular shape): `> **PRD**:` header → plan summary → optional `## Shared Decisions` → optional `## Binding Constraints` (internal H2s downshifted to H3 per the Shape Detection note) → `## Story Catalog` → `## Story Issues` (placeholder bullets – filled in step 4) → `Refs #<input-issue-N>` footer.
2. **Create the plan issue first** (Pattern A – title `[Plan] <feature-name>`, labels `plan` + `andthen-artifact` + **`andthen-finalizing`**). Capture `<plan-N>`. The `andthen-finalizing` label is the consumer race-window gate – `exec-plan --from-issue` refuses to parse issues carrying it.
3. **For each story (catalog order)**: build the story-issue body per granular Story Issue Body Skeleton. Create with title `S0N: <story name>`, labels `story` + `andthen-artifact`. Capture each issue number.
4. **Rewrite the plan issue's `## Story Issues` section** with real `#<S-N>` references via `gh issue edit <plan-N> --body-file <updated-body-path>` – one bullet per story in catalog order: `- #<story-issue-N> – <story name> – <one-line scope>`. Optional inter-story `Depends on #<sibling-N>` navigation: stories whose dependencies point at later-catalog stories use placeholder text initially, then a second `gh issue edit <story-N>` rewrites navigation once all sibling numbers exist. (`gh issue edit` is the granular two-pass rewrite vehicle.)
5. **Remove `andthen-finalizing`** from the plan issue: `gh issue edit <plan-N> --remove-label andthen-finalizing`. Finalization signal. If this call fails, surface and leave the label in place (consumers refuse to parse – safe default).
6. Print the plan issue URL and a one-line `<N> story issues created` summary with URLs.
7. **Stop** – Steps 5–6 do not run.

On `gh` failure mid-creation, Pattern A's "surface and stop" applies. Already-created issues stay – surface URLs for manual cleanup. The `andthen-finalizing` label remaining is the consumer block preventing partial state from being read as final.


## Gate

Plan issue (and story issues, if granular) created; nothing written to local disk; printed URLs match the resolved shape.
