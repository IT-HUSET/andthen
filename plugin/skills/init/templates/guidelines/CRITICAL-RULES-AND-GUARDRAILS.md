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
- **Commit only your own changes** – review the diff, stage by path (`git add <path>`, not `-A` / `-u`), never stage others' work.
- **Assume a shared worktree** – another agent may be mid-edit. `git reset`, `git restore` / `checkout --`, `git stash`, and `git clean` hit the whole tree and discard their uncommitted work unrecoverably; undo your own edits by editing back or reverting your own commit. Never delete a `.git/*.lock` – another process is mid-write. Run whole-tree destructive commands only when the active skill's contract or the user sanctions it.
- **Use `git mv`** for tracked moves/renames (preserves blame). Never `git rebase --skip` (data loss) – ask for help with conflicts.
- **Never overwrite `.env` files** without explicit confirmation.
- **Temp files** in `<project_root>/.agent_temp/`, named meaningfully, never the repo root.
- **Harness auto-memory is personal, not project storage** – user preferences and machine-local facts only; project-durable knowledge (traps, decisions, conventions) goes to committed docs (Learnings/Decisions/guidelines), visible to every agent and teammate.
- **Delegate to sub-agents** for retrieval, review, research, and deep exploration; route each per the **Sub-Agent Model Policy** below. Name each one with plain task words plus the model name – the agent list must read at a glance, never as codes ("S38r").

## Sub-Agent Model Policy

Delegated work inherits the session model *by default*; downshift when the task qualifies below. Classify the **task**, not the model – model names go stale, task properties don't. Two axes decide the tier: **specification** (scope, inputs, and outputs pinned down, with a checkable done-criterion?) and **judgment** (needs taste, trade-offs, creativity, or cross-cutting reasoning?).

This policy owns both model and effort for generic delegation; callers state task shape, not a competing effort. Dedicated installed agents keep their declared fixed effort as the explicit exception.

**Routing** (models: session = the root conversation model, and the ceiling: nothing routes above it · top = e.g. Opus 5 / GPT-5.6-Sol, never above session · cheap = e.g. Sonnet 5 / GPT-5.6-Luna):
- **High judgment** – orchestration, planning, architecture, design, reviews, security, creative or ambiguous work → session at xhigh. Never downshift.
- **Implementation and other medium/larger subtasks** – including fully-specced FIS/story execution (a complete spec doesn't shrink a sizeable story to the tier below) → top model at medium effort.
- **Small, well-specified, verifiable subtasks** – information retrieval, scans, mechanical edits, small clear-spec fixes, doc lookups → cheap model at medium for simple tasks, otherwise xhigh. Downshifting moves the burden to the prompt: exact scope, output contract, and done-criteria come from the orchestrator.

The named models are examples, not unconditional identifiers. Before overriding, verify the model is callable on this host and does not exceed the session ceiling; otherwise inherit the session model.

**Rules:**
- On a quality miss, escalate immediately – a tier up or an effort notch up; never a second unchanged attempt on what just failed.
