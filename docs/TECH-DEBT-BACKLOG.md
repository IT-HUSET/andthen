# Technical Debt Backlog

## High
<!-- Severity: blocks correctness, security, or critical workflow. Address with priority. -->

_No tech debt recorded yet._

## Medium
<!-- Severity: maintainability, clarity, or non-critical correctness. Schedule deliberately. -->

_No tech debt recorded yet._

## Low
<!-- Severity: cosmetic, minor consistency, or opportunistic cleanup. Address when convenient. -->

### Run: 2026-05-04 20:52 UTC — tech-debt

#### DEFERRED FINDINGS

- **`_canonicalize_dir` `mkdir -p` swallows error output** (`scripts/install-skills.sh:127`)
  - Severity: Low
  - Justification: pre-existing, not regression-induced; explicitly out of scope for the agent-to-skill-consolidation FIS. The end-user error message is correct ("cannot canonicalize directory <path>") but loses the underlying cause (permission denied, EEXIST, etc.). Cosmetic — minor diagnostic loss, no behavior bug. The related and more severe empty-arg leak was fixed separately in the same change set under `[0.16.0]`.

