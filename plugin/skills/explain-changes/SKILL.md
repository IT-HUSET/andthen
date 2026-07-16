---
description: Explain what changed in a PR, branch, or changeset as a narrative Changeset Walkthrough, rendered as an interactive HTML tour. Comprehension only – for findings or a verdict use the andthen:review skill. Trigger on 'explain this PR', 'what changed on this branch', 'changeset walkthrough'.
argument-hint: "[<base-ref> | <base>..<head> | --from-pr <N>] [--to-pr [<N>]] [--no-visual] [--auto]"
user-invocable: true
---

# Explain Changes

Turns a changeset – PR, branch, ref range, or working tree – into a **Changeset Walkthrough**: a narrative, intent-grouped explanation of what changed, why, and where it sits architecturally, rendered as an interactive HTML tour. The deliverable is *comprehension*, not judgment: the walkthrough carries no findings and no verdict (the `andthen:review` skill owns those).

**Untangle-then-Tour** – the load-bearing principle. A raw diff overwhelms because it orders files alphabetically and tangles unrelated intents into one wall. Readers reason measurably better over changes grouped by *intent* (behavior vs refactor vs config vs tests vs docs) and ordered by *conceptual importance*, with only the load-bearing hunks shown. The walkthrough does that untangling once so every reader doesn't have to. Every analysis decision below serves this principle.

**Read-only by contract**: never mutate the working tree, apply the diff, or check anything out. PR mode reads via `gh` only. No tracked file changes – all writes are confined to `.agent_temp/`.


## VARIABLES

TARGET: $ARGUMENTS with all flags stripped – a base ref (e.g. `main`), an explicit range (`main..feat/x`), or empty (auto-resolve). `--from-pr <N>` supplies the scope instead of TARGET.
AUTO_MODE: true when `--auto` is passed – make conservative assumptions, stop with `BLOCKED:` on contract failures.


## WORKFLOW

### 1. Resolve the changeset

| TARGET | Scope |
|---|---|
| `--from-pr <N>` | The PR. `gh pr view <N> --json number,title,baseRefName,headRefName,headRefOid,files,body` for metadata + intent context (PR body); `gh pr diff <N>` for the diff; `gh api repos/:owner/:repo/contents/<path>?ref=<headRefOid>` for full-file content on demand. Do not check out. Reject when a local ref was also supplied – `--from-pr` is the scope, do not mix. Surface `gh` failures verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR <N> not found` under AUTO_MODE). |
| `<base>..<head>` | That range: `git diff <base>..<head>` + `git log <base>..<head>`. |
| `<base-ref>` | Current branch vs base: diff and log against `git merge-base <base-ref> HEAD`. |
| empty | Current branch vs merge-base with the default branch. If the branch has no commits ahead, use working-tree changes (staged + unstaged) instead. |

Gather alongside the diff: `--stat` totals, per-file change kind (new/modified/deleted/renamed), commit messages, and **intent context** – the PR body, a governing FIS/PRD when one names this work, or commit-message trailers. Intent context anchors cluster naming and the TL;DR; without it, derive intent from the code itself and say so.

**Gate**: scope resolved, file list + stats in hand, intent context gathered or explicitly absent.

### 2. Analyze – untangle, order, distill

Produce these analysis products (large diffs: delegate per-area scanning to parallel sub-agents that return distilled briefs; synthesis stays here):

1. **Intent clusters.** Partition every changed file into exactly one cluster by *why it changed*: `behavior` (user/system-visible change), `refactor` (shape change, behavior preserved), `config`, `tests`, `docs`. A file serving two intents goes with its primary one – note the secondary in its role line. Name each cluster by its purpose ("Extract retry policy from the HTTP client"), not its mechanics.
2. **Narrative order.** Order clusters by conceptual importance – the change a reader must understand first (usually the behavior cluster) leads; mechanical fallout trails. Within a cluster, order files the same way.
3. **Key hunks.** For each cluster, extract the few diff hunks that carry the idea – the isolated spans a reader needs, not the full diff. Trim hunks to the load-bearing lines plus minimal context. The full diff stays in git/the PR; the walkthrough is the tour, not the archive.
4. **Per-file risk.** Tag each file `attention` (touches a trust boundary, public contract, concurrency, money/data integrity, or dense conditional logic), `medium`, or `safe` (mechanical/generated/docs). Risk here means *where careful reading pays off* – it is not a defect claim.
5. **Architectural delta.** When the changeset adds, removes, or rewires module-to-module relationships, capture before→after at component level. Use the project's Architecture document (see **Project Document Index**) as the baseline when it exists; otherwise derive boundaries from the directory/package structure.
6. **Focus points.** 3–7 numbered places where reviewer attention pays off most, ordered by risk, each with a one-line *why* and a `path:line` anchor.
7. **Scope boundary.** What this changeset deliberately does *not* do (from intent context), plus pre-existing issues noticed but untouched.

**Gate**: every changed file appears in exactly one cluster row; the cluster set covers the whole diff (no silent omissions – if files were skipped as noise, say which and why).

### 3. Write the walkthrough artifact

Write to `.agent_temp/walkthrough/<slug>-walkthrough-<YYYY-MM-DD>.md` (repo root; `<slug>` = `pr-<N>` or the kebab-cased branch name). Read and follow [`walkthrough-template.md`](references/walkthrough-template.md) exactly.

### 4. Render

Unless `--no-visual`: invoke the `andthen:visualize` skill on the artifact path. It detects the `changeset-walkthrough` type and renders the interactive tour.

### 5. Report and publish

Print the artifact path and the HTML path. When `--to-pr [<N>]` is set, resolve `<N>` in order: explicit value → the `--from-pr` number → the current branch's open PR (`gh pr view --json number`); reject only when none resolves. Post the walkthrough markdown as a PR comment via `gh pr comment <N> --body-file <artifact-path>`. Split into multiple comments rather than truncate when the body exceeds GitHub's 65,536-char comment limit. Surface `gh` errors verbatim; never roll back local artifacts (the PR-side post is transport, the local file is the source of truth).


## GOTCHAS

- **Findings creep.** Spotting a probable bug while analyzing is natural – it still doesn't belong in the walkthrough as a finding. Phrase it as a focus point ("careful eyes here: the retry loop's exit condition") and recommend the `andthen:review` skill in the report. A walkthrough that issues verdicts trains readers to skip the review.
- **Cluster-by-directory.** Directories are not intents. A behavior change usually spans `src/` + `tests/` + config; splitting it by location re-tangles what Step 2 untangled. Tests that merely accompany a behavior change belong in that behavior cluster; a standalone test-improvement effort is its own `tests` cluster.
- **Inventing intent.** When no PR body/FIS/commit trail states the why, say "derived from code" rather than presenting inferred intent as stated fact.


## FOLLOW-UP ACTIONS

Skip when AUTO_MODE=true – print only the artifact and HTML paths.

1. **Share with reviewers** – `--to-pr` posts the walkthrough on the PR (best default: in-context, visible to every reviewer). The HTML file is fully self-contained – it can be shared over any channel, but it embeds source code: treat it with the repo's confidentiality.
2. **Review with context** – run the `andthen:review` skill (e.g. `--from-pr <N>`) for findings and a verdict; the walkthrough's focus points make good review scope hints.
3. **Capture notes** – section-anchored notes taken in the HTML view export via clipboard; paste them into the PR conversation or alongside the next skill invocation.
