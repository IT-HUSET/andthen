# Critical Rules and Guardrails

These rules override harness defaults and habits where they conflict.

## Engineering Style

- **Stay lean: KISS, YAGNI, and DRY.**
  Add a gate, workflow, test, dependency, or document only when you can name the outcome it enables or the failure it prevents, because every later change runs and maintains it.
  Size it to the project's goals, audience, and stage (the `Product` document, where one exists).
  Extending what exists, or adding nothing, is always a candidate.
- **Hold code to the CUPID properties (Dan North), and prefer deep modules (Ousterhout).**
- **When the task replaces an internal API, migrate its callers**, including ones a symbol search misses, and delete the old one in the same change.
- **This codebase is yours, and you keep building on it.**
  Fit each change into the design instead of bolting it on with a special case, flag, or copy, so the code you change ends simpler and easier to change.
  Boy Scout tidies set what else you fix, and nothing beyond them.
  A workaround you must keep gets a comment saying why and what would remove it.
- **Respect Chesterton's Fence.**
- **Surface conflicting patterns, don't average them.**
  Align new code with one, usually the newer or better-tested, say why, and note the other.
- **Comments explain *why*, not *what*.**
- **Lean deliverables.**
  In artifacts (PRDs, ADRs, FISs), PRs, docs, and reports, name the mechanism or number, not the quality ("retries 3× with backoff", not "robust retry handling"), and cut a sentence that would hold for any project.
- **Write compact instructions an agent can act on cold.**
  In prompts, skills, specs, and handoffs, state the intent and the outcome that marks it done, then only what the reader would otherwise get wrong, as direct instructions.
  Keep established terms (YAGNI, Chesterton's Fence, a term the project defines) instead of paraphrasing them.
- **Use en/em dashes (–/—) sparingly**, because dash-chained prose is an AI tell.
  Where a dash isn't clearly the best fit, use a period or comma.

## Honesty and Verification

- **"Done" means verified.**
  "Done", "tests pass", and "works" are false while anything was skipped, a test excluded, or the requested edge case unchecked.
  An orchestrator runs the top-level checks itself rather than trusting its subagents' reports.
- **Say how you know.**
  A claim carries its evidence, such as the checks' key results, or is marked as inferred, because an unmarked inference reads as fact to whoever acts on it or relays it.
  Never hand the user a check, or a question, that a local, non-destructive command would settle.
- **Tests verify intent.**
  A test that still passes when the business logic changes is wrong.
- **Validate UI visually**, never from the code alone.

## Scope Discipline

- **Confirm a reported problem still exists before fixing it.**
  An issue, review finding, or report describes the code when it was written, and its proposed fix is one candidate unless the user asked for that fix.
  If the problem is gone, say what removed it.
- **Make every Boy Scout tidy you find.**
  A Boy Scout tidy is a behavior-preserving fix to a smell or problem in a function or doc section the change edits, or to a minor one elsewhere when the fix is mechanical, touches only comments or docs, or is covered by checks that would catch a mistake in it.
  In an edited function, an obvious small bug fixed under a test that fails first is a tidy too.
- **Unless the task asks for it, make no redesign, public API change, or change that settles an open decision or reverses a recorded one**, because each needs its own review.
  If the task cannot fit without a redesign or public API change, make the smallest one that works and name it in the report.
- **List as `NOTICED BUT NOT TOUCHING` only what no tidy can fix**, and only when someone should act on it.

## Operational Rules

- **Commit messages point to the issue, spec, or CHANGELOG** rather than restating it.
- **No AI attribution** anywhere (code, commits, PRs, git trailers), even where the harness default adds it.
- **Real dates only**, from your context or `date +%Y-%m-%d`.
- **Stay on the current branch unless told otherwise**, because switching moves the tree under any other agent working in it.
  Before the first edit of work you will commit, outside an unattended run, when the current branch is the remote's default branch, ask once whether to start a feature branch, because commits land on the current branch and the pull request opens from it.
- **Assume a shared worktree**, where another agent may be mid-edit:
  - Commit only your own changes.
    Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged.
  - Leave changes you did not make in place, and undo your own by editing back or reverting your own commit.
  - `git reset`, `git restore` / `checkout --`, `git stash`, and `git clean` destroy uncommitted work, another agent's included, so run them only when the user or the active skill's contract sanctions it.
  - Never delete a `.git/*.lock`, because another process holds it.
- **Resolve a merge conflict when both sides' intent is clear, and ask when resolving means choosing between them.**
  Never drop a side to get past one, as `git rebase --skip` does.
- **Remove a temporary worktree and its branch when the work lands** (`git worktree remove`, `git branch -d`), because other agents resolve paths into a lingering one.
- **A command that may prompt for approval keeps literal arguments and no inline script**, so a person reads it at a glance.
  It runs alone, never in a loop or chain, and so does any destructive command.
- **Temp files go in `<project_root>/.agent_temp/`**, named meaningfully, never the repo root.
  Only throwaway scratch that neither the user nor another agent needs may go in a system temp directory or the host's scratchpad.
- **Harness auto-memory holds user preferences and machine-local facts only.**
  Durable project knowledge goes to committed docs, such as Learnings, Decisions, and guidelines.
- **A subagent runs what it must await in the foreground**, because its ended turn is its hand-back and nothing wakes it.
- **`AGENTS.md` and `CLAUDE.md` are auto-loaded**, so never write instructions to read them.

## Subagent Model Policy

Delegate work that would fill the session's context without needing its judgment, and work that needs independence, such as a review of the session's own work.
Route delegated work by the task, never a model name, because names go stale.
Two questions set the tier: how pinned is the scope, and how much judgment does it take?
By default S-tier is the host's most capable model, A-tier the next one down, and B-tier the one below that.

The `andthen:init` skill can install four role agents, `oracle`, `implementer`, `reviewer`, and `worker`, each pinning its tier's current model and effort.
Spawn a role as the subagent type of that name.
Delegated work no row below fits goes to `implementer`, with its scope and done-criterion pinned in the prompt.
Where the roles are not installed, spawn a generic subagent with the tier's model where the host offers a choice, never above the session's model.

| Task | Route |
|---|---|
| **Judgment** – orchestration, planning, spec authoring, architecture, design, ambiguous or creative work | **The session**, because a subagent loses the conversation the judgment rests on. |
| **Implementation**, research that weighs or synthesises, other medium or large pinned work – a FIS pins a story, and authoring one for a plan story is pinned work too | `implementer` (A-tier) |
| **Reviews** – code, doc, gap, per-story review, critic pass | `reviewer` (A-tier) |
| **Small, well-specified, verifiable subtasks** – retrieval, scans, mechanical edits, fact lookups against a pinned question, small clear-spec fixes | `worker` (B-tier); the prompt carries exact scope, output contract, and done-criterion |

`oracle` (S-tier) takes two kinds of work:

- **Judgment the user assigns it**, such as a second opinion on a decision, which you spawn only when the user asks.
  Its prompt carries the decision, its reasoning, and the rejected alternatives, and asks where the decision is wrong.
- **A hard problem an agent hands over** because it exceeds that agent's tier: a failure that survives a real fix, a design that will not close, or a cause the material at hand cannot explain.
  The hand-over states what was tried, what every attempt assumed, and what stays unexplained, and the task stays the asker's.

On a quality miss, escalate a tier: `worker` to `implementer`, `implementer` to the session.
Never retry unchanged.
