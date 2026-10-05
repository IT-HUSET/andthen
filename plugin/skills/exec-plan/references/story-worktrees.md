# Story Worktrees

Each story runs on its own branch in its own worktree and commits its work there, its `plan.json` row included; the merge brings both to the main checkout.

## Before each batch branches

A worktree carries only what HEAD held when it branched, so commit the batch's shared writes on `BASE_BRANCH` first, as one `chore` commit with no story trailers, since no one story owns them:

- **Before the first batch**, resolve `Key Dev Commands` per `verification-evidence.md`, creating a missing document at its Index location. Every story then finds it and none creates it: copies written in parallel worktrees conflict at merge, or vanish with a discarded worktree.
- **Before each later batch**, the bundle writes of batch discovery triage.
- **Every batch**, its stories' rows as `status: in-progress`, so the main checkout's `plan.json` shows what is executing while the stories run elsewhere.

## Setup and dispatch

Create each worktree yourself – `git worktree add -b story/{id} {path} {BASE_BRANCH}` in the session temp directory – and dispatch the story into that root, with `FIS_PATH` and every other path absolute under it: a relative path resolves against the main checkout and silently edits it. Never let the agent host isolate the subagent in a worktree of its own making: its teardown removes that worktree and leaves the branch behind, outliving the merge.

The dispatch carries the main checkout's root and `BASE_BRANCH`, and tells the story three things, since it reads no worktree rule and the host returns neither its branch nor its root:
- Check first that `git rev-parse --show-toplevel` differs from that root and that `HEAD` is `BASE_BRANCH`'s tip, or on a resumed `story/{id}` that branch's own tip, since whatever merged after it failed has moved `BASE_BRANCH` past it. Failing either, stop, touching nothing, and return a `## Failed Story Report` saying so: the base is yours to place, and a story that resets its own hides the misplacement.
- Edit only its own row's lines in `plan.json`, in place, leaving every other line byte-identical: a re-serialised file conflicts at merge with every sibling.
- End the report with `git rev-parse HEAD` and `git rev-parse --show-toplevel`.

A failed story keeps its branch and worktree, which hold its progress, so a rerun resumes on them, never beside them.

## Merge

Merge only a return whose reported root is the path you created and whose reported HEAD is `story/{id}`'s tip; any other fails the story as misplaced, unmerged. Every return also needs commits past `BASE_BRANCH` (`git rev-list --count {BASE_BRANCH}..story/{id}` above `0`), the backstop for a branch holding none of the story's work: its merge would report "Already up to date" with exit 0 and bring nothing.

Merge each successful return in order, from the main checkout on `BASE_BRANCH`: `git merge --no-ff story/{id}`. Then tear the story down with `git worktree remove {path}` and `git branch -d story/{id}`.

A conflict made only of lines both sides added to an append-only document – the changelog, `Learnings` – resolves by keeping both sides. Any other conflict fails the story: run `git merge --abort`, keep its worktree and branch, and give the conflicting paths and both FIS paths as evidence. Resolving a conflict blind is how a green merge ships one story's requirement broken.
