---
description: Deprecated alias. Routes to the `andthen:simplify-code` skill for behavior-preserving code simplification. Do not invoke directly in new work.
argument-hint: "[args passed through verbatim to the andthen:simplify-code skill]"
---

# Refactor (Deprecated Alias)

The canonical skill is the `andthen:simplify-code` skill. This entry exists only so legacy invocations of the `andthen:refactor` skill keep working.

## INSTRUCTIONS

1. Invoke the `andthen:simplify-code` skill with `$ARGUMENTS` passed through verbatim (flags, paths, scope/description – all preserved).
2. Emit a one-line deprecation notice as the **final line of the reply**, after the `andthen:simplify-code` skill's completion summary has been returned in full. Wording: *"The `andthen:refactor` skill is deprecated – invoke the `andthen:simplify-code` skill directly next time."*
3. **Suppress the notice entirely** when `$ARGUMENTS` contains the literal token `--auto` (the AUTO_MODE trigger; see [`automation-mode.md`](${CLAUDE_PLUGIN_ROOT}/references/automation-mode.md)). During transition, also suppress when the legacy `--headless` token appears. The detection is purely textual on `$ARGUMENTS`; the redirect does not parse flags otherwise. Suppression preserves the canonical structured `STATUS:` / `FILES_CHANGED:` / `VERIFY:` / `DEFERRED:` block as the only output, so orchestrators parsing the bytes get exactly what the `andthen:simplify-code` skill emits.
4. Do not add behavior, flags, or workflow phases here. Any contract change belongs in the `andthen:simplify-code` skill.
