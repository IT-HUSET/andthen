# `--from-issue` Mode (GitHub Input)

GitHub-input mechanics for `andthen:exec-plan --from-issue <N>`. Load this reference when running the `andthen:exec-plan` skill with `--from-issue` set, or when changing how plan-issue bodies are parsed, how FIS files are generated just-in-time, or how closure comments are posted back to GitHub.

The flag swaps the plan source from a local `PLAN_DIR/plan.md` to a GitHub issue body. FIS files are generated **just-in-time per story** by invoking the `andthen:spec` skill (which itself does not parse a `--issue` flag — the orchestrator owns the issue fetch). After the per-story pipeline completes, shape-appropriate closure comments are posted on the relevant issues.

Companion references:
- [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md) — the canonical body shape (single-issue and granular) that this mode parses and that closure comments target.
- [`team-mode-orchestration.md`](team-mode-orchestration.md) — `--team` and `--worktree` mechanics. **`--from-issue` is mutually exclusive with `--team`** (parallel JIT FIS generation is not supported under this flag).


## Step 1: Flag-combination guard

Apply both guards before any other Step 1 work. The `--worktree` guard is added here (in addition to the existing `--worktree requires --team` pre-validate in the parent SKILL.md) so the user gets a single, accurate error rather than the ping-pong between `--worktree requires --team` and `--from-issue is mutually exclusive with --team`.

- If `--from-issue` is set with `--team`, stop. Print: `Error: --from-issue is mutually exclusive with --team (parallel JIT FIS generation not supported under this flag).` In `AUTO_MODE`, emit `BLOCKED: --from-issue is mutually exclusive with --team` and exit.
- If `--from-issue` is set with `--worktree`, stop. Print: `Error: --from-issue is mutually exclusive with --worktree (worktree isolation requires --team, which is itself rejected with --from-issue).` In `AUTO_MODE`, emit `BLOCKED: --from-issue is mutually exclusive with --worktree` and exit.


## Step 1: Plan-source resolution (`--from-issue` branch)

Replaces the local-directory `PLAN_DIR/plan.md` read. Fetch the plan-issue body with `gh issue view <N> --json body,labels` and parse it per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md):

- **Finalization gate** (granular consumer race protection): if the issue carries the label `andthen-finalizing` (set by `andthen:plan --to-issue --create-story-issues` during the two-pass `gh issue edit` rewrite window), stop. In default mode print `Plan issue #<N> is still being finalized by andthen:plan — retry once the andthen-finalizing label has been removed.` In `AUTO_MODE`, emit `BLOCKED: plan issue #<N> is still being finalized — retry after the producer completes` and exit. Apply before any other parsing.
- **Detect shape**: presence of `## Story Issues` H2 with at least one `#<digit>` reference under it → **granular**; otherwise **single-issue** (per the Shape Detection rules in `plan-issue-shape.md`, which strip fenced code blocks and HTML comments before the regex). On parser ambiguity (e.g. malformed catalog table, no `## Story Catalog` section), stop with `BLOCKED: cannot parse plan issue shape` in `AUTO_MODE`.
- **Extract Shared Decisions and Binding Constraints**: read the optional `## Shared Decisions` and `## Binding Constraints` sections from the plan-issue body (per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md) parser anchors). Hold them in working notes for inlining into per-story FIS context (see Step 3b). Both sections are optional — proceed without them when absent. Legacy plan issues carrying `## Technical Research` are tolerated (parsed if present) but the section is not materialized to disk; new plans must not emit it.
- **Build the execution plan**: parse the `## Story Catalog` table for IDs, dependencies, wave assignments. In granular shape, also map each catalog `ID` to its story-issue `#<N>` from the `## Story Issues` section.
- **Skip the FIS-existence check** — FIS files are generated just-in-time per story in Step 3 (see JIT FIS layer below).

In `--from-issue` mode there is no `PLAN_DIR` — for `CODE_DIR` auto-detection, use CWD's git root. The run slug for temp-file paths used elsewhere in this skill (e.g. `exec-plan-completion-{plan-slug}.md` in Step 5b) resolves to `issue-<N>` in this mode (full path: `.agent_temp/exec-plan-completion-issue-<N>.md`), since `PLAN_DIR` is empty.


