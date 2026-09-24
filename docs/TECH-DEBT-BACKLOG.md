# Technical Debt Backlog

## High
<!-- Severity: blocks correctness, security, or critical workflow. Address with priority. -->

_No tech debt recorded yet._

## Medium
<!-- Severity: maintainability, clarity, or non-critical correctness. Schedule deliberately. -->

- **Claude eval subjects run in the maintainer's context** – every cell's workspace sits under `.agent_temp/evals/` inside this repo and DartClaw sets `inherit_user_settings: true`, so the subject loads the maintainer's global `CLAUDE.md`, this repo's `CLAUDE.md` and `CLAUDE.local.md`, and their output style; the `directory` marketplace also loads skills from the working tree, not the installed copy `evals/README.md` claims. Remedy: stage each cell's workspace outside the repo as part of the run (evidence stays under `.agent_temp/evals/`), and give the subject the plugin without the rest of the user settings. Blocker: how the subject gets the `andthen` plugin once user settings are not inherited. Source: 2026-09-24 `plan` eval investigation.

## Low
<!-- Severity: cosmetic, minor consistency, or opportunistic cleanup. Address when convenient. -->

_No tech debt recorded yet._
