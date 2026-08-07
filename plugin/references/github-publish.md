# GitHub Publish Patterns

Canonical `gh` CLI recipes for publishing AndThen artifacts. Three reusable patterns cover every call site.

> Skills that reference this document: `clarify`, `exec-plan`, `exec-spec`, `issue-triage`, `plan`, `prd`, `triage`.

Load when implementing or modifying any `--to-issue` / `--to-pr` / `--from-issue` step. Host skills keep artifact-specific bits (title, labels, temp-file path) inline and defer here for publish mechanics. Issue **body shape** (link conventions, parser anchors, single-issue vs granular) lives in [`plan-issue-shape.md`](${CLAUDE_PLUGIN_ROOT}/references/plan-issue-shape.md); this document covers **mechanics** only.


## Tracker resolution

`docs/ISSUE-TRACKER.md` is security-critical executable config – its operation-table values are run as commands, so review changes to it as code.

- **Resolve** – before any issue operation, resolve the `Issue Tracker` document (see **Project Document Index**; default `docs/ISSUE-TRACKER.md`). Absent, `Backend: none`, or `Backend: GitHub` → use the `gh` patterns in this file (`none` ≡ absent: the built-in default, exact current behavior). Any other named backend → substitute each operation per the document's operation table. A present document whose `Backend:` line is missing or unparseable → `BLOCKED: issue-tracker backend unspecified – set the Backend: line in <tracker-doc path>`.
- **Operation vocabulary** – used wherever an issue op is named: `fetch issue`, `list issues`, `create issue`, `comment`, `edit body`, `add label` / `remove label`, `close issue`. Child-issue publishing, the `Depends on #N` / `Part of #N` / `Refs #N` footers, Owner cells, and `andthen-finalizing` are conventions layered on these ops – they carry no ops of their own and keep their names on every backend.
- **Value constraints** – every body shape, label name, and footer token stays identical across backends (the document maps transport, not contract). Backends must expose numeric issue identifiers; `<N>` in every flag, footer, and token is the backend's issue number. Each operation-table value is a single direct command invocation – an executable, fixed arguments, and `<placeholders>` – with no pipes, shell operators, command substitution, or piping to an interpreter.
- **Validate** – before the first tracker operation (reads included), validate that every operation the invoked flow needs is mapped; an unmapped load-bearing operation → `BLOCKED: issue-tracker operation <op> unmapped` before any external call, so a read-only flow with an unmapped `fetch issue` stops up front and a multi-op write never strands partial external state. An operation used only in a best-effort posture (e.g. Pattern C closure) degrades per that Pattern's failure posture instead of hard-stopping.

Pattern B (`gh pr comment`) and every PR flow stay GitHub-native: PRs are not tracker-abstracted.

## Durability rule

Descriptive published bodies – PRD issues, plan-issue overview/summary sections, issue-triage agent briefs, comments – outlive the code snapshot: no file paths, no line numbers, no code snippets; name interfaces (types, signatures, commands) and behavior instead. Exception: a snippet that itself encodes a settled decision (schema, state machine, type) may be inlined, trimmed to the decision-carrying part. Exempt: the machine-parsed catalog/anchor and footer tokens consumers resolve (story `Source refs`, `Refs #N` / `Part of #N` / `Depends on #N`); embedded FIS payloads in story issues (transport for `--from-issue` execution, consumed promptly – Required Context stays load-bearing); and local FIS/plan files.


## Shared Gotchas

- **`gh` auth is the user's responsibility.** Skills assume `gh auth status` is clean; do not run `gh auth login`.
- **65,536-char body limit.** GitHub rejects issue bodies (Pattern A) and comment bodies (Patterns B / C) above the limit. Every pattern uses `--body-file` (not inline `--body "..."`) so the filesystem carries the body and shell-escape on multi-line content is moot. Comment producers (B / C) split into multiple comments rather than truncate. Issue-create producers (Pattern A – `prd --to-issue` and `plan --to-issue` carry the largest bodies) use Pattern A's "Body size" create-then-supplement fallback.


## Pattern A – Create new issue with `Refs #<input-N>` provenance

**Used by**: `clarify --to-issue`, `prd --to-issue`, `triage --to-issue` (plan-only and fix flows), `plan --to-issue` (single-issue + each story body in granular).

When the host was invoked with an input issue (`--issue <N>` or a GitHub issue URL), append a blank line + `Refs #<N>` as the **last line** of the body. This footer is a contract – the `andthen:exec-plan` skill's `--from-issue` flow and other consumers extract provenance from it; without it the chain breaks. Omit when no input issue was supplied.

Body lives in a temp file under the host's temp-dir convention (typical: `.agent_temp/<skill>/<feature-slug>-issue-body.md`); the local artifact is the source of truth on disk and is never mutated. Then: `gh issue create --title "<title>" [--label <label>...] --body-file <body-path>`.

**The input issue is left untouched** – `--to-issue` is always create-new, never update-in-place.

**Body size**: when the body exceeds the 65,536-char limit, do not truncate. Create the issue with the body minus the largest extractable section (typically `## Binding Constraints` for plan bodies with many verbatim PRD spans, or per-story sections – preserve the parser-anchor H2 with a single-line stub like `_See follow-up comment for full content._`), capture the new issue number, then post the omitted section via Pattern B (`gh issue comment <N> --body-file <section-path>`, splitting further if a section still exceeds the limit). Surface as a multi-step run in the host's report so the user sees the supplemental comments.

**Failure handling**: surface `gh` errors verbatim and stop. `AUTO_MODE`: `BLOCKED: gh authentication required` (auth) or `BLOCKED: <verbatim gh error>` (other) and exit.


## Pattern B – Post existing summary as PR comment

**Used by**: `exec-spec --to-pr`, `exec-plan --to-pr`. (`review --to-pr` and `architecture --to-pr` use inline `gh pr comment`; not wired through this pattern.)

Body is whatever the host's prior step produced – **no new content generation here**. If not on disk, write to the host's temp-dir convention (typical: `.agent_temp/<skill>-completion-<slug>.md`). Resolve the canonical GitHub `owner/name` from the implementation target's captured git root, verify the numbered PR there with `gh pr view <number> --repo <owner/name>`, then post via `gh pr comment <number> --repo <owner/name> --body-file <summary-path>`. Unresolved identity or membership blocks.

**Failure handling (default)**: surface `gh` errors verbatim and stop. `AUTO_MODE`: `BLOCKED: gh pr comment failed for #<number>` and exit. Never roll back the local completion – the local artifact is durable; the PR-side post is transport.

**Host-skill override**: a host may **continue** past failure when a downstream step has its own load-bearing GitHub side effect (e.g. `exec-plan --from-issue` granular issue closure in Step 5c). The override must be documented inline at the call site with explicit reason – never silent. The default applies whenever the host does not state otherwise.


## Pattern C – Comment-then-close (deliberate 2-call) for granular issue closure

**Used by**: `exec-plan --from-issue` Step 5c granular branch.

Two-call: `gh issue comment <N> --body-file <summary-path>` then `gh issue close <N>` (no body on the close).

**Why two calls and not `gh issue close --comment "..."`**: `gh issue close` only accepts inline `--comment <string>`, not `--body-file`. Inline strings hit shell-escape on multi-line content and the 65,536-char per-comment limit. The split routes the body through `--body-file` and reserves `gh issue close` for the state transition.

**Failed stories: comment but do not close.** Leave the issue open so the failure stays visible; surface in the final report.

**Failure handling**: surface `gh` errors verbatim and continue. Closure is best-effort post-implementation – local execution has already succeeded, so a comment-side or close-side failure must not roll back any local state.
