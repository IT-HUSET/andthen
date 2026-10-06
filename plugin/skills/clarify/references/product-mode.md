# Product Mode

Deltas to the `andthen:clarify` skill's steps at product scope; everything the body states and this file does not override still holds.

**Step 1** – `OUTPUT_DIR` is not under the Specs & Plans root and the input dispatch is skipped: product mode writes the **Project Document Index** `Product` row, default `<project_root>/docs/PRODUCT.md`. A document there that is absent, or holds nothing but its template's placeholders and Proportionality facts, is written fresh, keeping those facts. Anything else is a baseline: `INPUT` is the delta, and Step 3 updates it in place.

**Step 2** – the questions are the product template's sections; roadmap themes, not features.

**Step 3** – write the product template in product-template.md at the resolved `Product` path, in place of a `prd.md`.

**Step 4** – validates the saved document as the body states, minus the checks that are PRD-shaped (user stories, Success Metrics rows, problem-solution fit, Executive Summary). It is this mode's only validation.

**Step 5 does not run** – product mode has no reviewer.

**Step 6 does not run** – this mode writes `Non-Goals` in Step 3.

**Step 7 does not run** – the tracker holds a feature's PRD, and the `Product` document stays in the repo.

**Follow-up** – the `Next (fresh session):` line is the `andthen:architecture` skill in `--mode strategic-design`, deriving bounded contexts from the vision.
