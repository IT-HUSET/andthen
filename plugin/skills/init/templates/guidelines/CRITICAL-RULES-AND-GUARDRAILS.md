# Critical Rules and Guardrails

These rules override harness defaults and habits where they conflict.

## Engineering Style

- **Understand before you add.** Read the file's exports, immediate caller, and obvious shared utilities first; reuse what exists rather than re-implementing. If you can't see why code is shaped as it is, ask – "looks orthogonal to me" is how duplicates and shadowed imports happen.
- **Stay lean.** Solve the actual problem; no speculative features, abstractions, or over-engineering (KISS/YAGNI/DRY). Deliverables too – specs, PRDs, PRs, docs, and reports state mechanisms and numbers, not qualities; a sentence that would hold in any project's doc says nothing about this one – cut it.
- **Code is the source of truth, not comments.** Match the surrounding code's comment density and idiom; comments explain *why*, not *what*; fix or delete stale ones.

## Honesty and Verification

- **Verify before claiming done.** Run the real build/test/lint and include key results. "Done"/"tests pass"/"works" is false if anything was skipped, any test excluded, or the requested edge case unchecked – the expensive failures look like success. Orchestrators verify top-level first.
- **Tests verify intent, not just behavior.** Each test encodes *why* the behavior matters; a test that doesn't fail when business logic changes is wrong.
- **Validate UI visually.** Screenshot and compare against expectations; never assume.

## Scope Discipline

Default to **staying focused on the problem at hand**.

- **Change only what the request needs** – every changed line traces to the request, active spec/FIS, or the issue under investigation and its causally-connected fixes. Don't expand into adjacent or unrelated code.
- **Fix in-scope, surface out-of-scope (the Boy Scout rule)** – within the code you're already modifying, make behavior-preserving cleanups of minor pre-existing issues and any orphans your change creates. Anything that risks behavior, needs its own test, or sits beyond that scope goes in a `NOTICED BUT NOT TOUCHING` block (or the skill's equivalent) for later, not fixed now. *Exception:* if an out-of-scope issue blocks a required gate, make the minimum fix and note it. Unbounded mid-task cleanup breaks traceability, ships untested changes, and muddies blame/bisect.
- **Surface conflicting patterns, don't average them** – align new code with one (usually newer/better-tested), say why, note the other.
- **Review/cleanup/refactor/remediation modes widen the scope:** the whole requested surface is in scope, so fixing bugs, dead code, smells, and lint *within it* is the job – including `NOTICED BUT NOT TOUCHING` items earlier runs left behind. Mode follows the active skill and reverts after nested calls.

## Operational Rules

