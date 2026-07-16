# `--from-issue` Mode (GitHub Input)

GitHub-input mechanics for `andthen:exec-plan --from-issue <N>`. Load when running with `--from-issue`, or when changing how plan-issue bodies are parsed, how FIS files are generated JIT, or how closure comments are posted.

The flag swaps the plan source from a local `PLAN_DIR/plan.json` to a GitHub issue body. The issue body is parsed **once** and materialized into a local `plan.json`; subsequent reads, scheduling, and the `andthen:ops` skill's writes target the local plan. GitHub issue = durable contract; local `plan.json` = runtime state. FIS files are generated **just-in-time per story** via the `andthen:spec` skill (the orchestrator owns the issue fetch). After the per-story pipeline completes, shape-appropriate closure comments are posted; the issue body is **not** rewritten.

Companion references:
- [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md) – body shape parsed here.
- [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) – plan schema.
- [`team-mode-orchestration.md`](team-mode-orchestration.md) – `--team` / `--worktree`. **`--from-issue` is mutually exclusive with `--team`.**


## Step 1: Flag-combination guard

Apply both guards before any other Step 1 work. The `--worktree` guard is duplicated here (alongside parent SKILL.md's pre-validate) so the user sees one accurate error.

- `--from-issue` + `--team` → stop. `Error: --from-issue is mutually exclusive with --team (parallel JIT FIS generation not supported under this flag).` `AUTO_MODE`: `BLOCKED: --from-issue is mutually exclusive with --team`.
- `--from-issue` + `--worktree` → stop. `Error: --from-issue is mutually exclusive with --worktree (worktree isolation requires --team, which is itself rejected with --from-issue).` `AUTO_MODE`: `BLOCKED: --from-issue is mutually exclusive with --worktree`.


## Step 1: Plan-source resolution (`--from-issue` branch)

Replaces the local `PLAN_DIR/plan.json` read. Fetch with `gh issue view <N> --json body,labels` and parse per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md):

- **Finalization gate** (granular race protection): if the issue carries the label `andthen-finalizing` (set by `andthen:plan --to-issue --create-story-issues` during its two-pass rewrite window), stop. Default mode: `Plan issue #<N> is still being finalized by andthen:plan – retry once the andthen-finalizing label has been removed.` `AUTO_MODE`: `BLOCKED: plan issue #<N> is still being finalized – retry after the producer completes`. Apply before any other parsing.
- **Detect shape**: `## Story Issues` H2 with ≥1 story-issue reference line under it → **granular**; otherwise **single-issue** (per Shape Detection in `plan-issue-shape.md`, which strips fenced code/HTML comments before regex). The canonical granular producer shape is a bullet line beginning `- #<story-issue-N>`; parser ambiguity → `BLOCKED: cannot parse plan issue shape` in `AUTO_MODE`.
- **Resolve PRD source**: parse the required `> **PRD**:` header. `github://issue/<N>` → fetch with `gh issue view <N> --json body --jq .body`; local paths resolve relative to explicit `CODE_DIR` or CWD's git root. Legacy issues without the header fall back to the first `Refs #<N>` footer. If a story has `**Source refs**` but PRD source can't be resolved: `BLOCKED: cannot resolve PRD source for story <story-id> Source refs` in `AUTO_MODE` (default mode prints the same error and stops). A compact brief is insufficient without referenced spans.
- **Extract Shared Decisions and Binding Constraints**: read optional `## Shared Decisions` and `## Binding Constraints` sections. Legacy `## Technical Research` is tolerated but not materialized; new plans must not emit it.
- **Validate the Story Catalog**: parse `## Story Catalog`. `Dependencies` cells are `-` or comma-separated Story IDs from the same catalog. Prose or unknown IDs → `BLOCKED: invalid dependency in <story-id>: "<value>" – use Story IDs in the catalog and put milestone prose in issue body notes.` Granular: also map each `ID` to its story-issue `#<N>` from `## Story Issues`.

### Step 1b – Materialize the local `plan.json`

Render the parsed issue body into `plan.json` per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) and write to `.agent_temp/from-issue-<N>/plan.json` (path stable across reruns). Field mapping:

- `schemaVersion: "1"`.
- `prd`: resolved PRD source – relative POSIX path or `"github://issue/<prd-N>"`.
- `references`: `[]` (surface any in `executionNotes` if needed).
- `overview.summary`: the plan summary paragraph(s).
- `overview.phases`: derived from catalog `Phase` / `Wave` columns.
- `sharedDecisions` / `bindingConstraints`: structured renderings of parsed sections. Empty arrays when absent.
- `stories[]`: one per catalog row. `status` starts `"pending"`, `fis` starts `null` (JIT in Step 3b). Other fields map from catalog row + story brief (`### Story S0N: <name>` in single-issue; fetched story-issue body in granular). Granular: stash the mapped `#<story-issue-N>` on the in-memory plan (synthetic field, run-only, not schema).

**Reconcile on rerun**: when `.agent_temp/from-issue-<N>/plan.json` already exists, compare the issue's story-ID set against the existing plan:

