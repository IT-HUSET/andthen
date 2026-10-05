# ADR-027: Draw AndThen artifacts as checked pages with a small `visualize` skill

## Status
Accepted. Recorded 2026-10-04.

Rewrites the Still Current note "AndThen renders nothing; it owns the artifact contracts" in place, because the reopen condition it named, a reader with no downstream tool, is met. It reverses the migration guide's "removed with no replacement" for `visualize`. `explain-changes` stays retired.

## Context

**No public tool shows what five JSON files hold.** 1.0 writes `architecture-model.json` and `domain-model.json` (`describe --model`), `context-map.json` and `event-storms/<slug>.json` (`architecture` in strategic-design and event-storming modes), and `plan.json`. `plan` reads the module boundaries in `architecture-model.json`, and execution reads `plan.json`. Nothing in AndThen reads `domain-model.json`, the two boards, or the model's `tours`, and `board-models.md` says the board JSON "is what a board view draws". The only viewer, AndThen Studio, is private, and on 2026-10-04 the maintainer ruled that it stays private for now.

**The retired skills were large and fragile.** At 0.40, `visualize`, `explain-changes` and `excalidraw-diagram` held 43,239 words of markdown, 64% of today's 68,000-word shipped-surface budget. On top of that came 13 artifact templates, about 3,500 lines of renderer JS and a 1,797-line atlas template. CHANGELOG 0.17.0 (on `main`) names four regressions in model-written HTML. In one, a `SyntaxError` disabled the page's whole `<script>`, and every button with it. The note's verdict on them stands: the model-composed half never had a gate.

