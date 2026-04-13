# GitHub Artifact Round-Trip Conventions

Use this reference when a skill publishes an AndThen workflow artifact to GitHub or consumes one from a GitHub issue / PR comment.

## Goals
- GitHub-hosted artifacts must be human-readable **and** machine-consumable
- Publishing must preserve enough structure for downstream skills to continue from GitHub alone
- Consumers must validate artifact type before acting; incompatible handoffs fail closed

## Typed Envelope

Wrap the GitHub issue body or PR comment in a typed envelope, then embed the artifact files as fenced blocks.

````markdown
<!-- ANDTHEN_ARTIFACT:BEGIN -->
```yaml
schema: andthen/github-artifact-v1
artifact_type: plan-bundle
source_skill: andthen:plan
canonical_local_primary: docs/specs/my-feature/plan.md
canonical_local_companions:
  - docs/specs/my-feature/prd.md
  - docs/specs/my-feature/technical-research.md
plan_path: docs/specs/my-feature/plan.md
fis_path:
report_path:
story_ids: []
requirements_baseline:
  - docs/specs/my-feature/prd.md
  - docs/specs/my-feature/plan.md
implementation_targets: []
source_issue_number: 42
```
<!-- ANDTHEN_ARTIFACT:END -->

## Human Summary
[short operator-oriented overview]

## Artifact Files

### File: docs/specs/my-feature/plan.md (primary)
```markdown
[exact file contents]
```

### File: docs/specs/my-feature/prd.md
```markdown
[exact file contents]
```
````

## Metadata Rules
- Use relative repo paths when known. Do not emit absolute paths.
- `canonical_local_primary` is the deterministic primary artifact a downstream skill must resume from. Consumers should fail closed if it is missing, ambiguous, or not present among the embedded file blocks.
- `canonical_local_companions` lists sibling files required for faithful continuation.
- Embedded `### File:` headings must use repo-relative paths, not bare filenames. The heading path must exactly match `canonical_local_primary` or an entry in `canonical_local_companions`.
- Populate `plan_path`, `fis_path`, `report_path`, `story_ids`, `requirements_baseline`, `implementation_targets`, and `source_issue_number` whenever the skill knows them. Empty values are acceptable when genuinely unknown.
- For a FIS created from a plan story or composite story set, populate `plan_path` and `story_ids`, and include the current `plan.md` as a companion file.
- Embedded file blocks contain the **exact artifact contents**, not summaries or paraphrases.
- Keep `## Human Summary` concise; the embedded files are the source of truth.

## Standard Artifact Types
- `plan-bundle` — `plan.md` primary; include sibling `prd.md`; include `technical-research.md` when present; when resuming after spec generation or execution, also include any FIS files referenced by `plan.md` that downstream steps now depend on
- `fis-bundle` — FIS primary; include `technical-research.md` when present; if the FIS originated from a plan story, include `plan.md` and populate `plan_path` / `story_ids`
- `triage-plan` — investigation / fix plan primary
- `triage-completion` — completion summary with verification evidence primary
- `gap-review`, `code-review`, `architecture-review`, `doc-review`, `council-review` — review reports; the report file is the primary artifact

Add narrower types only when a downstream consumer needs distinct behavior.

## Publishing Rules
- GitHub issues: add the type-specific labels plus `andthen-artifact`
- GitHub PR comments: publish the same typed envelope; print the **direct comment URL**
- When downstream execution or review requires companion files, include them as embedded `### File:` sections and list them in `canonical_local_companions`
- At completion, print both the GitHub URL and the local primary path
- If the posting command does not return a direct comment URL, resolve it immediately via follow-up GitHub lookup and print that URL before completion

## Consumption Rules
- For GitHub issue / PR comment inputs, inspect the body for the typed envelope **before** treating the text as ordinary prose
- If the envelope exists, validate `schema` and `artifact_type` first
- If compatible, extract each embedded file verbatim into `.agent_temp/github-artifacts/{github-id}-{artifact_type}/`, preserving the repo-relative paths from the `### File:` headings. Use `canonical_local_primary` to choose the primary extracted file
- If typed but incompatible with the current skill, stop and tell the user which artifact type or skill is expected
- If the current skill requires a specific workflow artifact (plan, FIS, review report), do **not** guess from an untyped GitHub shell page or free-form issue body. Stop and ask for the typed artifact or the local file instead
- Requirements-oriented skills may still consume untyped issues as raw requirements input when that is already part of their normal contract

## Continuation Rules
- An extracted `.agent_temp/github-artifacts/...` directory is a **working mirror**, not canonical state
- If the mirrored artifact also exists locally at the declared canonical path(s), switch to those real workspace files before mutating anything
- If a skill mutates only the extracted mirror, it must sync those changes back to canonical state before completion:
  - Prefer updating the real local files when the canonical local paths exist in the workspace
  - Otherwise update the source GitHub issue / PR comment (or create a successor typed artifact and print its URL) so the authoritative GitHub artifact contains the latest plan/FIS/report state
- Never leave `.agent_temp/github-artifacts/...` as the only updated copy of a workflow artifact

## Resolve Plan-Bundle Input

Reusable procedure for skills that accept `<path-to-plan | --issue <number> | issue URL>` and need a local `PLAN_DIR`. The calling skill provides incompatible-type routing inline.

1. **Local directory path**: use it as `PLAN_DIR`. Set `PLAN_SOURCE_MODE = local`.
2. **`--issue <number>` or GitHub issue URL**:
   a. Fetch the issue body and inspect the typed envelope (validate `schema` and `artifact_type`)
   b. Require `artifact_type: plan-bundle` — if incompatible, apply the calling skill's routing table
   c. If untyped, **STOP** — the calling skill requires a typed plan artifact, not a free-form issue
   d. Extract embedded files into `.agent_temp/github-artifacts/{github-id}-plan-bundle/`, preserving the repo-relative paths from `### File:` headings
   e. Resolve `PLAN_FILE_PATH` from `canonical_local_primary`; set `PLAN_DIR` to its parent directory
   f. Store `SOURCE_ISSUE` (issue number or URL) from the envelope's `source_issue_number` or from the input — needed by the continuation sync to know which issue to update
   g. **Canonical-local fallback**: if `PLAN_FILE_PATH` already exists in the workspace, switch to that real file, set `PLAN_DIR` to its parent, and set `PLAN_SOURCE_MODE = local` — the extracted directory becomes a read-only reference
   h. Otherwise set `PLAN_SOURCE_MODE = github-artifact`

After resolution, the calling skill has `PLAN_DIR`, `PLAN_FILE_PATH`, `PLAN_SOURCE_MODE`, and (when from GitHub) `SOURCE_ISSUE`. Consumers should use `PLAN_FILE_PATH` (not a hardcoded filename) when reading the plan, since `canonical_local_primary` may use a non-standard name.

## Plan-Bundle Continuation Sync

Apply when `PLAN_SOURCE_MODE = github-artifact` — both incrementally (after each plan/FIS status update) and as a final gate before the skill finishes.

- If the declared canonical local plan/FIS paths exist in the workspace, verify all updated files landed there
- Otherwise update `SOURCE_ISSUE` to the latest typed `plan-bundle`, including the updated `plan.md`, `prd.md`, `technical-research.md` when present, and every FIS file referenced by `plan.md` that now exists
- Never finish with the extracted mirror as the only updated copy

## Direct URLs
- Issues: print and accept the issue URL
- PR comments: print and accept the direct comment URL, not just the PR URL or a generic confirmation
