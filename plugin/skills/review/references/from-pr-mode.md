# `--from-pr` Mode

PR-as-input fetch mechanics for `andthen:review --from-pr <N>`. Load this reference when running the `andthen:review` skill with `--from-pr` set, or when implementing a new lens that needs to know how PR-mode scope discovery and full-fidelity opt-in work.

The flag swaps the implementation scope from local pending changes to the named PR – without modifying the working tree under the lightweight default. `--worktree` is the opt-in for full-fidelity local review.

Companion references:
- [`review-report-location.md`](${CLAUDE_PLUGIN_ROOT}/references/review-report-location.md) – PR-mode does not change report-location resolution; the report still lands per the standard tier resolution.


## Lightweight default fetch

When `--from-pr <N>` is set, the implementation scope is the named PR, not local pending changes. Reject up-front when a local target/path was also supplied (`--from-pr` is the scope; do not mix). Fetch via `gh`:

- **Metadata**: `gh pr view <N> --json number,title,baseRefName,headRefName,headRefOid,files,body` – provides the changed-files list at PR HEAD plus the PR body (use as user intent / requirements context).
- **Change diff**: `gh pr diff <N>` – unified diff for change-scope identification; do **not** apply or check out.
- **File blobs at PR HEAD** (on demand, when a lens needs full-file content): `gh api repos/:owner/:repo/contents/<path>?ref=<headRefOid>` and base64-decode the `content` field.

`git status` after the run must show the same state as before. Surface `gh` failures verbatim and stop (`BLOCKED: gh authentication required` / `BLOCKED: PR <N> not found` in `AUTO_MODE`).


## `--worktree` opt-in (full-fidelity)

When `--worktree` is also set, isolate the PR HEAD in a temp worktree so the user's main working tree stays untouched. `gh pr checkout <N>` alone checks out into the *current* working tree – that violates the lightweight-default guarantee. Use this sequence instead:

1. `git worktree add <temp-path> <baseRefName>` – e.g. `.agent_temp/review-pr-<N>-worktree/`. The branch hint can be the PR base; `gh pr checkout` swaps to the PR head inside the worktree.
2. `cd <temp-path> && gh pr checkout <N>` – checks out the PR head inside the isolated worktree only.
3. Run lens analysis from `<temp-path>` (project analyzers, build, tests against PR HEAD).
4. On exit (success or failure): `git worktree remove <temp-path> --force` to clean up.

Use only when a lens genuinely needs project analyzers / build state at PR HEAD – see the trigger conditions below. The team-mode worktree pattern in `plugin/skills/exec-plan/references/team-mode-orchestration.md` covers parallel multi-worktree orchestration; this skill needs only one worktree per invocation.


## Lightweight-insufficient detection (lens trigger for HIGH "needs `--worktree`")

These triggers apply only when `--worktree` is **not** set. When `--worktree` is already in effect, the lens has full-fidelity access and these warnings are unnecessary – suppress the finding.

A lens running under lightweight `--from-pr` should emit a HIGH finding when any of the following hold – it cannot do its job from diff + on-demand blobs alone:

- **Diff exceeds context budget**: `gh pr diff <N>` output is larger than the lens can reason about in one pass (rough threshold: >2000 changed lines or >200 changed files). Partial-diff analysis silently misses defects in unread regions.
- **Project analyzers required**: the lens depends on running typecheck/build/lint/test against PR HEAD (e.g. code lens checking type-safety of a refactor, security lens running Semgrep, gap lens executing tests for proof-of-work). `gh api .../contents` returns file content, not analyzer state.
- **Cross-file refactor scope**: the diff crosses module boundaries in ways that need full-tree analysis (call graph, dead-code detection, dependency cycles). Reasoning from diff hunks alone produces false negatives on cross-reference defects.

The HIGH finding text follows the calibration: `"deep code lens needs project analyzers – re-run with --worktree"` (substitute lens name as appropriate). The lens emits the finding and proceeds with whatever lightweight analysis is still meaningful – it does **not** auto-broaden to worktree without the user's flag. Auto-promotion would mutate the working tree without consent (see SKILL.md GOTCHAS).
