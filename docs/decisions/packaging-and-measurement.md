# Decisions: Packaging and measurement

Rationale, evidence, history, and reopen conditions for the **Packaging and measurement** bullets in [DECISIONS.md](../DECISIONS.md) § Still Current. Each decision is stated there; a section here holds only what would not fit its one line.

## AndThen owns the artifact contracts; downstream tooling owns its views

The corpus carries its owner routing. A downstream viewer's own views include its boards and atlas, and it closes its notes loop by invoking the owning skill directly. No shipped skill reads the visual-review-notes payload. ADR-027 holds the rest of the rationale.

## No tests inside the plugin directory

Reopens only if a host gains an install-time exclude.

## Codex does not substitute `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_SKILL_DIR}` in skill text

Skill-root-relative paths work because both hosts announce that root; the first form is for a canonical, the second for a bundled script.

Reopens if the Agent Skills spec standardizes a path variable; upstream `openai/codex#35702` asks for Claude-compatible aliases.

## Leanness is measured per consuming path, and dedup never creates a reference file

One 40-word sentence copied into five skills costs less than five links to an 850-word canonical.
