# Existing-plan Regeneration

Read by the `andthen:plan` skill at Step 2 when `OUTPUT_DIR/plan.json` already exists.

The rerun is a full regeneration that preserves intact story state, converging on an in-memory plan ready for Step 5. Only schemaVersion `"2"` takes this path – any other version blocks, a v1 plan being evidence only that regenerates from its source.

Capture each story's `id`, `status`, `fis`, `completedTaskIds`, `owner`, and content-defining fields into a preservation map, retaining only a canonical sibling FIS that passes the reuse checks Step 5 states; discard every other pointer.

Step 4 restores `status`, `fis`, `completedTaskIds`, and `owner` for each story satisfying the **Preservation predicate**:

- same `id` and normalized name;
- a retained FIS;
- content-defining fields unchanged.

Task IDs survive only where that FIS declares them in canonical order; otherwise the story resets to `pending`/`null`/`[]`/`null`.

Emit `Regenerated plan.json; preserved status/fis/completedTaskIds/owner for stories satisfying the Preservation predicate: <ids>.` and, when anything reset, `Reset to pending/null/[]/null due to predicate failure (content drift or missing FIS file): <ids>.`
