# Artifact fixture corpus

One minimal, real-shaped artifact per type in the table below, plus one sample of the notes payload a
viewer sends back. Downstream tooling pins this directory by AndThen tag and renders these files to
check conformance; `tests/test_fixtures.py` reads the table, so a new type ships with a fixture here
and a row below, or the suite fails.

The **owning skill** is the skill that maintains the source artifact; it heads a notes payload. **Where
notes go** is what that owner does with them.

| type | fixture | owning skill | where notes go |
|---|---|---|---|
| `prd` | `prd.md` | `andthen:clarify` | `andthen:clarify` amendment context, or conversational input to a fresh `andthen:plan` run |
| `plan` | `plan.json` | `andthen:plan` | `andthen:plan` regeneration, `andthen:exec-plan` execution caveats, or `andthen:review --mode gap` |
| `fis` | `s01-harden-the-session-cookie.md` | `andthen:spec` | `andthen:spec` (standalone) or `andthen:plan` (plan story) regeneration, or `andthen:exec-spec` execution context inlined beside the spec |
| `intent` | `intent.md`, `intent-intake.md` | `andthen:clarify` | `andthen:clarify`, which folds an intent doc into the PRD, or amends it under `--brief` |
| `product-vision` | `product-vision.md` | `andthen:clarify` | `andthen:clarify`, which amends the vision document |
| `review-report` | `review-report.md`, `review-report-mixed.md` | `andthen:review` | `andthen:implement-fix` for actionable findings, or `andthen:review` for re-scoping |
| `tradeoff` | `tradeoff.md` | `andthen:architecture` | the next `andthen:architecture` run in `--mode trade-off` |
| `adr` | `adr.md` | `andthen:architecture` | the next `andthen:architecture` run in `--mode trade-off` |
| `architecture-review` | `architecture-review.md` | `andthen:architecture` | the next `andthen:architecture` run in `--mode review` |
| `strategic-design` | `strategic-design.md` | `andthen:architecture` | the next `andthen:architecture` run in `--mode strategic-design` |
| `fitness` | `fitness.md` | `andthen:architecture` | the next `andthen:architecture` run in `--mode fitness` |
| `decompose` | `decompose.md` | `andthen:architecture` | the next `andthen:architecture` run in `--mode decompose` |
| `event-storming` | `event-storming.md` | `andthen:architecture` | `andthen:architecture --mode strategic-design` (Big Picture) or `--mode decompose` (Design Level) |
| `event-storm` | `event-storm.json` | `andthen:architecture` | the next `andthen:architecture` run in `--mode event-storming` |
| `context-map` | `context-map.json` | `andthen:architecture` | the next `andthen:architecture` run in `--mode strategic-design` |
| `architecture-model` | `architecture-model.json` | `andthen:describe` | `andthen:architecture --mode strategic-design` or `--mode review`, or `andthen:describe --mode codebase` for model corrections and regeneration |
| `domain-model` | `domain-model.json` | `andthen:describe` | `andthen:describe --mode domain` for glossary corrections, then `--model` to regenerate the projection |

`visual-review-notes.md` is the notes payload in the exact shape a viewer copies or sends: the H1 names
the owner and the artifact path, each `## Section:` block carries one section's heading verbatim, notes
are `- ` bullets in creation order, and a multi-line note continues with two-space indentation. The
`andthen:now-what` skill keys on that H1 to route a pasted payload.

The two review reports split the header the `andthen:review` skill pins under the H1: `review-report.md` is a
single-lens report with the always-present fields, `review-report-mixed.md` a remediated follow-up review over a
lens chain, carrying `Resolved chain`, `Follows`, `Remediated`, and the one `## Verdict` section a mixed report
has.

The four model `.json` fixtures are sample documents for a downstream renderer; nothing in this repo
validates them; their shape contract is the `*.schema.json` shipped in `plugin/references/`, with the
semantics in `{architecture-model,board-models}.md` beside it. `plan.json` and `s01-harden-the-session-cookie.md`
are read by two more suites: `tests/test_tracker.py` projects the plan into tracker payloads, and
`tests/test_audit_cookbook.py` pins its `schemaVersion` against `plan.schema.json`. Change a fixture
and run every suite that reads it.