## Step 3b: JIT FIS layer

Before the per-story pipeline, materialize the story's FIS into a local file.

**Invocation form** (both shapes): write the story body to a temp file at `<run-tempdir>/story-<story-id>-body.md`. If `## Shared Decisions` and/or `## Binding Constraints` were extracted in Step 1, prepend them verbatim above the story body so the spec skill picks them up as user-supplied context (Binding Constraints' verbatim PRD spans become Required Context blocks in the FIS, sourced from each entry's `prd.md#<heading-slug>`). Then invoke the `andthen:spec` skill with the temp-file path as the argument (file-reference form per the spec skill's argument-hint and Step 0 "Otherwise" branch). Passing the body as a literal `$ARGUMENTS` string risks newline-handling drift and shell-escape issues; the temp-file form is the contractually pinned recipe.

- **Single-issue shape**: extract the matching `### Story S0N: <name>` section from the plan-issue body (carry the H3 heading and all metadata fields), assemble the body file as described above, then invoke `/andthen:spec <run-tempdir>/story-<story-id>-body.md`. The spec skill's "Otherwise" Step 0 branch reads the file and produces the FIS at `docs/specs/<feature-name>.md` per the spec skill's `## OUTPUT` contract.
- **Granular shape**: fetch the story-issue body with `gh issue view <story-N> --json body --jq .body` for the story's mapped issue number, assemble the body file as described above, then invoke `/andthen:spec <run-tempdir>/story-<story-id>-body.md` (same mechanism as single-issue — `andthen:spec` itself does not parse a `--issue` flag).

**FIS path capture**: the spec skill prints the resolved FIS path on completion. The orchestrator captures this path (parse the printed line ending in `.md` under `docs/specs/`) and uses it as `{fis_path}` for the per-story pipeline. If the print format changes, this capture breaks — keep the spec skill's "print the output's relative path from the project root" contract pinned.

**Provenance-field injection**: the file-reference branch of `andthen:spec` does not auto-populate `**Plan**:` and `**Story-ID**:` (those fields are emitted only when invoked via the `story <id> of <plan>` form, which is unavailable in this mode). After the FIS file is written, the orchestrator MUST inject the provenance fields between the H1 heading and `## Feature Overview and Goal` per `data-contract.md` `## FIS Provenance Fields`. Use a synthetic `**Plan**: github://issue/<plan-N>` value when the plan source is a GitHub issue (no local plan path exists); `**Story-ID**: <S0N>` carries the catalog ID. Without this injection, downstream `andthen:exec-spec` and `andthen:ops` calls cannot locate the parent plan for status writes.

**Serial dispatch**: `andthen:spec` invocations run serially per story. The constraint is sub-agent fan-out coordination for JIT FIS generation, which is not implemented in this skill — it is **not** a `--team` constraint (local `andthen:plan` parallelizes via sub-agents without `--team`, so the same fan-out is feasible here). On `andthen:spec` failure for a story: surface the error, mark the story as failed, and continue with remaining stories per the existing "log and continue" failure policy.

After the FIS path is captured (and provenance fields injected), fall through to the standard per-story pipeline using that path as `{fis_path}`.


## Step 5c: Issue closure comments

After Final Verification, post shape-appropriate closure comments. Use the existing per-story completion summaries (from `andthen:exec-spec` Step 5c) and the rolled-up plan summary (Step 5).

- **Single-issue shape**: post one comment per story on the plan issue `#N` with that story's summary, then post a final rolled-up summary comment on `#N`. Use `gh issue comment <N> --body-file <path>` per call. The plan issue is not closed — the user closes manually if desired.
- **Granular shape**: for each story, follow **Pattern C** (comment-then-close) in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Then post a rolled-up summary comment on the plan issue `#N` via `gh issue comment <N> --body-file <rollup-path>`.

`gh` failure handling matches Pattern C (surface and continue) for both shapes — closure is best-effort post-implementation.


## Gate

Closure comments posted per shape (or skipped when `--from-issue` is absent).
