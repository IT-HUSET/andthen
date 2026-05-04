# `--to-issue` Mode (GitHub Output)

GitHub-output sibling of Step 4 in `andthen:plan`. Load this reference when running the `andthen:plan` skill with `--to-issue` set, or when implementing changes to the plan-issue body shape.

**Nothing is written to disk** — no `plan.md`, no `.technical-research.md`, no FIS files. The plan content goes into a GitHub issue body per the canonical shape in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Steps 5 (Technical Research write), 6 (FIS generation), and 7 (cross-cutting review) are skipped — Step 5's research synthesis still runs but the output is held in memory and inlined into the plan-issue body instead of written to `.technical-research.md`.


## 1. Synthesize technical research in memory

Run the same Step 5 sub-agent fan-out for technical research, but keep the output in memory (do not write `.technical-research.md`). The result is inlined into the plan-issue body's `## Technical Research` section in step 2 below.


## 2. Build the plan-issue body

Synthesize per the **single-issue shape** in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md): plan summary → `## Technical Research` → `## Story Catalog` table → one `### Story S0N: <name>` per story → `Refs #<input-issue-N>` footer line when an input issue was supplied.

Story Catalog columns and per-story metadata fields are identical to the local `plan.md` template — the same `data-contract.md` Story Catalog Columns and Required Story Metadata Labels apply. The `**FIS**` field stays unset (`-`); FIS files are generated just-in-time by `andthen:exec-plan --from-issue`.


## 3. Create the plan issue (single-issue mode, default)

When `--create-story-issues` is **not** set, publish per **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Title: `[Plan] <feature-name>`. Labels: `plan`, `andthen-artifact`. Body temp file: `.agent_temp/plan-issue-<feature-slug>.md`.

After success: **Stop** — do not run Steps 5, 6, 7. The local working tree contains no new plan/research/FIS files.


## 4. Create plan + story issues (granular mode, `--create-story-issues`)

When `--create-story-issues` is set, use the **granular shape** from [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md). Each issue creation below follows **Pattern A** in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md); the orchestration around them is granular-specific:

1. **Build the plan-issue body** with the granular shape: plan summary → `## Technical Research` (with internal H2s downshifted to H3 — see the Shape Detection note in `plan-issue-shape.md`) → `## Story Catalog` → `## Story Issues` (placeholder bullets — real issue numbers fill in step 5 below) → `Refs #<input-issue-N>` footer.
2. **Create the plan issue first** (Pattern A — title `[Plan] <feature-name>`, labels `plan` + `andthen-artifact` + **`andthen-finalizing`**) with placeholder `## Story Issues` bullets. Capture its number `<plan-N>`. The `andthen-finalizing` label is the producer/consumer race-window gate — consumers (`andthen:exec-plan --from-issue`) refuse to parse a plan issue carrying this label.
3. **For each story (in catalog order)**: build the story-issue body per the granular **Story Issue Body Skeleton** in `plan-issue-shape.md`. Create per Pattern A with title `S0N: <story name>` and labels `story` + `andthen-artifact`. Capture each new issue number.
4. **Rewrite the plan issue's `## Story Issues` section** with the real `#<S-N>` references via `gh issue edit <plan-N> --body-file <updated-body-path>` — one bullet per story in catalog order using the canonical 3-field shape from [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md): `- #<story-issue-N> — <story name> — <one-line scope>`. Inter-story `Depends on #<sibling-N>` resolution: a story whose dependencies point at later-catalog stories temporarily uses placeholder text, then a second `gh issue edit <story-N>` rewrites the dependencies once all sibling numbers exist. (`gh issue edit` is the granular two-pass rewrite vehicle — Pattern A covers create-new only.)
5. **Remove the `andthen-finalizing` label** from the plan issue: `gh issue edit <plan-N> --remove-label andthen-finalizing`. This is the finalization signal — only after this call may consumers parse the plan issue. If this call fails, surface the failure but leave the label in place (consumers will refuse to parse, which is the safe default — surface the error so the user can manually remove the label after verifying).
6. Print the plan issue URL and a one-line `<N> story issues created` summary with their URLs.
7. **Stop** — Steps 5, 6, 7 of the parent skill do not run; the local working tree contains no new files.

On `gh` failure mid-creation, Pattern A's "surface and stop" applies. Already-created issues are left in place — surface their URLs so the user can act manually rather than attempting a destructive rollback. The `andthen-finalizing` label remaining on the plan issue is the consumer-side block that prevents partial state from being treated as final.


## Gate

Plan issue (and story issues, if granular) created; nothing written to local disk; printed URLs match the resolved shape.
