---
description: Describe what a project already is – map an existing codebase into documentation and implicit requirements, or extract and maintain its Ubiquitous Language glossary; `--model` emits the architecture or domain model for downstream tooling. Trigger on 'map this codebase', 'what does this repo do', 'build a glossary', 'generate an architecture model'.
argument-hint: "[--mode codebase|domain] [--model] [--model-only] [scope or output directory]"
---

# Describe

Read-only description of what a project already is. Both modes read code, docs, and conversation without modifying or committing them and write their own documentation outputs; `--model` emits the mode's typed artifact – alongside the documentation in codebase mode, in place of it in domain mode, where the model is a projection of the existing `Ubiquitous Language` document.

`$ARGUMENTS` minus flags is the focus area (`SCOPE`, blank for the whole project) or, in codebase mode, the documentation output directory `OUTPUT_DIR`, which defaults to the **Project Document Index** location or `docs/`.

## Mode (auto-detected from arguments or explicit `--mode`)

| Mode | Triggers | Read |
|------|----------|----------------|
| **codebase** (default) | "map the codebase", "understand this repo", "what does this project do", "document the architecture", "discover requirements", "architecture model" | `references/mode-codebase.md`; `../../references/project-document-templates.md` when the run writes documentation |
| **domain** | "glossary", "ubiquitous language", "domain terms", "terminology cleanup", "what do we call this", "domain model" | `references/mode-domain.md`; `../../references/project-document-templates.md` when the run writes documentation |

Explicit `--mode` always wins. On an ambiguous invocation ("describe this project") default to **codebase** and say which mode you took in one line, so the user can redirect – mode selection is cheap and reversible.

The two modes are separate because each emits a different typed artifact under `--model`: `architecture-model` from **codebase**, `domain-model` from **domain**. Either model is written against `../../references/architecture-model.schema.json` and `../../references/architecture-model.md`, read under `--model` only.

`MODEL` is true when `--model` is passed or the request asks for that mode's model in words; `--model-only` (`MODEL_ONLY`) implies it. Both pass through to the active mode, which owns their meaning. `MODEL_ONLY` refreshes the committed projection and writes no documentation – the deterministic surface an orchestrating skill uses when only the model needs to be current.

## WORKFLOW

Resolve the mode, state it, then load what its **Read** column names and follow the mode reference end to end. The mode reference owns its contract; nothing here overrides it.

A run that needs both descriptions runs the modes one after the other, codebase first – the context list it produces is the seed the domain extraction clusters against.
