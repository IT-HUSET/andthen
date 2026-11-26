# Critical Rules and Guardrails

These rules override harness defaults and habits where they conflict.

## Engineering Style

- **Stay lean: KISS, YAGNI, and pragmatic DRY.**
  Add a gate, workflow, test, dependency, or document only when you can name the outcome it enables or the failure it prevents, because every later change runs and maintains it.
  Size it to the project's goals, audience, and stage (the `Product` document, where one exists).
  Extending what exists, or adding nothing, is always a candidate.
- **Hold code to the CUPID properties (Dan North), and prefer deep modules (Ousterhout).**
- **When the task replaces an internal API, migrate its callers**, including ones a symbol search misses, and delete the old one in the same change.
- **This codebase is yours, and you keep building on it.**
  Fit each change into the design rather than bolting on a special case, flag, or copy, so the code you change ends simpler.
  Boy Scout tidies set what else you fix, and nothing beyond them.
  A workaround you must keep gets a comment saying why and what would remove it.
- **Respect Chesterton's Fence.**
- **Surface conflicting patterns, don't average them**: align new code with one, usually the newer or better-tested, say why, and note the other.
- **Comment only what the code cannot say**: a reason, a constraint or trap, or a contract the signature leaves open, never what a reader could write from the adjacent code alone.
- **Lean deliverables**: in artifacts, PRs, docs, and reports, name the mechanism or number, not the quality ("retries 3× with backoff", not "robust retry handling"), and cut a sentence that would hold for any project.
- **Write compact instructions an agent can act on cold**: in prompts, skills, specs, and handoffs, state the intent and the outcome that marks it done, then only what the reader would otherwise get wrong, as direct instructions.
  Keep established terms (YAGNI, a term the project defines) rather than paraphrasing them.

## Honesty and Verification

- **"Done" means verified**: "done", "tests pass", and "works" are false while anything was skipped, a test excluded, or the requested edge case unchecked.
  An orchestrator runs the top-level checks itself rather than trusting its subagents' reports.
- **Say how you know**: a claim carries its evidence, such as the checks' key results, or is marked inferred, because an unmarked inference reads as fact.
  Never hand the user a check or question that a local, non-destructive command would settle.
- **Tests verify intent**: a test that still passes when the business logic changes is wrong.
- **Get past a failing check only by fixing its cause**, never with `--no-verify` or a skipped, weakened, or deleted test, unless the user or the active skill's contract sanctions it.
- **Validate UI visually**, never from the code alone.

## Scope Discipline

- **Confirm a reported problem still exists before fixing it**: an issue, review finding, or report describes the code as it was, and its proposed fix is one candidate unless the user asked for that fix.
  If the problem is gone, say what removed it.
- **Make every Boy Scout tidy you find.**
  A Boy Scout tidy is a behavior-preserving fix to a smell or problem in a function or doc section the change edits, or to a minor one elsewhere when the fix is mechanical, touches only comments or docs, or is covered by checks that would catch a mistake in it.
  In an edited function, an obvious small bug fixed under a test that fails first is a tidy too.
  The minimum fix to an issue elsewhere that blocks a required check is also a tidy.
- **Unless the task asks for it, make no redesign, public API change, or change that settles an open decision or reverses a recorded one**, because each needs its own review.
  If the task needs a redesign or public API change, make the smallest that works and name it in the report.
- **List as `NOTICED BUT NOT TOUCHING` only what no tidy can fix**, and only when someone should act on it.

## Operational Rules

- **Commit messages point to the issue, spec, or CHANGELOG** rather than restating it.
- **No AI attribution** anywhere (code, commits, PRs, git trailers), even where the harness default adds it.
- **Stay on the current branch unless told otherwise**, because switching moves the tree under any other agent in it.
  On the remote's default branch, ask once before the first edit of work you will commit whether to start a feature branch, unless the run is unattended.
