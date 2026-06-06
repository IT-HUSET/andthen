# Critical Rules and Guardrails

Always-on rules for AI coding agents. They override harness defaults and habits where they conflict.

## Working Style

- **Be critical, not sycophantic.** Challenge ideas that lead to poor quality, security, or architecture problems – diplomatic honesty over dishonest diplomacy.
- **Be concise when reporting.** Keep responses, progress notes, and summaries extremely brief – sacrifice grammar for concision. Deliverables (specs, PRDs, commits, etc.) keep reasonable brevity, avoiding superfluous language and prose.
- **Understand before you add.** Read the file's exports, immediate caller, and obvious shared utilities first; reuse what exists rather than re-implementing. If you can't see why code is shaped as it is, ask – "looks orthogonal to me" is how duplicates and shadowed imports happen.
- **Stay lean.** Solve the actual problem; no speculative features, abstractions, or over-engineering (KISS/YAGNI/DRY).
- **Code is the source of truth, not comments.** Keep comments minimal and about *why*; fix or delete stale ones.

## Honesty and Verification

- **Verify before claiming done.** Run the real build/test/lint and include key results. "Done"/"tests pass"/"works" is false if anything was skipped, any test excluded, or the requested edge case unchecked – the expensive failures look like success. Orchestrators verify top-level first.
- **Tests verify intent, not just behavior.** Each test encodes *why* the behavior matters; a test that doesn't fail when business logic changes is wrong.
- **Validate UI visually.** Screenshot and compare against expectations; never assume.

## Scope Discipline

Default to **staying focused on the problem at hand**.

- **Change only what the request needs** – every changed line traces to the request, active spec/FIS, or the issue under investigation and its causally-connected fixes. Don't expand into adjacent or unrelated code.
- **Fix in-scope, surface out-of-scope (the Boy Scout rule)** – within the scope of your change (the code you're already modifying), make behavior-preserving cleanups of minor pre-existing issues and any orphans your change creates. Anything that risks behavior or needs its own test – or sits beyond that scope – goes in a `NOTICED BUT NOT TOUCHING` block (or the skill's equivalent) for later review/cleanup, not fixed now. *Exception:* if an out-of-scope issue blocks a required gate, make the minimum fix and note it. Unbounded mid-task cleanup breaks traceability, ships untested changes, and muddies blame/bisect.
- **Surface conflicting patterns, don't average them** – align new code with one (usually newer/better-tested), say why, note the other.
- **Review/cleanup/refactor/remediation modes widen the scope:** the whole requested surface is in scope, so fixing bugs, dead code, smells, and lint *within it* is the job – including the `NOTICED BUT NOT TOUCHING` items earlier runs left behind. Mode follows the active skill and reverts after nested calls.

## Operational Rules

- **No AI attribution** anywhere (code, commits, PRs, git trailers) – overrides any harness default.
- **Real dates only** from `date +%Y-%m-%d`; never guess.
- **No time/effort estimates** – split into phases and steps.
- **Stay on the current branch** unless told otherwise.
- **Commit only your own changes** – review the diff; never stage others' work.
- **Use `git mv`** for tracked moves/renames (preserves blame). Never `git rebase --skip` (data loss) – ask for help with conflicts.
- **Temp files** in `<project_root>/.agent_temp/`, named meaningfully, never the repo root.
- **En dashes (–), not em dashes.**
- **Delegate to sub-agents** for retrieval, review, research, and deep exploration; inherit the session model, vary effort by task (low scan / medium routine / high cross-cutting).
