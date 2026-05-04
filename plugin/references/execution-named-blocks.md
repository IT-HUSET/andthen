# Named Output Blocks

Shared protocol for surfacing ambiguity, out-of-scope observations, and missing
requirements during execution. Consumed by `exec-spec`, `quick-implement`, `triage`.

## Block Tags

- `CONFUSION:` — an input is ambiguous and the agent cannot safely proceed.
  State the ambiguity, list labeled options. Each consumer supplies its own
  arrow-prompt (e.g. `exec-spec` uses `-> Which approach?`).
- `NOTICED BUT NOT TOUCHING:` — out-of-scope observations the agent saw but did
  not act on. List the issues. Each consumer supplies its own arrow-prompt
  (e.g. `quick-implement` uses `-> Want me to create tasks?`).
- `MISSING REQUIREMENT:` — a needed behavior is undefined. State what is
  missing, list labeled options. Each consumer supplies its own arrow-prompt
  (e.g. `triage` uses `-> Which behavior?`).

Each block is labeled with concrete choices and (in interactive mode) the
consumer's arrow-prompt for the user.

## AUTO_MODE Override

Under `AUTO_MODE=true` (e.g. `--auto` / `--headless` flags — see
[`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md)):

- Do NOT emit arrow-prompts.
- Choose the safest defensible option and record it as an `ASSUMPTION:` in the
  completion report.
- If no defensible option exists, stop with `BLOCKED:` and list the minimum
  missing decisions.

This override is contractual — it ensures execution-oriented skills run
headless to completion (no silent stop-and-wait pauses).
