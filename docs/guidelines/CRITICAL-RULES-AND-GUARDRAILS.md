# Critical Rules and Guardrails

## Core Behavioral Rules

- **Be critical, not sycophantic.** Challenge suggestions that lead to poor code quality, security issues, or architectural problems. Disagree when you have good reason to — diplomatic honesty over dishonest diplomacy.
- **Be concise and clear.** In all output — conversations, reports, plans, commit messages — sacrifice grammar for brevity. Focus on clarity, pragmatism, and actionability. Avoid unnecessary prose.
- **Never re-invent the wheel.** Before writing new code, understand all existing patterns, utilities, and solutions in the codebase. Reuse what exists. Do not create custom implementations of things already solved well by existing solutions.
- **Be lean, pragmatic, and effective.** Solve the problem at hand in the most efficient, robust way possible. Apply KISS, YAGNI, and DRY. Do not over-engineer, add speculative features, or introduce unnecessary abstractions.
- **Verify before claiming done.** Run the actual verification command (build, tests, lint) and include key results in your response. Never state something is complete or fixed without evidence. Orchestrators: run top-level verification before claiming overall completion.
- **Validate UI visually.** For UI changes, capture screenshots and compare against expectations. Never assume correctness without actual visual verification.
- **Surgical changes, Boy Scout cleanup.** Make precise, minimal changes to solve the problem at hand. Do not refactor, restructure, or expand scope beyond the immediate task. However, apply the **Boy Scout Rule** in files you are already modifying: actively fix obvious bugs, typos, dead code, analyzer/linting issues, and warnings you encounter — even if unrelated to your current task. Leave things better than you found them.

## Operational Rules

- **Correct date**: Use a Bash command (`date +%Y-%m-%d` or `date -Iseconds`) to get the current date — do not guess or hallucinate dates.
- **Correct author**: Do not write "Created by Claude Code" or similar in file headers or commit messages.
- **No estimates**: Do not provide time or effort estimates. Split work into logical phases and steps instead.
- **Temp files**: Store temporary files in `<project_root>/.agent_temp/` with meaningful names — never in the root directory.
- **Delegate to sub-agents**: Offload specific tasks to available sub-agents to keep the main agent's context window focused. This directly impacts performance and output quality.
- **Stay on current branch** unless explicitly told to create a new one.
- **Only commit your own changes**: Review the diff before committing. Never stage changes made by other agents or users.
- **Use `git mv`** for moving/renaming tracked files — preserves blame history.
- **Do not reformat entire projects**: Only format code you are modifying. Format entire files or directories only upon explicit request.
- **Do not use `git rebase --skip`** — it causes data loss. Ask the user for help with rebase conflicts instead.
- **Don't use em dashes** in any text, use en dash (–) instead. 
