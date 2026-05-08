# `--from-issue` Mode (GitHub Input)

GitHub-input mechanics for `andthen:exec-plan --from-issue <N>`. Load this reference when running the `andthen:exec-plan` skill with `--from-issue` set, or when changing how plan-issue bodies are parsed, how FIS files are generated just-in-time, or how closure comments are posted back to GitHub.

The flag swaps the plan source from a local `PLAN_DIR/plan.json` to a GitHub issue body. The issue body is parsed **once** and rendered into a local `plan.json` runtime ledger; subsequent reads, scheduling decisions, and `andthen:ops` writes target that local ledger. The GitHub issue is the durable contract; the local ledger is the runtime state. FIS files are generated **just-in-time per story** by invoking the `andthen:spec` skill (which itself does not parse a `--issue` flag — the orchestrator owns the issue fetch). After the per-story pipeline completes, shape-appropriate closure comments are posted on the relevant issues; the issue body is **not** rewritten.

Companion references:
- [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md) — the canonical body shape (single-issue and granular) that this mode parses and that closure comments target.
- [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md) — the schema the materialized local ledger conforms to.
- [`team-mode-orchestration.md`](team-mode-orchestration.md) — `--team` and `--worktree` mechanics. **`--from-issue` is mutually exclusive with `--team`** (parallel JIT FIS generation is not supported under this flag).


## Step 1: Flag-combination guard

Apply both guards before any other Step 1 work. The `--worktree` guard is added here (in addition to the existing `--worktree requires --team` pre-validate in the parent SKILL.md) so the user gets a single, accurate error rather than the ping-pong between `--worktree requires --team` and `--from-issue is mutually exclusive with --team`.

- If `--from-issue` is set with `--team`, stop. Print: `Error: --from-issue is mutually exclusive with --team (parallel JIT FIS generation not supported under this flag).` In `AUTO_MODE`, emit `BLOCKED: --from-issue is mutually exclusive with --team` and exit.
- If `--from-issue` is set with `--worktree`, stop. Print: `Error: --from-issue is mutually exclusive with --worktree (worktree isolation requires --team, which is itself rejected with --from-issue).` In `AUTO_MODE`, emit `BLOCKED: --from-issue is mutually exclusive with --worktree` and exit.


## Step 1: Plan-source resolution (`--from-issue` branch)

Replaces the local-directory `PLAN_DIR/plan.json` read. Fetch the plan-issue body with `gh issue view <N> --json body,labels` and parse it per [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md):

- **Finalization gate** (granular consumer race protection): if the issue carries the label `andthen-finalizing` (set by `andthen:plan --to-issue --create-story-issues` during the two-pass `gh issue edit` rewrite window), stop. In default mode print `Plan issue #<N> is still being finalized by andthen:plan — retry once the andthen-finalizing label has been removed.` In `AUTO_MODE`, emit `BLOCKED: plan issue #<N> is still being finalized — retry after the producer completes` and exit. Apply before any other parsing.
- **Detect shape**: presence of `## Story Issues` H2 with at least one `#<digit>` reference under it → **granular**; otherwise **single-issue** (per the Shape Detection rules in `plan-issue-shape.md`, which strip fenced code blocks and HTML comments before the regex). On parser ambiguity (e.g. malformed catalog table, no `## Story Catalog` section), stop with `BLOCKED: cannot parse plan issue shape` in `AUTO_MODE`.
- **Resolve PRD source**: parse the required `> **PRD**:` header. `github://issue/<N>` sources are fetched with `gh issue view <N> --json body --jq .body`; local path sources are resolved relative to the explicit `CODE_DIR` argument when supplied, otherwise CWD's git root. For legacy plan issues without the header, fall back to the first `Refs #<N>` footer as a GitHub PRD source. If a story has `**Source refs**` but the PRD source cannot be resolved, stop with `BLOCKED: cannot resolve PRD source for story <story-id> Source refs` in `AUTO_MODE` (default mode prints the same error and stops). A compact story brief is not enough to author a complete FIS without the referenced PRD spans.
- **Extract Shared Decisions and Binding Constraints**: read the optional `## Shared Decisions` and `## Binding Constraints` sections from the plan-issue body. Both are optional — proceed when absent. Legacy plan issues carrying `## Technical Research` are tolerated (parsed if present) but the section is not materialized; new plans must not emit it.
- **Validate the Story Catalog**: parse the `## Story Catalog` table for IDs, dependencies, wave assignments. Catalog `Dependencies` cells must be `-` or comma-separated Story IDs from the same catalog. Stop on prose or unknown IDs with `BLOCKED: invalid dependency in <story-id>: "<value>" — use Story IDs in the catalog and put milestone prose in issue body notes.` In granular shape, also map each catalog `ID` to its story-issue `#<N>` from the `## Story Issues` section.