- IDs in **both**: apply the **Preservation predicate** ([`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) **Writability rules**) against local vs issue. Predicate holds → preserve local `status`/`fis` (actual execution state) and refresh the rest – including `owner`, which always re-reads from the issue's Owner cell (claims live on the issue, the durable contract; empty/sentinel cell → `null`). This is how `done` work survives a rerun and teammates' claims propagate to every materialized plan. Predicate fails (content drift or missing FIS file) → reset to `pending`/`null` before refreshing. Emit: `Regenerated plan.json (from issue); preserved status/fis: <id-list>; owner refreshed from issue.` and (when applicable) `Reset to pending/null: <id-list>.`
- IDs only in the **issue** (grew): append with `status: "pending"`, `fis: null`, `owner` from the issue's Owner cell (or `null`).
- IDs only **locally** (shrank): retain; annotate `notes` with `"removed from issue on <ISO-date>"`. Do not delete completed work.

After 1b, set `PLAN_PATH` to the absolute path of the materialized plan. The rest of exec-plan runs as if it were a normal `plan.json` – the FIS-existence check (Step 1.5) is relaxed; `fis: null` triggers Step 3b's JIT layer.

In `--from-issue` there is no `PLAN_DIR` – for `CODE_DIR` auto-detection, use CWD's git root. Run-slug for temp-file paths (e.g. Step 5b's completion summary) resolves to `issue-<N>`.


## Step 3b: JIT FIS layer

Materialize the story's FIS into a local file before the per-story pipeline.

**Invocation form** (both shapes): write the story body to `<run-tempdir>/story-<story-id>-body.md`. If `## Shared Decisions` and/or `## Binding Constraints` were extracted in Step 1, prepend them verbatim so the spec skill picks them up as user-supplied context (Binding Constraints' verbatim spans become Required Context blocks sourced from each entry's `prd.md#<heading-slug>`). Then append `## Source Material` with the PRD spans named by the story's `**Source refs**`; if span extraction is uncertain, include the full PRD body. Invoke the `andthen:spec` skill with the temp-file path (file-reference form). Passing the body as `$ARGUMENTS` risks newline/shell-escape issues; the temp-file form is the pinned recipe.

- **Single-issue shape**: extract the matching `### Story S0N: <name>` section from the plan-issue body (H3 + compact brief), assemble the body file, then invoke the andthen:spec skill on `<run-tempdir>/story-<story-id>-body.md`. The spec skill's "Otherwise" branch reads the file and prints the relative `.md` path it wrote, resolved by the spec skill's own output-location rules.
- **Granular shape**: `gh issue view <story-N> --json body --jq .body` for the story's mapped issue, assemble, invoke the `andthen:spec` skill the same way (the spec skill does not parse `--issue`).

**FIS path capture**: parse the spec skill's printed relative path (ends in `.md`). Use as `{fis_path}`. If the print format changes, this capture breaks – keep the spec skill's "print the output's relative path" contract pinned.

**Provenance-field injection**: the `andthen:spec` skill's file-reference branch does not auto-emit `**Plan**:` / `**Story-ID**:` (only the `story <id> of <plan>` form does). After the FIS is written, the orchestrator MUST inject these between the H1 and `## Feature Overview and Goal` per [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) `## FIS Provenance Fields`. Use `**Plan**: github://issue/<plan-N>` (traceability to the durable contract) and `**Story-ID**: <S0N>`.

**Update the local plan**: after FIS write + provenance injection, drive via the `andthen:ops` skill against the materialized path:

- `andthen:ops update-plan-fis <local-plan-path> <story-id> <fis-path>`.
- `andthen:ops update-plan <local-plan-path> <story-id> spec-ready` – only when spec's self-review reported no blocking signal (`MISSING REQUIREMENT:` / `BLOCKED:`). A blocking signal holds the story: keep the FIS pointer, do not advance to `spec-ready`, treat it as a spec failure (mark failed, skip exec per *Serial dispatch* below), and surface the unresolved decision.

These land in `.agent_temp/from-issue-<N>/plan.json`, not the GitHub issue. Status updates do not propagate back to GitHub during the run; Step 5c posts closure comments.

**Serial dispatch**: the `andthen:spec` skill's invocations run serially – sub-agent fan-out for JIT FIS generation is not implemented here because `--team` was rejected earlier. Spec failure → surface, mark story failed, continue with remaining stories ("log and continue").

After capture + plan update, fall through to the standard per-story pipeline using `{fis_path}`.


## Step 5c: Issue closure comments

After Final Verification, prepare shape-appropriate closure comments. Use per-story summaries (from the `andthen:exec-spec` skill's Step 5c) and the rolled-up plan summary (Step 5).

- **Single-issue shape**: post one comment per story on plan issue `#N` with the story summary, then a final rolled-up summary on `#N`. Use `gh issue comment <N> --body-file <path>` per call. Plan issue is not auto-closed.
- **Granular shape**: per story, prepare the **Pattern C** (comment-then-close) payloads from [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Then prepare the rolled-up summary for plan issue `#N`.

`gh` failure handling matches Pattern C (surface and continue) – closure is best-effort.


## Gate

Closure comments prepared per shape (or skipped when `--from-issue` is absent); posting waits for the `andthen:exec-plan` skill's Step 6 completion-presentation gate.
