# Git and Progress Formats

Output formats for the Git Operations (`commit`, `branch`, `changelog`) and Progress Tracking (`progress`, `stale`) forms.

## Commit

Standardized commit message formatting.

**Format**: `{type}({scope}): {description}`

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`, `ci`

Rules:
- Scope is optional but recommended
- Description: imperative mood, lowercase, no period, max 72 chars
- If story context exists, append story ID: `feat(auth): add login form [S03]`

## Branch

Standardized branch naming.

**Format**: `{type}/{story-id}-{slug}`

Types: `feat`, `fix`, `refactor`, `chore`, `docs`

Example: `feat/S03-user-authentication`

Rules:
- Slug: lowercase, hyphen-separated, max 5 words
- Story ID from `plan.json` if available

## Changelog Entry

Format:
```markdown
## [{version}] – {YYYY-MM-DD}

### Added
- {description} ([S{id}])

### Changed
- {description}

### Fixed
- {description}
```

## Progress Summary

Generate a progress summary from `plan.json`.

Output:
```
## Progress Summary
- **Total Stories**: {N}
- **Done**: {done} ({percentage}%)
- **In Progress**: {in_progress}
- **Spec Ready**: {spec_ready}
- **Pending**: {pending}
- **Skipped**: {skipped}
- **Blocked**: {blocked}

### By Phase
| Phase | Total | Done | In Progress | Spec Ready | Pending | Skipped/Blocked |
|-------|-------|------|-------------|------------|---------|-----------------|
| {phase} | {n} | {n} | {n} | {n} | {n} | {n} |

### Current Wave
- Wave {N}: {status} ({done}/{total} stories complete)
```

## Stale Detection

A story is potentially stale if:
- `fis` exists but no task checkboxes are checked
- All entries in `dependsOn` have `status: "done"` but the story is still `pending` or `spec-ready`

Output: List of potentially stale stories with reasons.