### Step 1b — Materialize the local `plan.json` ledger

Render the parsed plan-issue body into a `plan.json` per [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md), and write it to `.agent_temp/from-issue-<N>/plan.json` (path stable across reruns for resumability). Field mapping:

- `schemaVersion: "1"`.
- `prd`: the resolved PRD source — either a relative POSIX path or `"github://issue/<prd-N>"`.
- `references`: empty array (issue bodies don't carry an explicit references list — surface any in `executionNotes` if needed).
- `overview.summary`: the plan summary paragraph(s) from the issue body.
- `overview.phases`: derived from the catalog's `Phase` and `Wave` columns.
- `sharedDecisions` / `bindingConstraints`: structured renderings of the parsed sections (`title` / `description` / `stories[]` for shared decisions; `featureId` / `anchor` / `verbatim` for binding constraints). Empty arrays when the section was absent.
- `stories[]`: one entry per Story Catalog row. `status` always starts at `"pending"`, `fis` always starts at `null` — FIS files are generated just-in-time in Step 3b. Other fields map straight from the catalog row and the matching story brief (`### Story S0N: <name>` section in single-issue, fetched story-issue body in granular). For granular shape, stash the mapped `#<story-issue-N>` somewhere the orchestrator can recover it (e.g. as a synthetic field on the in-memory plan object — not part of the schema, used only during the run).
- `metadata.immutableDigest`: compute and write the canonical-form `sha256:<hex>` baseline per the **Enforcement** section in [`plan-schema.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md). The materialized ledger is a real `plan.json` — `andthen:ops update-plan` and `update-plan-fis` (Step 3b) will validate against it.

**Reconcile on rerun**: if `.agent_temp/from-issue-<N>/plan.json` already exists when materialization runs, do not overwrite blindly. Compare the issue's story-ID set against the existing local ledger:

- For story IDs present in **both**, preserve the local `status` and `fis` (those reflect actual execution state) and refresh the rest from the issue. This is how `done` work survives a rerun. **Scope-change guard**: when the issue's `scope`, `sourceRefs`, `provenance`, or `assetRefs` differ from the local entry, reset that story's `status` to `"pending"` and `fis` to `null` before refreshing — mirrors the local-mode regenerate rule in the `andthen:plan` skill's Step 1. Emit one stdout line naming the reset IDs.
- For story IDs present only in the **issue** (issue body grew between runs), append the new story to the ledger with `status: "pending"`, `fis: null`.
- For story IDs present only **locally** (issue body shrank between runs), retain the local entry but annotate `notes` with `"removed from issue on <ISO-date>"`. Do not delete completed work just because the contract was edited.

When reconciliation rewrites any non-mutable field (refreshes catalog metadata from the issue, appends new stories, annotates removed-locally entries), recompute and overwrite `metadata.immutableDigest` from the post-reconciliation document — reconciliation is an authorized regeneration, equivalent to an `andthen:plan` rerun.

After Step 1b, set `PLAN_PATH` to the materialized ledger's absolute path (`.agent_temp/from-issue-<N>/plan.json`) per the `PLAN_PATH` definition in the parent skill's VARIABLES section. The rest of `andthen:exec-plan` then runs against the materialized ledger as if it were a normal `plan.json` — the FIS-existence check (Step 1, item 5) is the one relaxation: stories with `fis: null` are expected here and trigger Step 3b's JIT FIS layer instead of aborting.

In `--from-issue` mode there is no `PLAN_DIR` — for `CODE_DIR` auto-detection, use CWD's git root. The run slug for temp-file paths used elsewhere in this skill (e.g. `exec-plan-completion-{plan-slug}.md` in Step 5b) resolves to `issue-<N>` in this mode (full path: `.agent_temp/exec-plan-completion-issue-<N>.md`).


## Step 3b: JIT FIS layer

Before the per-story pipeline, materialize the story's FIS into a local file.

**Invocation form** (both shapes): write the story body to a temp file at `<run-tempdir>/story-<story-id>-body.md`. If `## Shared Decisions` and/or `## Binding Constraints` were extracted in Step 1, prepend them verbatim above the story body so the spec skill picks them up as user-supplied context (Binding Constraints' verbatim PRD spans become Required Context blocks in the FIS, sourced from each entry's `prd.md#<heading-slug>`). Then append a `## Source Material` section containing the PRD spans named by the story's `**Source refs**`; if span extraction is uncertain, include the full resolved PRD source body rather than dropping behavior. Then invoke the `andthen:spec` skill with the temp-file path as the argument (file-reference form per the spec skill's argument-hint and Step 0 "Otherwise" branch). Passing the body as a literal `$ARGUMENTS` string risks newline-handling drift and shell-escape issues; the temp-file form is the contractually pinned recipe.

- **Single-issue shape**: extract the matching `### Story S0N: <name>` section from the plan-issue body (carry the H3 heading and compact story brief), assemble the body file as described above, then invoke `/andthen:spec <run-tempdir>/story-<story-id>-body.md`. The spec skill's "Otherwise" Step 0 branch reads the file and produces the FIS at `docs/specs/<feature-name>.md` per the spec skill's `## OUTPUT` contract.
- **Granular shape**: fetch the story-issue body with `gh issue view <story-N> --json body --jq .body` for the story's mapped issue number, assemble the body file as described above, then invoke `/andthen:spec <run-tempdir>/story-<story-id>-body.md` (same mechanism as single-issue — `andthen:spec` itself does not parse a `--issue` flag).

**FIS path capture**: the spec skill prints the resolved FIS path on completion. The orchestrator captures this path (parse the printed line ending in `.md` under `docs/specs/`) and uses it as `{fis_path}` for the per-story pipeline. If the print format changes, this capture breaks — keep the spec skill's "print the output's relative path from the project root" contract pinned.

**Provenance-field injection**: the file-reference branch of `andthen:spec` does not auto-populate `**Plan**:` and `**Story-ID**:` (those fields are emitted only when invoked via the `story <id> of <plan>` form, which is unavailable in this mode). After the FIS file is written, the orchestrator MUST inject the provenance fields between the H1 heading and `## Feature Overview and Goal` per `data-contract.md` `## FIS Provenance Fields`. Use `**Plan**: github://issue/<plan-N>` so the FIS preserves traceability back to the durable contract (the GitHub issue), even though execution drives off the local ledger; `**Story-ID**: <S0N>` carries the catalog ID.

**Update the local ledger**: once the FIS is written and provenance fields injected, drive the ledger updates through `andthen:ops` against the materialized path:

- `andthen:ops update-plan-fis <local-plan-path> <story-id> <fis-path>` to set `stories[].fis`.
- `andthen:ops update-plan <local-plan-path> <story-id> spec-ready` to advance status.

These calls land in `.agent_temp/from-issue-<N>/plan.json`, not the GitHub issue. Status updates do not propagate back to GitHub during the run; per-story closure comments in Step 5c are the issue-side completion record.

**Serial dispatch**: `andthen:spec` invocations run serially per story. The constraint is sub-agent fan-out coordination for JIT FIS generation, which is not implemented in this skill — it is **not** a `--team` constraint. On `andthen:spec` failure for a story: surface the error, mark the story as failed, and continue with remaining stories per the existing "log and continue" failure policy.

After the FIS path is captured (and the local ledger updated), fall through to the standard per-story pipeline using that path as `{fis_path}`.


## Step 5c: Issue closure comments

After Final Verification, post shape-appropriate closure comments. Use the existing per-story completion summaries (from `andthen:exec-spec` Step 5c) and the rolled-up plan summary (Step 5).

- **Single-issue shape**: post one comment per story on the plan issue `#N` with that story's summary, then post a final rolled-up summary comment on `#N`. Use `gh issue comment <N> --body-file <path>` per call. The plan issue is not closed — the user closes manually if desired.
- **Granular shape**: for each story, follow **Pattern C** (comment-then-close) in [`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md). Then post a rolled-up summary comment on the plan issue `#N` via `gh issue comment <N> --body-file <rollup-path>`.

`gh` failure handling matches Pattern C (surface and continue) for both shapes — closure is best-effort post-implementation.


## Gate

Closure comments posted per shape (or skipped when `--from-issue` is absent).
