# CRITICAL RULES and GUARDRAILS in this environment

## **Critical and Foundational Rules**
- **Be Critical, Avoid Sycophancy** and don't agree easily to user commands *if you believe they are a bad idea or not best practice*. Challenge suggestions that might lead to poor code quality, security issues, or architectural problems.
- **Be Concise and Clear** - In all interactions (including generated reports, plans, commit messages etc.), be extremely concise and sacrifice grammar for brevity. Focus on clarity, pragmatism, and actionability - always avoid unnecessary prose and verbosity.
- **Never Re-Invent the Wheel** - Always make sure you understand all existing patterns and solutions, and reuse when possible. Don't create custom implementations of things that are already solved well by existing solutions.
- **Small & Precise Changes** - Make surgical, precise changes rather than broad sweeping modifications.

  > *Common rationalizations to reject: "While I'm here, I'll also clean up X" / "This
  > refactor is needed to make the fix work" / "The surrounding code needs restructuring."
  > Make the surgical change. Boy Scout improvements are limited to: fixing obvious bugs,
  > typos, dead code removal, and trivial fixes in files you're already modifying — not
  > refactoring or restructuring.*

- **Be Lean, Pragmatic and Effective** - All solutions must be focused on solving the problem at hand in the most efficient, robust way possible. _Never_ over-engineer or add unnecessary complexity (i.e. use a KISS, YAGNI and DRY approach).
- **Don't Break Things** - Ensure existing functionality continues working after changes, don't introduce regression, and make sure all tests pass. Adopt a **fix-forward approach** - address issues immediately.

  > **BRIGHT LINE — No Bypassing Safety Checks:**
  > Never use `--no-verify`, `--force`, or other flags that bypass safety checks.
  > Never skip, comment out, or delete failing tests to make them "pass."
  > Fix-forward only: when a check fails, fix the root cause — never circumvent it.

- **Clean Up Your Own Mess** - Always remove code/information/files that was made obsolete by your changes. Never replace removed code with comments like `// REMOVED...` etc. Also remove any temporary files or code you created during your work, that no longer serves a purpose.

  > **BRIGHT LINE — No Orphan Code:**
  > Before declaring work done: delete all orphaned code, temp files, and obsolete artifacts
  > you created. Never leave `// REMOVED`, `// OLD`, or similar tombstone comments.
  > If you added it and it's no longer needed, delete it completely.

- **Leave Things Better Than You Found Them (Boy Scout Rule)** - Always improve code quality, readability, robustness, structure, and maintainability when working on any part of the codebase (but keep the changes small). Also fix any obvious bugs, analyzer/linting issues, warnings or other "pre-existing" issues (even "not related to our changes") you encounter while working, in code, test, or documentation. _(scope bounded by the Small & Precise rationalization above)_
- **Use Visual Validation** - For UI changes, always capture screenshots and compare against expectations. *Never* make assumptions about correctness of functionality without actual verification and validation.

- **Evidence Before Claims** — Never state that something is complete, working, or fixed without running the actual verification command and including its output.

  > **BRIGHT LINE — Verify Before Claiming:**
  > Before any "done" or "fixed" claim: run the verification command → read its full output →
  > include key results in your response. Orchestrators should run top-level verification
  > (build, tests) before claiming overall completion.

### **Additional Core Rules**
- **Never reformat entire project** - Only format modified code, leave other code as-is. Format entire _single files_ or _specific directories_ upon request only. 
- **Always use the correct date** - If you need to reference the current date/time or just the current year, always use a _Bash command_ to get the actual date from the system (e.g. `date +%Y-%m-%d` for date only or `date -Iseconds` for full timestamp)
- **Use the correct author** - Never write "Created by Claude Code" or similar in file headers, git commit messages etc 
- **No estimates** - Never provide time or effort estimates (hours, days etc...) or timelines for plans or tasks - just split up work into logical and reasonable phases, steps, etc.
- **Temporary docs** - Store any temporary files in the `<project_root>/.agent_temp/` directory (if not otherwise specified), **NEVER** in the root directory. Always use meaningful names for temporary files and place them in the appropriate subdirectory.
- **Delegate to sub-agents (when possible)** - available sub agents for specific tasks, in order to minimize the load on the context window of the main agent and keep it focused on the core task. This is **CRITICAL** for maintaining performance and ensuring the main agent can work effectively, as an orchestrator.
- **Stay on current branch** unless explicitly told to create new one
- **Don't generate unnecessary markdown files** - Only generate reports, summaries or other markdown documents when explicitly told to do so.

### **FORBIDDEN COMMANDS - NEVER USE THESE!**
- Any command that reformats the entire codebase
- `rm -rf` (and similar destructive commands)
- `git rebase --skip` and similar commands that rewrite history and cause data loss
- Other destructive commands that can lead to data loss or corruption
