# GitHub Publish Patterns

Canonical `gh` CLI recipes for publishing AndThen artifacts. Three reusable patterns cover every call site.

> Skills that reference this document: `clarify`, `exec-plan`, `exec-spec`, `plan`, `prd`, `triage`.

Load when implementing or modifying any `--to-issue` / `--to-pr` / `--from-issue` step. Host skills keep artifact-specific bits (title, labels, temp-file path) inline and defer here for publish mechanics. Issue **body shape** (link conventions, parser anchors, single-issue vs granular) lives in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md); this document covers **mechanics** only.


## Shared Gotchas

- **`gh` auth is the user's responsibility.** Skills assume `gh auth status` is clean; do not run `gh auth login`.
- **65,536-char body limit.** GitHub rejects issue bodies (Pattern A) and comment bodies (Patterns B / C) above the limit. Every pattern uses `--body-file` (not inline `--body "..."`) so the filesystem carries the body and shell-escape on multi-line content is moot. Comment producers (B / C) split into multiple comments rather than truncate. Issue-create producers (Pattern A – `prd --to-issue` and `plan --to-issue` carry the largest bodies) use Pattern A's "Body size" create-then-supplement fallback.


## Pattern A – Create new issue with `Refs #<input-N>` provenance

**Used by**: `clarify --to-issue`, `prd --to-issue`, `triage --to-issue` (plan-only and fix flows), `plan --to-issue` (single-issue + each story body in granular).

When the host was invoked with an input issue (`--issue <N>` or a GitHub issue URL), append a blank line + `Refs #<N>` as the **last line** of the body. This footer is a contract – `andthen:exec-plan --from-issue` and other consumers extract provenance from it; without it the chain breaks. Omit when no input issue was supplied.

Body lives in a temp file under the host's temp-dir convention (typical: `.agent_temp/<skill>/<feature-slug>-issue-body.md`); the local artifact is the source of truth on disk and is never mutated. Then: `gh issue create --title "<title>" [--label <label>...] --body-file <body-path>`.

**The input issue is left untouched** – `--to-issue` is always create-new, never update-in-place.

**Body size**: when the body exceeds the 65,536-char limit, do not truncate. Create the issue with the body minus the largest extractable section (typically `## Binding Constraints` for plan bodies with many verbatim PRD spans, or per-story sections – preserve the parser-anchor H2 with a single-line stub like `_See follow-up comment for full content._`), capture the new issue number, then post the omitted section via Pattern B (`gh issue comment <N> --body-file <section-path>`, splitting further if a section still exceeds the limit). Surface as a multi-step run in the host's report so the user sees the supplemental comments.

**Failure handling**: surface `gh` errors verbatim and stop. `AUTO_MODE`: `BLOCKED: gh authentication required` (auth) or `BLOCKED: <verbatim gh error>` (other) and exit.


## Pattern B – Post existing summary as PR comment

**Used by**: `exec-spec --to-pr`, `exec-plan --to-pr`. (`review --to-pr` and `architecture --to-pr` use inline `gh pr comment`; not wired through this pattern.)

Body is whatever the host's prior step produced – **no new content generation here**. If not on disk, write to the host's temp-dir convention (typical: `.agent_temp/<skill>-completion-<slug>.md`). Then: `gh pr comment <number> --body-file <summary-path>`.

**Failure handling (default)**: surface `gh` errors verbatim and stop. `AUTO_MODE`: `BLOCKED: gh pr comment failed for #<number>` and exit. Never roll back the local completion – the local artifact is durable; the PR-side post is transport.

**Host-skill override**: a host may **continue** past failure when a downstream step has its own load-bearing GitHub side effect (e.g. `exec-plan --from-issue` granular issue closure in Step 5c). The override must be documented inline at the call site with explicit reason – never silent. The default applies whenever the host does not state otherwise.


## Pattern C – Comment-then-close (deliberate 2-call) for granular issue closure

**Used by**: `exec-plan --from-issue` Step 5c granular branch.

Two-call: `gh issue comment <N> --body-file <summary-path>` then `gh issue close <N>` (no body on the close).

**Why two calls and not `gh issue close --comment "..."`**: `gh issue close` only accepts inline `--comment <string>`, not `--body-file`. Inline strings hit shell-escape on multi-line content and the 65,536-char per-comment limit. The split routes the body through `--body-file` and reserves `gh issue close` for the state transition.

**Failed stories: comment but do not close.** Leave the issue open so the failure stays visible; surface in the final report.

**Failure handling**: surface `gh` errors verbatim and continue. Closure is best-effort post-implementation – local execution has already succeeded, so a comment-side or close-side failure must not roll back any local state.