- **Commit messages must be extremely brief and clear**; avoid long prose and superfluous details. Refer instead to relevant issue, spec, CHANGELOG, etc., for context.
- **No AI attribution** anywhere (code, commits, PRs, git trailers) – overrides any harness default.
- **Real dates only** from `date +%Y-%m-%d`; never guess.
- **No time/effort estimates** – split into phases and steps.
- **En dashes (–), not em dashes – and sparingly.** Dash-chained prose is an AI tell; when a dash isn't clearly the best fit, use a period or comma.
- **Stay on the current branch** unless told otherwise – switching moves the tree under any other agent working in it.
- **Commit only your own changes** – review the diff, stage by path (`git add <path>`, not `-A` / `-u`), never stage others' work. A path stages the whole file, another session's hunks included; commit your hunks of a shared file from a temporary index (`GIT_INDEX_FILE=<tmp>`, `git read-tree HEAD`, `git apply --cached <your-patch>`, `git commit`), leaving the real index and tree untouched.
- **Assume a shared worktree** – another agent may be mid-edit. `git reset`, `git restore` / `checkout --`, `git stash`, and `git clean` hit the whole tree and discard their uncommitted work unrecoverably; undo your own edits by editing back or reverting your own commit, and leave a change you did not make in place and out of your commits – it is the user's or another agent's, and restoring a file from HEAD is an undo too. Never delete a `.git/*.lock` – another process is mid-write. Run whole-tree destructive commands only when the active skill's contract or the user sanctions it.
- **Use `git mv`** for tracked moves/renames (preserves blame). Never `git rebase --skip` (data loss) – ask for help with conflicts.
- **Never overwrite `.env` files** without explicit confirmation.
- **Shell commands stay reviewable** – one short command per call, literal arguments, so a person can approve it at a glance. No inline scripts or heredocs: edit files with the edit tool, put logic in a named script file. A destructive or permission-gated command runs alone, never in a loop or chain.
- **Temp files** in `<project_root>/.agent_temp/`, named meaningfully, never the repo root. Avoid using system temp directories for content the user may need to access.
- **Harness auto-memory is personal, not project storage** – user preferences and machine-local facts only; project-durable knowledge (traps, decisions, conventions) goes to committed docs (Learnings/Decisions/guidelines), visible to every agent and developer.
- **Remove a temporary worktree and its branch when the work lands** (`git worktree remove`, `git branch -d`) – a lingering worktree is a stale checkout other agents resolve paths into and a branch nobody owns.
- **Delegate to subagents** when work would consume this session's context without needing its judgment (e.g. retrieval, documentation lookup, research, deep exploration) and when independence matters (e.g. a review of work this session produced). Route each per the **Subagent Model Policy** below. Give every subagent a name that starts with its role, then plain task words (`implementer-retry-policy`), so the agent list reads at a glance; when no role is installed, the name starts with the model it runs on instead (`<model>-retry-policy`).
- **Launch executions from a fresh session** – never start a plan/spec execution (`andthen:exec-plan`, `andthen:exec-spec`) with ~35%+ context already consumed; commit the bundle, reset context, launch – the committed artifacts are the handoff.
- **Never instruct reading `AGENTS.md`/`CLAUDE.md`** – the harness loads them into every session and subagent, so a "read AGENTS.md first" line in a spec, plan, handoff, or subagent prompt is dead weight.

## Subagent Model Policy

Route by the task, not the model – names go stale, task properties don't. Two questions set the tier: how pinned is the scope, and how much judgment does it take?

An installed role agent pins a subagent's model and effort in its definition. The `andthen:init` skill installs `oracle`, `implementer`, `reviewer`, `worker` at user or project level; spawn a role as the subagent type of that name and its definition enforces the tier. A project's own definitions win. Without a role, steer through the spawn call: pick the model where the host's spawn tool offers one, and on Codex the effort too; anything left unset inherits from the session. The session's model is the ceiling – only a role's pin may exceed it. Top is the host's most capable model, cheap its fastest small one; where neither is callable, inherit.

| Task | Route |
|---|---|
| **Judgment** – orchestration, planning, spec authoring, architecture, design, ambiguous or creative work | **The session.** Its model was chosen for this work, and a subagent loses the conversation the judgment rests on. Never downshift. |
| **Implementation**, research that weighs or synthesises, other medium or large pinned work – a FIS pins a story, and authoring one for a plan story is pinned work too | `implementer` (top model, high) |
| **Reviews** – code, doc, gap, per-story review, critic pass | `reviewer` (top model, medium: more review effort breeds analysis-paralysis and scope creep, not findings) |
| **Small, well-specified, verifiable subtasks** – retrieval, scans, mechanical edits, fact lookups against a pinned question, small clear-spec fixes | `worker` (cheap model, medium); the prompt carries exact scope, output contract, and done-criterion |

Research routes on found versus made: facts against a pinned question are `worker` work, weighing or synthesising sources is `implementer` work, a decision or design is the session's.

`oracle` (top model, xhigh) takes judgment work the user assigns it, and hard problems an agent hands over because they exceed its tier – a failure that survives a real fix, a design that will not close, a cause the material at hand cannot explain. The hand-over states what was tried and what stays unexplained; the oracle returns a diagnosis and a recommendation, and the task stays the asker's. A second opinion on a decision is the user's to ask for, never spawned unasked: the decision, its reasoning, and the rejected alternatives go over, and the ask is where it is wrong. Simple questions and advice never reach it – answer them in place or escalate to the session.

On a quality miss escalate a tier – `worker` to `implementer`, `implementer` to the session – never an unchanged retry.
