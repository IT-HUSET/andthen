# Product Mode

Deltas to the `andthen:clarify` skill's steps when `MODE=product`; everything the body states and this file does not override still holds. Product scope is the whole product or product line, sitting above PRDs (one product spawns many) – the litmus is *"what should this product be?"* where feature scope asks *"what should this feature do?"*. `--brief` is a no-op here: this scope already writes one document.

**Step 1** – `OUTPUT_DIR` is not under the Specs & Plans root and the input dispatch is skipped: product mode writes the **Project Document Index** `Product` row, default `<project_root>/docs/PRODUCT.md`. At that path, the init-scaffolded **stub** (≤ 10 lines AND a `TODO` or `[fill me in]` marker) means write fresh content; anything else is a baseline – INPUT is the delta, Step 2 scopes to new or still-open gaps, Step 3 updates it in place.

**Step 2** – the questions are vision & problem statement; target users & personas; value propositions; anti-goals; success metrics; strategic constraints; proportionality facts (stage, scale, standing technical non-goals); roadmap themes, not features.

**Step 3** – write the product template in product-template.md at the resolved `Product` path, in place of a `prd.md`.

**Step 4** – validates the saved document as the body states, minus the checks that are PRD-shaped (user stories, Success Metrics rows, problem-solution fit, Executive Summary). It is this mode's only validation.

**Step 5 does not run** – product mode has no reviewer.

**Step 6 does not run** – the `Non-Goals` this mode writes are Step 3's template section, not an append carrying one feature's rejection.

**Follow-up** – the `andthen:architecture` skill in `--mode strategic-design`, deriving bounded contexts from the vision.
