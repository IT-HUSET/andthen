# Resolve GitHub Input

Standard procedure for skills that accept `--issue <number>` or a GitHub issue/PR URL as input. The calling skill provides its **compatible types** and **redirect targets** inline.

## Procedure

1. **Fetch**: `gh issue view <number>` (or fetch the URL body)
2. **Inspect envelope**: Look for the typed envelope (`<!-- ANDTHEN_ARTIFACT:BEGIN -->`) in the body. Validate `schema: andthen/github-artifact-v1` and read `artifact_type`.
3. **Route on type**:
   - **Compatible type** → extract embedded files into `.agent_temp/github-artifacts/{github-id}-{artifact_type}/`, preserving repo-relative paths from `### File:` headings. Use `canonical_local_primary` to identify the primary file. Recover metadata: `plan_path`, `fis_path`, `report_path`, `story_ids`, `requirements_baseline`, `implementation_targets`, `source_issue_number`.
   - **Typed but incompatible** → **STOP** and direct user to the skill listed in the calling skill's redirect table.
   - **Untyped** → apply the calling skill's untyped-input rule (use as prose input, or STOP if the skill requires a typed artifact).
4. **Canonical-local fallback**: If `canonical_local_primary` (or other declared canonical paths) already exist in the workspace, switch to those real files and treat the extracted directory as a read-only reference.

## Calling Skill Contract

Each skill that loads this reference must specify inline:
- **Compatible types**: which `artifact_type` values the skill accepts and what to do with each
- **Incompatible-type redirects**: which skill to name in the STOP message for each incompatible type
- **Untyped rule**: whether an untyped issue is usable input or requires a STOP
