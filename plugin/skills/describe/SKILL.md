---
description: Document what a project already is – map an existing codebase into architecture docs and discovered requirements; `--model` adds the typed architecture model. Trigger on 'map this codebase', 'document this repo', 'architecture model'. Glossary requests are the andthen:domain skill.
argument-hint: "[--model] [--model-only] [output directory]"
---

# Describe

Describe documents what a project already is and never modifies its code.

## Input

`$ARGUMENTS` minus flags is the output directory `OUTPUT_DIR` (default `docs/`). The whole project is always mapped.

- `--model` (`MODEL`), also set when the request asks for the model in words, adds the typed `architecture-model`. Write it against [`architecture-model.md`](references/architecture-model.md) and [`architecture-model.schema.json`](references/architecture-model.schema.json).
- `--model-only` (`MODEL_ONLY`) writes the model against the same two files and no documentation – the refresh path when only the model must be current.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.
- Every dispatch is a fresh subagent: the installed role agent it names (`worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt.

## Workflow

1. **Map the codebase.** Follow `mode-codebase.md` end to end. Loads:

   - Every run: [`mode-codebase.md`](references/mode-codebase.md).
   - Every run but `--model-only`, which writes no documentation: [`project-document-templates.md`](../../references/project-document-templates.md).

   **Gate**: the reference's Output is printed.
