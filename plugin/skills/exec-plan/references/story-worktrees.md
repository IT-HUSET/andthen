# Story Worktrees

Read by the `andthen:exec-plan` skill under `--worktree`, before the first dispatch of Step 2.

## Setup and dispatch

Each story runs on its own branch in its own worktree and commits only code and its FIS appends there; `plan.json` stays the run session's, written in the main checkout after the merge.

The run session creates the worktree itself – `git worktree add -b story/{id} {path} {BASE_BRANCH}` in the session temp directory – and dispatches the story into that root, with `FIS_PATH` and every other path absolute under it: a relative path resolves against the main checkout and silently edits it. Never let the agent host isolate the subagent in a worktree of its own making instead: its teardown removes that worktree and leaves the branch behind it, outliving the merge in the branch list.

A failed story keeps its branch and worktree, and they hold its progress – the commits and the FIS observations the `andthen:exec-spec` skill resumes from – so a rerun continues on them rather than beside them: a worktree `git worktree list` still names is reused as it stands, and otherwise `git worktree prune` precedes `git worktree add {path} story/{id}` without `-b`, which collides on the existing branch. Either way `git merge {BASE_BRANCH}` runs there before the redispatch – siblings moved the base, and the guard below rejects a branch behind it – a conflict taking the Merge section's Stop-the-Line rule.

Every dispatch carries the main checkout's root and `BASE_BRANCH`. The story's first action checks that `git rev-parse --show-toplevel` differs from that root and that `HEAD` is `BASE_BRANCH`'s tip – on a resumed `story/{id}`, a descendant of it. Failing either, the story stops, touching nothing, and returns a `## Failed Story Report` saying so: the base is the run session's to place, and a story that resets its own hides the misplacement.

Every report ends with the story's branch and root (`git rev-parse --abbrev-ref HEAD`, `--show-toplevel`): the host returns neither.

## Merge

Merge each successful return in order, from the main checkout on `BASE_BRANCH`: `git merge --no-ff story/{id}`. Then write that story's row and commit it, and tear the story down – `git worktree remove {path}`, `git branch -d story/{id}`. Nothing but code and the FIS came over the branch, so there is nothing to reconcile.

A merge that reports a conflict is Stop-the-Line: `git merge --abort`, then the story fails with the conflicting paths and both FIS paths as evidence, worktree and branch preserved. The story's work stands; the merge is what is missing, and the report says so. Resolving one blind is how a green merge ships one story's requirement broken.

## Between batches

Commit the bundle writes of batch discovery triage before the next batch branches – one `chore` commit, no story trailers, since they span the batch. A worktree carries only what HEAD held when it branched.
