# Critical Rules and Guardrails

These rules override harness defaults and habits where they conflict.

## Engineering Style

- **Understand before you add.** Read the file's exports, immediate caller, and obvious shared utilities first, and reuse what exists. Respect Chesterton's Fence: ask before reshaping code whose reason you cannot find. "Looks orthogonal to me" is how duplicates and shadowed imports happen.
- **Stay lean.** Solve the actual problem, with no speculative features, abstractions, or over-engineering (KISS/YAGNI/DRY). Deliverables too: specs, PRDs, PRs, docs, and reports state mechanisms and numbers, not qualities. Cut a sentence that would hold in any project's doc, because it says nothing about this one.
- **Code is the source of truth, not comments.** Comments explain *why*, not *what*. Fix or delete stale ones.

## Honesty and Verification

- **Verify before claiming done.** Run the real build/test/lint and include key results. "Done"/"tests pass"/"works" is false if anything was skipped, any test excluded, or the requested edge case unchecked. The expensive failures look like success. An orchestrator runs the top-level checks itself rather than trusting its subagents' reports.
- **Tests verify intent, not just behavior.** Each test encodes *why* the behavior matters. A test that doesn't fail when business logic changes is wrong.
- **Validate UI visually.** Screenshot and compare against expectations. Never assume.

## Scope Discipline

- **Change what the task needs, plus Boy Scout tidies in the files you touch.** Every changed line traces to the request, the active spec/FIS, the issue under investigation and its causal fixes, or a tidy: small and behavior-preserving, or an obvious small bug fixed under a test that fails first. Tidy rather than leave a note, because a smell left in a changed file comes back as a review finding and costs a fix round. Name each tidy in the report.
- **A redesign, a public API change, or a change that settles an open decision or reverses a recorded one is never a tidy**, because each needs its own review. Report it, like any issue outside the files the change touches, as `NOTICED BUT NOT TOUCHING` only when someone should act on it. An issue elsewhere that blocks a required gate gets the minimum fix, named in the report.
- **Surface conflicting patterns, don't average them.** Align new code with one (usually newer/better-tested), say why, and note the other.
- **Review, cleanup, refactor, and remediation tasks own their whole requested surface**, so fixing bugs, dead code, smells, and lint within it is the job, including what earlier runs reported but left.

## Operational Rules

- **Commit messages are extremely brief and clear.** Point to the relevant issue, spec, or CHANGELOG for context in place of long prose and superfluous detail.
- **No AI attribution** anywhere (code, commits, PRs, git trailers) – overrides any harness default.
- **Real dates only**, from your context or `date +%Y-%m-%d`; never guess.
- **No time/effort estimates** – split into phases and steps.
- **En dashes (–), not em dashes, and sparingly.** Dash-chained prose is an AI tell. Where a dash isn't clearly the best fit, use a period or comma.
- **Stay on the current branch** unless told otherwise – switching moves the tree under any other agent working in it.
- **Commit only your own changes.** Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged.
- **Assume a shared worktree**, where another agent may be mid-edit. Leave changes you did not make in place, and undo your own by editing back or reverting your own commit. `git reset`, `git restore` / `checkout --`, `git stash`, and `git clean` remove uncommitted work, another agent's included, so run them only when the user or the active skill's contract sanctions it. Never delete a `.git/*.lock`, because another process is mid-write.
- **Resolve a merge conflict when both sides' intent is clear, and ask when resolving means choosing between them.** Never drop a side to get past one, as `git rebase --skip` does.
- **Never overwrite `.env` files** without explicit confirmation.
- **A command that may prompt for approval keeps literal arguments and no inline script**, so a person reads it at a glance. A destructive or permission-gated command runs alone, never in a loop or chain.
- **Temp files** in `<project_root>/.agent_temp/`, named meaningfully, never the repo root. Avoid using system temp directories for content the user may need to access.
- **Harness auto-memory is personal, not project storage.** It holds user preferences and machine-local facts only. Project-durable knowledge (traps, decisions, conventions) goes to committed docs (Learnings, Decisions, guidelines), visible to every agent and developer.
- **Remove a temporary worktree and its branch when the work lands** (`git worktree remove`, `git branch -d`) – a lingering worktree is a stale checkout other agents resolve paths into and a branch nobody owns.
- **Delegate to subagents** when work would consume this session's context without needing its judgment (e.g. retrieval, documentation lookup, research, deep exploration) and when independence matters (e.g. a review of work this session produced). Route each per the **Subagent Model Policy** below. Give every subagent a name that starts with its role, then plain task words (`implementer-retry-policy`), so the agent list reads at a glance. When no role is installed, the name starts with the model it runs on instead (`<model>-retry-policy`).
- **Never instruct reading `AGENTS.md`/`CLAUDE.md`.** The harness loads them into every session and subagent, so a "read AGENTS.md first" line in a spec, plan, handoff, or subagent prompt is dead weight.

## Subagent Model Policy

Route by the task, not the model: model names go stale, task properties don't. Two questions set the tier: how pinned is the scope, and how much judgment does it take? A tier is a capability class, not a fixed model. By default S-tier is the host's most capable model, A-tier the next one down, B-tier the one below that; the installed roles carry the current recommendation, which shifts as lineups change and can put two tiers on one model at different efforts. Where a tier is not callable, inherit.

An installed role agent pins a subagent's model and effort in its definition. The `andthen:init` skill installs `oracle`, `implementer`, `reviewer`, and `worker` at user or project level. Spawn a role as the subagent type of that name, and its definition enforces the tier. A project's own definitions win.

Without a role, steer through the spawn call. Pick the model where the host's spawn tool offers one. Anything left unset inherits from the session. The session's model is the ceiling, and only a role's pin may exceed it.

| Task | Route |
|---|---|
| **Judgment** – orchestration, planning, spec authoring, architecture, design, ambiguous or creative work | **The session.** Its model was chosen for this work, and a subagent loses the conversation the judgment rests on. Never downshift. |
| **Implementation**, research that weighs or synthesises, other medium or large pinned work – a FIS pins a story, and authoring one for a plan story is pinned work too | `implementer` (A-tier) |
| **Reviews** – code, doc, gap, per-story review, critic pass | `reviewer` (A-tier) |
| **Small, well-specified, verifiable subtasks** – retrieval, scans, mechanical edits, fact lookups against a pinned question, small clear-spec fixes | `worker` (B-tier); the prompt carries exact scope, output contract, and done-criterion |

`oracle` (S-tier) takes two kinds of work: judgment work the user assigns it, and hard problems an agent hands over because they exceed its tier. Such a problem is a failure that survives a real fix, a design that will not close, or a cause the material at hand cannot explain. The hand-over states what was tried and what stays unexplained. The oracle returns a diagnosis and a recommendation, and the task stays the asker's. A second opinion on a decision is the user's to ask for, never spawned unasked. The decision, its reasoning, and the rejected alternatives go over, and the question is where it is wrong. Simple questions and advice never reach it. Answer them in place or escalate to the session.

On a quality miss, escalate a tier: `worker` to `implementer`, `implementer` to the session. Never retry unchanged.
