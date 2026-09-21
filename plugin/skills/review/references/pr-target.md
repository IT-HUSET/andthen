# PR Target

Resolution and execution policy for a pull-request target, in place of the local-tree scope Step 1 otherwise builds.


## Resolve

A PR URL resolves its `owner/name` and number; bare `PR <n>` resolves the canonical current repository once, and that `PR_REPO` holds for every read. A bare `#<n>` is ambiguous (issue or PR) and is never auto-resolved.

Then `gh pr view <n> --repo <PR_REPO> --json title,body,baseRefOid,headRefOid,isCrossRepository` – title and body are Intent Context, the two OIDs pin what was reviewed – `git fetch <remote of PR_REPO> refs/pull/<n>/head <baseRefOid>`, and a detached worktree at the head OID under the host's worktree directory (Claude Code: `.claude/worktrees/`), else the session temp directory: `git -c core.hooksPath=/dev/null worktree add --detach <dir>/pr-<n> <headRefOid>` with `GIT_LFS_SKIP_SMUDGE=1`, because the launch checkout's own hooks and filters would otherwise run against the PR's files.

The implementation scope is that tree against `git merge-base <baseRefOid> <headRefOid>` – the base resolves from the OID the host reports, never a local branch name, which is stale or absent as often as not – and the report cites both SHAs. Project Rules Context stays the launch checkout's: a PR does not rewrite the rules it is judged by. Remove the worktree (`git worktree remove --force`) on completion.

Surface `gh` and `git` failures verbatim (`BLOCKED: gh authentication required` / `BLOCKED: PR <n> not found` in `AUTO_MODE`).


## Execute

The fetched tree is reviewed as a local tree with every lens. The project's checks and scanners run on it when the head branch lives in `PR_REPO` itself – pushing it there took the write access every branch the framework tests already has; a fork PR (`isCrossRepository`) gets a static pass with the checks reported unavailable, and only the user's explicit word lifts that, the same authorization shape as `--fix`.

Do not switch the session into the worktree – reads and checks take absolute paths under that root, because a check run in the launch checkout proves the base and reports green. A spawned pass carries this rule.
