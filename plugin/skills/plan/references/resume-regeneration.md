# Existing-Plan Resume / Regeneration (Step 2)

Local-output-mode existing-plan handling for the `andthen:plan` skill. Applies when `OUTPUT_DIR/plan.json` already exists: treat the rerun as a full regeneration preserving intact story state.

Capture each story's `id`, `status`, `fis`, `owner`, the content-defining fields per the **Preservation predicate** (see *Writability rules* in *The Plan Schema*), and `executionNotes` into a preservation map. Discard legacy `metadata` fields (e.g. `immutableDigest`) – not in the current schema. Continue Step 2 and proceed through 3–4 as a fresh generation. After Step 4's reassembly:

- **Preserve `executionNotes`** by prepending the captured value to the freshly assembled value (de-duplicate identical lines; the migration annotation is durable per the schema's **Migration from legacy `plan.md`** section).
- **Restore `status`, `fis`, and `owner`** from the preservation map per the **Preservation predicate**. Stories failing any clause reset to `pending` / `null` / `null`.
- Emit: `Regenerated plan.json; preserved status/fis/owner for stories satisfying the Preservation predicate: <id-list>.` and (when applicable) `Reset to pending/null/null due to predicate failure (content drift or missing FIS file): <other-id-list>.`

If every story satisfies the predicate, omit the reset line – the regeneration is observationally a resume.
