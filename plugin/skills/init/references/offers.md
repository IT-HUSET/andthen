# Offers

The procedures behind Step 3's offers. Work only the section of the offer the user took up, or, for the critical rules, declined.

## Role agents

Compare what is installed at both levels, for the host(s) in play, against the templates. Name each differing file and ask before replacing it. With nothing installed, ask the level:

- **User** – a personal default across projects: `agents/` under `$CLAUDE_CONFIG_DIR` / `$CODEX_HOME`, defaulting to `~/.claude` / `~/.codex`.
- **Project** – `.claude/agents/`, `.codex/agents/`, sharing the pins with the team.

Create nothing under a host whose home directory is absent. Definitions load at session start, so the roles take effect next session.

## Adopt Project Rules

Adopt into the project instruction file by default, so the policy travels with the checkout into CI and containers. An existing policy – custom, referenced, or a copy of the template – is replaced only when the user asks for an update, with the diff shown first.

**Adopt** – place the guideline body in the root instruction file (`AGENTS.md` in the shared layout, never the thin `CLAUDE.md`) under its own `# Critical Rules and Guardrails` heading. Rewrite only from that heading to the next heading, of any level, that is not one of the guideline's own, so surrounding content and customizations survive.

- A symlinked instruction file is never written through: report it and stop, since the target lives outside the project.

**Skip** – add the standalone marker `<!-- AndThen critical rules: skipped -->` to each owning instruction file where adoption was declined (`AGENTS.md` alone in the shared layout).

**Personal configuration.** User-level rules take the same bounded block in the same host home as the role agents above; skip an absent one. Conversation style is independent of rules adoption: configure it from `concise-critical.md` for the requested hosts only.

- **Claude Code**: the installed plugin registers `<plugin-name>:concise-critical`; otherwise copy the style to the host's `output-styles/` and use `concise-critical`. Merge `outputStyle` into user `settings.json`, preserving other keys; report a project setting that shadows it.
- **Codex**: put the style body below its frontmatter into top-level `developer_instructions` in user `config.toml`, above the first table header. Preserve existing instructions and other settings.

Never replace an existing style choice or rewrite an unparseable configuration. Tell the user configuration changes take effect next session.

**Gate**: Project policy adopted, preserved, or explicitly declined; only requested personal configuration changed.

## Optional documents

For each confirmed document type, generate the file from its template in `project-document-templates.md`, at the location from the **Project Document Index**.

## Sub-project instruction files

For each confirmed sub-project, generate a lightweight agent instruction file: the sub-project's name and description, its key development commands (inline table), and any conventions that differ from the root.

Mirror the root file choice – `CLAUDE.md`, `AGENTS.md`, or both. Both uses the same thin-import pattern; `@` paths resolve relative to the importing file, so the sub-project `CLAUDE.md` imports its sibling `AGENTS.md`.

Update the root `Key Dev Commands` document (**Project Document Index**), if created, with per-sub-project sections.
