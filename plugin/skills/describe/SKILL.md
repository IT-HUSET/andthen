---
description: Document what a project already is – map an existing codebase into architecture docs and discovered requirements, or extract and maintain its Ubiquitous Language glossary; `--model` adds the typed architecture or domain model. Trigger on 'map this codebase', 'document this repo', 'build a glossary'.
argument-hint: "[--mode codebase|domain] [--model] [--model-only] [output directory (codebase) or scope (domain)]"
---

# Describe

Describe documents what a project already is and never modifies its code.

## Input

`$ARGUMENTS` minus flags is, in codebase mode, the output directory `OUTPUT_DIR` (default `docs/`); in domain mode, the focus area `SCOPE` (blank for the whole project). Codebase mode always maps the whole project.

- `--mode codebase|domain` picks the mode.
- `--model` (`MODEL`), also set when the request asks for the model in words, adds the mode's typed model: `architecture-model` in codebase mode, `domain-model` in domain mode. Write it against [`architecture-model.md`](references/architecture-model.md) and [`architecture-model.schema.json`](references/architecture-model.schema.json).
- `--model-only` (`MODEL_ONLY`) writes the model against the same two files and no documentation – the refresh path when only the model must be current.

| Mode | Triggers |
|------|----------|
| **codebase** | "map the codebase", "document the architecture", "discover requirements", "architecture model" |
| **domain** | "glossary", "ubiquitous language", "domain terms", "terminology cleanup", "domain model" |

An explicit `--mode` wins, then a request that points at one mode. When neither decides it, ask once – codebase (preselected), domain, or both – because the modes write different documents and a wrong guess costs a full run.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- Every dispatch is a fresh subagent: the installed role agent it names (`implementer`, `reviewer`, `worker`) when available, else a generic inherited subagent. Never pin model or effort in a prompt.

## Workflow

1. **Resolve the mode.** A run of both modes runs codebase first, so the domain extraction reads a current `Architecture` document.

2. **Run the mode.** Follow its reference end to end:

   - Codebase mode: [`mode-codebase.md`](references/mode-codebase.md).
   - Domain mode: [`mode-domain.md`](references/mode-domain.md).
   - A run that writes documentation – every run but `--model-only`, and the extraction a domain `--model-only` run needs: [`project-document-templates.md`](../../references/project-document-templates.md).

   **Gate**: the reference's Output is printed.
