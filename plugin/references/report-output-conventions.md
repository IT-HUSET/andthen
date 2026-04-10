# Shared Review Report Output Conventions

Use this reference when a review skill needs to explain where to write its report and how to name it.

## Required Caller-Supplied Values
- **Report suffix**: short kebab-case suffix such as `code-review`, `doc-review`, `gap-review`, or `council-review`
- **Scope placeholder**: the skill-specific scope token used in the filename, such as `<feature-name>`, `<spec-name>`, or `<scope>`
- **Spec-directory rule**: the condition for storing the report in a feature/spec directory
- **Target-directory rule**: the condition for storing the report next to the primary review target

## Standard Rules
- **Output directory resolution order**: Apply in this priority: (1) **spec directory** — if the spec-directory rule matches, write there; (2) **target directory** — if the target-directory rule matches, write next to the review target; (3) **fallback** — write to `{AGENT_TEMP}/reviews/` where `{AGENT_TEMP}` is the Agent Temp path from the Project Document Index (default: `.agent_temp/`).
- **Agent identifier**: Determine your agent short name (for example `claude`, `codex`, `cursor`, `aider`). If uncertain, use `agent`.
- **File collision avoidance**: Before writing, check whether the target filename already exists. If it does, append `-2`, `-3`, and so on. Never overwrite an existing report.
- **Filename format**: `<{scope-placeholder}>-{report-suffix}-<agent>-<YYYY-MM-DD>.md`
- **Completion output**: When complete, print the report's relative path from the project root. Do not use absolute paths.

## Optional GitHub Publishing
Only include this when the calling skill already supports `--to-issue` or `--to-pr`.

- **Publish to issue**: Create a GitHub issue using the skill-specific title template and the report content as the body, then print the issue URL.
- **Publish to PR**: Post the report as a PR comment using the skill-specific command or integration, then print confirmation.