**Models now write such pages well, and a check is within reach.** A one-line prompt produces a decent self-contained page with inline SVG figures (the maintainer's `systemskiss.html`). A headless browser, or the desktop app's browser pane, renders a page inside the project folder and returns a screenshot. The pane was verified on 2026-10-04 and acts only on files inside the project folder. `ship` step 3 already asks for "the smallest view that makes the point", which may be an SVG.

**The floor works without a skill, but nothing checks it.** A user can ask for such a page in plain words today. A skill adds three things over that: the render-and-look check as a stated gate, the meaning of the JSON fields (evidence levels, `tours`, the four runtime node kinds), and a name users can find. No 1.0-era run shows a plain-words page failing. The failure evidence comes from 0.17.

HumanLayer's `show-me` (462 words) and pstack's `teach` and `how` show demand. Under the Decision Rule that is context, not evidence.

## Decision

**A small `visualize` skill draws an AndThen artifact as one self-contained HTML page with inline SVG figures, and checks the page by rendering it.** It is the 20th skill.

- **Model-written, with no machinery.** No templates, no per-type renderers, no Mermaid, no layout scripts, and no notes loop. Interactivity is left to the model. Web fonts may load, with a fallback stack so the page still reads offline.
- **The gate is a render-and-look loop.** The run renders the page in a headless browser where one is available, otherwise in any browser it can reach. It looks at the result and fixes overlaps, clipped labels, unreadable arrows, and broken interactions, repeating until the page is clean. A run that reaches no browser reports the page as unchecked. The project's `Visual Validation` document plays no part, because it covers the project's own UI, which may be a native app.
- **Any AndThen artifact.** The user names one. The skill states field meanings only for the five JSON types, because they are why it exists. It has no type check, because no contract needs that gate (Product, Flexible).
- **The page goes to the `Agent Temp` location** (default `.agent_temp/`) unless the user names another place. It is not committed by default, because it is a derived copy that drifts from its source.
- **The name returns.** Users reach for "visualize", and 0.x references to `andthen:visualize` keep working. A reference that passes an old mode gets its best reading.
- **The outputs that only a viewer uses stay.** The board JSON and `tours` now have a public reader.
- **`now-what` drops its route for pasted visual review notes.** Only Studio produces that payload, and its first heading already names the owning skill. The payload contract stays in `scripts/fixtures/renders/` because Studio pins that folder by tag: the sample, the shape rules and owner mapping in its `README.md`, and `NotesSampleTest`. `NotesRouteTest` goes with the route.

## Consequences

**Easier**
- Public users can see what the model and board files hold, and any artifact can become a page that was rendered and looked at before it is shown.
- `now-what` sheds about 75 words that every run loaded for a block no public tool produces.

**Harder**
- 20 skills, one more description in Codex's shared description budget, and a surface-budget raise.
- The check is the model judging its own render. That is the gate the old skills lacked, but it is not a fresh-context reader.
- If a downstream viewer goes public, the JSON types again have two producers of one view, which is why the 0.x skills retired.
- 0.x users may expect the old notes loop and modes.

**Unchanged**
- AndThen owns the artifact contracts. Downstream tooling owns its views and closes its notes loop by invoking the owning skill directly. Shipped skills never name a downstream app.
- `explain-changes` and `excalidraw-diagram` stay retired, and `visual-validation` remains the check for the project's UI.

## Alternatives Considered

1. **Draw only the five JSON files.** Rejected: it adds an input check and a refusal path for no contract, and a plan's dependency graph or a FIS's flow is worth a page too.
2. **Draw anything, code included.** Rejected: that goes beyond why the skill exists, and its description would trigger on every "explain this", competing with plain chat.
3. **A new name (`draw`, `show`).** Rejected: neither carries 0.x baggage, but users reach for "visualize", and 0.x references would stay broken.
4. **Retire the outputs only a viewer uses.** Stop writing `context-map.json`, `event-storms/*.json`, and `tours`. Rejected: Studio's boards and the corpus lose those types, and the skill gives them a reader anyway.
5. **Keep `now-what`'s notes route.** Rejected: every public run loads it for a block it never sees.
6. **Drop the notes contract too.** Rejected: Studio pins the corpus, and redefining the shape when Studio goes public would change a published contract.
7. **Floor option: no skill, so users ask in plain words.** Rejected: nothing checks a page unless the user thinks to ask, and nothing tells a user that the JSON files can be drawn or what their fields mean.

## Implementation Notes

Implement directly in one change, not through a plan. The work is one skill and the records that name it.

1. Add `plugin/skills/visualize/SKILL.md` and its `agents/openai.yaml`, written to intent per `docs/SKILL-AUTHORING-GUIDELINES.md` and reviewed with the `skill-review` skill. The description fits the 400-character cap. Shared references go in the installer arrays only if the skill loads one.
2. Remove the notes row and its `### Notes` paragraph from `now-what`. Remove `NotesRouteTest` and `notes_route` from `tests/test_fixtures.py`. In the corpus `README.md`, drop the sentence saying `now-what` keys on the payload heading.
3. Update the records:
   - `MIGRATING-FROM-0.x.md`: the `visualize` row, and `visualize` in its grep.
   - `README.md`: the skill count, and the figure regenerated with `python3 scripts/skills-overview.py`.
   - `plugin/README.md`: a `visualize` section.
   - `docs/ARCHITECTURE.md`: the skill list.
   - `CHANGELOG.md`: rework the existing bullets rather than adding new ones (the `now-what` bullet's pasted-notes clause, and `visualize` in the removed-skills line), then add the skill.
4. Raise `tests/surface-budget.json` in the same commit.
5. No eval case (maintainer ruling, 2026-10-04).

## Project Compliance

- **Product Decision Rule.** The outcome it enables is a public view of files AndThen writes. The check names the failure it prevents: 0.17.0's page whose every button went dead.
- **Lean, Flexible, Intent-driven.** It has no templates or renderers and no input type check, and it is written to intent. `now-what` loses a route no public run uses.
- **Standing technical non-goals.** It adds no hosted control plane, service, or downstream adapter. The page is a local file.
- **Still Current notes.** "No model-only or user-only skills" holds: users and skills both invoke it. The rewritten note keeps AndThen's ownership of the contracts and the rule against naming a downstream app.
- **ADR-018.** The surface raise is the reviewed act in `tests/surface-budget.json`.

## Reopens

- If a downstream viewer goes public and covers the JSON types: weigh retiring the skill's JSON half against having two producers of one view.
- If recorded runs report a page clean when its render showed a defect: the check needs a fresh-context reader.

## References

- The decision brief of 2026-10-04 and this session's interview with the maintainer.
- CHANGELOG 0.17.0 on `main`; the 0.40 skill bodies at the parent of `af64b753`.
- `plugin/skills/architecture/references/board-models.md`, `scripts/fixtures/renders/README.md`.
- Related: ADR-018, ADR-026.
