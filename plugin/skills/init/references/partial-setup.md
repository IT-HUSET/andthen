# Partial Setup

Repairing a project that already has `CLAUDE.md` and/or `AGENTS.md` – Step 2b's read-and-check, the host-layout repair, and the confirmed-action list. Step references are to the skill body.

## Read and check

Read the existing root agent instruction file(s) and check for: Project Document Index, Project-Specific Guidelines and Rules section, Project Overview filled in, the Core orientation stubs (`PRODUCT.md`, `ARCHITECTURE.md`, `KEY_DEVELOPMENT_COMMANDS.md`, `TESTING-STRATEGY.md`, `DECISIONS.md`, `LEARNINGS.md` – same set Step 2a scaffolds by default), and referenced documents that actually exist.

If both `CLAUDE.md` and `AGENTS.md` exist without the thin import, offer conversion to the Step 2a layout: merge any CLAUDE.md-only content into `AGENTS.md`, then rewrite `CLAUDE.md` to `@AGENTS.md` plus a `## Claude Code` section for genuinely Claude-specific instructions – on confirm only; if declined, preserve per-host ownership and apply only the choices confirmed for each host.

If only one exists, repair that file and offer the missing counterpart for cross-agent portability: existing `AGENTS.md` → a thin `CLAUDE.md` import; existing `CLAUDE.md` only → promote it (`git mv CLAUDE.md AGENTS.md`, preserving blame) and create the thin `CLAUDE.md` import.

## Present the findings

Present the findings as a short marked checklist – what is present, which Index entries and Core stubs are missing, and whether project critical rules are adopted, declined, or not yet asked (Step 3) – then offer the fixes. Planning / Domain / Monorepo docs and the optional Index entries (`Context Map`, `Review Policy`) are offered interactively – never added by default.

If the `Architecture` document or the Project-Specific Guidelines and Rules section in the root agent instruction file(s) is missing and the codebase has 20+ files, also suggest:
```
Missing architecture/conventions documentation detected.
Run the `andthen:describe` skill in `--mode codebase` to auto-generate from codebase analysis? (recommended)
```

## Execute confirmed actions

Wait for user response, then execute confirmed actions:

- **Missing Core orientation stubs** (default): scaffold per Step 2a.
- **Gitignore hygiene** (default): apply per Step 2a.
- **New optional Index entries** (`Context Map`, `Review Policy`): append the entry only when confirmed, without a file – the Context Map is written later by the `andthen:architecture` skill in `--mode strategic-design`, the Review Policy by hand if ever.
- **Missing Index entries**: append to the existing Index in the shape it already uses, never rewriting it. The `Models` entry is always present (add it if an older file lacks it, replacing separate `Architecture Model` / `Domain Model` entries); its files are written later by the `andthen:describe` skill with `--model` and by the `andthen:architecture` skill, so the entry is a location declaration, not a missing referenced document to create.
- **Missing documents**: generate per Step 2a.
- **Role agents**: make the same comparison and offer as Step 2a, whatever is already installed.
- **Missing sections**: Add to the root agent instruction file(s) at the appropriate location (in the thin-import layout, sections belong in `AGENTS.md`, never the thin `CLAUDE.md`).
- **describe**: Invoke the `andthen:describe` skill in `--mode codebase`; skip creating the `Architecture` document from templates since it produces it from actual analysis
- **Critical rules**: Step 3 – preserve existing adoption or opt-out when repairing a project.
