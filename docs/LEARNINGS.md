# Project Learnings

<!-- Traps only, one bullet each: `- **<title>** – <trap + fix>`. Admit a trap only if a frontier
     model doesn't know it, the code and git history don't carry it, and it outlives the current
     initiative; an initiative-only trap goes in that initiative's PRD, plan, or FIS. Before
     appending, check for a reworded duplicate. Delete an entry once a check encodes it. -->

## Agent Workflows

- **Read-only subagents still edit source** – after a read-only fan-out, expect changes only under `.agent_temp/`; diff the tree and confirm provenance before restoring anything.
- **Claude Code's `isolation: "worktree"` is unreliable** – ignored for team agents; for subagents it branches from the default branch (0.x `main` here), returns no path or branch, and blocks `git reset --hard`. Create worktrees yourself from the current branch, and enter one with `EnterWorktree`, since `cd` moves only Bash.
- **Read a spawned role's tier back before claiming it** – `agentType` in `~/.claude/projects/<project>/<session>/subagents/*.meta.json` and the transcript's per-turn `effort`; an `Effort:` line in the prompt does nothing.
- **A Skill call runs the installed plugin, never the working tree** – to try edited skill text outside the eval harness, copy `plugin/` to scratch and give a subagent the skill by absolute path, in a detached throwaway worktree of the target.
- **A `plan.json` on disk does not mean a plan run** – every FIS has one, one-story specs included; branch on what the argument names or on the plan's story count.

## Eval harness (DartClaw)

- **A `format: path` output resolves from uncommitted worktree changes** – an executor commits its story before returning, so the resolver finds nothing left; execution workflows return completion as `format: text`.
- **The structured-output extraction turn allows two turns and no tools** – a schema field the model must compute (git tree hashes, changed paths) fails the step; ask only for what the run already said.

## Process & Tooling

- **A skill rename is gated only for `/andthen:` sigils in four docs** (`audit-cookbook.py`) – `rg` the bare old name across the repo and diff each `Trigger on` clause against its predecessor's.
- **`git grep` skips untracked files** – a FIS proof over a file the story creates fails, and an `! git grep` absence check passes vacuously, until the commit; use `rg`, or `git add -N` in a throwaway `GIT_INDEX_FILE`.
- **`agent-browser screenshot --full-page` writes a file named `--full-page`** – put an absolute screenshot path before `--full`; the daemon's working directory is not yours.
- **The Bash tool's shell is zsh on macOS** – a word starting with `=` expands as a command path (`echo =====` fails and drops the rest of a `;` chain), and an unmatched glob aborts the call; quote separators and globs: `echo '---'`, `--include='*.py'`.