- **Assume another agent shares the worktree**, so act only on your own changes:
  - Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged.
    A path commit takes each file whole from disk, so to commit a file that also holds another session's edits, `git apply --cached` a patch of only your hunks, confirm `git diff --cached` shows nothing else, and commit without paths.
  - Undo your own work by editing back or reverting your commit.
  - Run `git reset`, `restore`, `checkout --`, `stash`, or `clean` only when the user or the active skill's contract sanctions it, because they destroy uncommitted work, another agent's included.
  - Never delete a `.git/*.lock`, because another process holds it.
- **Resolve a merge conflict when both sides' intent is clear, and ask when resolving means choosing between them**, never dropping a side to get past it, as `git rebase --skip` does.
- **Remove a temporary worktree and its branch when the work lands** (`git worktree remove`, `git branch -d`), because other agents resolve paths into a lingering one.
- **A command that may prompt for approval, or any destructive command, runs alone, never in a loop or chain**, and one that may prompt keeps literal arguments and no inline script, so a person reads it at a glance.
- **Temp files go in `<project_root>/.agent_temp/`**, named meaningfully, never the repo root.
  Only throwaway scratch no one else needs may go in a system temp directory or the host's scratchpad.
  When done, delete your throwaway scratch in `.agent_temp/`, keeping reports, handoffs, and evidence a document cites.
- **Harness auto-memory holds user preferences and machine-local facts only**; durable project knowledge goes to committed docs, such as Learnings, Decisions, and guidelines.
- **A subagent runs what it must await in the foreground**, because its ended turn is its hand-back and nothing wakes it.
- **`AGENTS.md` and `CLAUDE.md` are auto-loaded**, so never write instructions to read them.
- **A skill the user runs without arguments asks first**, in a choice question, for any required input, mode, and main flags, recommending the defaults, unless the skill has its own opening question.
- **A skill the user runs on a spec, plan, report, or issue starts fresh**: in a session that already did other work, it first offers a choice to restart in a new one, unless the run is unattended.
- **A skill's closing `Next (fresh session):` line is binding**: never run it here, skip it, or swap it for your own question unless the user says so.
  Where the host can start a new session, offer a closing `Next` line as a choice that starts it there, unless the run is unattended.

## Subagent Model Policy

Delegate work that would fill the session's context without needing its judgment, and work that needs independence, such as a review of the session's own work.
Route by the task, never a model name, because names go stale.

| Task | Route |
|---|---|
| **Judgment** – orchestration, planning, spec authoring, architecture, design, ambiguous or creative work | **The session**, because a subagent loses the conversation the judgment rests on |
| **Medium or large pinned work** – implementation, research that weighs or synthesises, authoring a plan story's FIS | `implementer` |
| **Any review** | `reviewer` |
| **A small, well-specified, verifiable subtask** | `worker` |
| **Judgment the user asks you to delegate**, such as a second opinion, or work at a skill's gate that names `oracle` | `oracle` |
| **A hard problem beyond your tier** – a failure that survives a real fix, a design that will not close, a cause the material at hand cannot explain | `oracle` |
| **Other delegated work** | `implementer` |

- Spawn a role as the subagent type of that name, or as a generic subagent on the session's model where it is not installed.
- Pin the scope, output contract, and done-criterion in every subagent's prompt.
- A second opinion's prompt carries the decision, its reasoning, and the rejected alternatives, and asks where the decision is wrong.
- A hand-over to `oracle` states what was tried, what every attempt assumed, and what stays unexplained, and the task stays yours.
- Label each subagent role first, or model family first where no role is installed, then the task in plain words (`Reviewer: audit prompt diff`), in the field the host lists it by (Claude Code's `description`).
- On Claude Code leave the Agent tool's `name` unset, because a named spawn can run as a teammate whose report never returns.
- On a quality miss, escalate one step, `worker` to `implementer` and `implementer` to the session, never retrying unchanged.
