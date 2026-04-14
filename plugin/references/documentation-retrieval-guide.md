# Documentation Retrieval Guide

Methodology for getting current, implementation-relevant documentation without flooding the calling agent with raw source material.

## Core Approach

- Work as a background lookup task
- Prefer official, version-specific sources
- Retrieve only what the caller needs to decide or implement
- Return distilled conclusions, not page dumps

Prioritize concrete API behavior, configuration details, examples, deprecations, and caveats over descriptive prose.

## Tool Priority

1. **Context7 MCP** for library/framework docs
   - resolve the library first
   - query a narrow topic, not the whole product
   - include version when known
2. **Fetch MCP** for known documentation URLs
   - fetch the relevant page or section
   - check `llms.txt` when the docs site exposes it and it helps navigation
3. **Web search** only to locate the right official source or, if no official source exists, the highest-authority fallback

## Query Optimization

- include library/framework name and version when relevant
- ask the smallest question that unlocks the task
- prefer multiple targeted lookups over one broad lookup
- include intent words such as `API reference`, `configuration`, `migration`, `authentication`, `middleware`

## Result Evaluation

- prefer official docs over community content
- prefer versioned pages over generic landing pages
- extract the exact behavior or signature the caller needs
- capture deprecations, caveats, and incompatible examples
- cross-check across two sections when a single page feels incomplete or ambiguous

## Error Handling

- If the best source is unclear, say so and explain the fallback path used.
- If version is unknown but matters, state the assumption explicitly.
- If no reliable documentation is found, say that clearly instead of inferring from memory.

## Output Format

Return:
- **Source**: product, version if known, and link
- **Answer**: the concise answer to the caller's question
- **Details**: exact API/configuration points that matter
- **Example**: a minimal code/config example only when it materially helps
- **Caveats**: deprecations, version traps, or missing certainty
