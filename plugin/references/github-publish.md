# GitHub Publish Patterns

Canonical recipes for publishing AndThen artifacts to GitHub via the `gh` CLI. Three reusable patterns cover every current call site.

> Skills that reference this document: `clarify`, `exec-plan`, `exec-spec`, `plan`, `prd`, `triage`.

Load this when implementing or modifying any `--to-issue` / `--to-pr` / `--from-issue` step. The host skill keeps artifact-specific bits (title, labels, temp-file path) inline and refers here for the publish mechanics. Issue **body shape** (link conventions, parser-friendly section markers, single-issue vs granular) lives in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md) — this document covers publish **mechanics** only.


## Shared Gotchas

- **`gh` auth is the user's responsibility.** Skills assume `gh auth status` is clean; do not run `gh auth login` from a skill.
- **65,536-char body limit.** GitHub rejects both **issue bodies** (Pattern A) and **comment bodies** (Patterns B / C) above the limit. Every pattern below uses `--body-file` (not inline `--body "..."`) so the file system, not the shell, carries the body — this also sidesteps shell-escape issues on multi-line content. For comment producers (Patterns B / C), split into multiple comments rather than truncate. For issue-create producers (Pattern A — `prd --to-issue` and `plan --to-issue` carry the largest bodies), see Pattern A's "Body size" subsection for the create-then-supplement fallback.


## Pattern A — Create new issue with `Refs #<input-N>` provenance

**Used by**: `clarify --to-issue`, `prd --to-issue`, `triage --to-issue` (plan-only and fix flows), `plan --to-issue` (single-issue + each story body in granular).

When the host skill was invoked with an input issue (`--issue <N>` or a GitHub issue URL), append a blank line + `Refs #<N>` as the **last line** of the body. This footer is a contract — `andthen:exec-plan --from-issue` and other downstream consumers extract provenance from it; without it the chain breaks. Omit when no input issue was supplied.

The body lives in a temp file under the host's temp-dir convention (typical: `.agent_temp/<skill>/<feature-slug>-issue-body.md`); the local artifact stays the source of truth on disk and is never mutated. Then: `gh issue create --title "<title>" [--label <label>...] --body-file <body-path>`.

**The input issue is left untouched** — `--to-issue` is always create-new, never update-in-place. No comment, no edit on the source.

**Body size**: when the assembled body exceeds the 65,536-char limit, do not truncate. Create the issue with the body sans the largest extractable section (typically `## Technical Research` for plan / PRD bodies — preserve the parser-friendly H2 anchor with a single-line stub like `_See follow-up comment for full content._`), capture the new issue number, then post the omitted section as a follow-up comment on that same issue via Pattern B's mechanics (`gh issue comment <N> --body-file <section-path>`, splitting further if a single section still exceeds the limit). Surface this as a multi-step run in the host's report so the user sees the supplemental comments.

**Failure handling**: surface `gh` errors verbatim and stop. In `AUTO_MODE`: `BLOCKED: gh authentication required` (auth) or `BLOCKED: <verbatim gh error>` (other) and exit.


## Pattern B — Post existing summary as PR comment

**Used by**: `exec-spec --to-pr`, `exec-plan --to-pr`. (`review --to-pr` and `architecture --to-pr` use inline `gh pr comment` calls; they are not currently wired through this pattern.)

The body is whatever the host's prior step produced — **no new content generation here**. If the summary is not already on disk, write it under the host's temp-dir convention (typical: `.agent_temp/<skill>-completion-<slug>.md`). Then: `gh pr comment <number> --body-file <summary-path>`.

**Failure handling (default)**: surface `gh` errors verbatim and stop. In `AUTO_MODE`: `BLOCKED: gh pr comment failed for #<number>` and exit. Never roll back the local completion — the local artifact is durable; the PR-side post is a transport.

**Host-skill override**: a host may **continue** past failure when a downstream step has its own load-bearing GitHub side effect (e.g. `exec-plan --from-issue` granular issue closure in Step 5c). The override must be documented inline at the call site with the explicit reason — never silent. The default applies whenever the host does not state otherwise.


## Pattern C — Comment-then-close (deliberate 2-call) for granular issue closure

**Used by**: `exec-plan --from-issue` Step 5c granular branch.

Two-call sequence: `gh issue comment <N> --body-file <summary-path>` then `gh issue close <N>` (no body on the close).

**Why two calls and not `gh issue close --comment "..."`**: `gh issue close` accepts only an inline `--comment <string>`, not `--body-file`. Inline strings hit two failure modes on real summaries — shell-escape issues on multi-line content and the 65,536-char per-comment limit. The split routes the body through `--body-file` and reserves `gh issue close` for the state transition only.

**Failed stories: comment but do not close.** Leave the issue open so the failure stays visible; surface in the final report.

**Failure handling**: surface `gh` errors verbatim and continue. Closure is best-effort post-implementation — the local execution has already succeeded, so a comment-side or close-side failure must not roll back any local state.
