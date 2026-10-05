# Partial Setup

Repairing a project that already has `CLAUDE.md` and/or `AGENTS.md`: the defaults applied without a question, and the offers passed to Step 3.

## Host files

If both `CLAUDE.md` and `AGENTS.md` exist without the thin import, the conversion to the Step 2a layout is an offer: merge any CLAUDE.md-only content into `AGENTS.md`, then rewrite `CLAUDE.md` to `@AGENTS.md` plus a `## Claude Code` section for genuinely Claude-specific instructions. Convert only on confirmation. Declined, preserve per-host ownership and apply only the choices confirmed for each host.

If only one exists, repair that file, and offer the missing counterpart for cross-agent portability. Both offers go to Step 3.

- an existing `AGENTS.md` gets a thin `CLAUDE.md` import;
- an existing `CLAUDE.md` alone is promoted (`git mv CLAUDE.md AGENTS.md`), and the thin `CLAUDE.md` import is created.

## Apply the defaults

Apply these without asking:

- **Missing Index entries**: append to the existing Index in the shape it already uses, never rewriting it.
- **First-write sentences**: make the Index preamble's match `CLAUDE.template.md`'s, the `Learnings` header line included.
- **Project Overview**: when empty or a `TODO`, fill it per Step 2a.
- **Missing sections**: add them to the root agent instruction file(s). In the thin-import layout they belong in `AGENTS.md`, never the thin `CLAUDE.md`.
- **`Key Dev Commands`**: seed it per Step 2a when a manifest exists and the document does not.
- **Gitignore hygiene**: apply per Step 2a.

**Gate**: Every missing Index entry is appended and the preamble matches the template's; the Project Overview holds no `TODO`; `.gitignore` carries both entries; `Key Dev Commands` exists when a manifest does; nothing else was created – then Step 3.
