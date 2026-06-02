# Intent and Rules Context

Shared loader contract for skills that propose, apply, or critique changes to a codebase. Consumed by the `andthen:review` skill, the `andthen:quick-review` skill, the `andthen:remediate-findings` skill, and the `andthen:simplify-code` skill.

> **Core principle**: Reviews, remediations, and cleanups drift when the executor has no concrete anchor for what the work is *for* or what rules constrain *how* it can be done. Both bundles below exist to supply that anchor.


## What to collect

Two compact bundles, collected up-front by the consuming skill before any finding pass, routing decision, or mutation:

### Project Rules Context

- Root `CLAUDE.md` / `AGENTS.md` (project-tier instructions) plus the local rule / guideline files they reference (typically under `docs/guidelines/`, `plugin/references/`, or whatever the project uses).
- Filter to rules a diff can verify; skip pure process rules (release procedure, commit cadence) unless the change set touches that surface.
- Record source paths (file + section) so any finding that traces to a rule can cite the rule by source.

### Intent Context

- The governing artifact(s) for the change set: the Product document (project-level vision; default `docs/PRODUCT.md` via the Project Document Index `Product` row when present), PRD, FIS, `clarify` output, or active plan story. Any tier present contributes its falsifiers – higher tiers (Product, PRD) anchor strategic intent; lower tiers (FIS, plan story) anchor feature- and story-level intent.
- Extract: **Intent**, **Expected Outcomes**, **Non-Goals / anti-goals / Out-of-Scope**, and any explicit **deferrals** to later stories. Anti-goals is the Product-tier naming for the same semantic role as Non-Goals at the FIS tier – treat them identically for routing.
- Locate by walking up from changed paths; when present, consult the **Project Document Index** in `CLAUDE.md`. Do not invent intent the artifact does not state.
- Record source paths (with tier) so any routing decision against the bundle can cite the anchor – e.g. `dismissed: anti-goal in docs/PRODUCT.md`, `demoted: Non-Goal in <FIS path>`.

If no governing artifact is discoverable, omit the Intent Context bundle entirely – consuming skills degrade gracefully (routing operates on severity, confidence, and scope alone). Do not synthesize intent from the code itself; an unanchored review is better than a fabricated one.


## How to use the bundles

Both bundles are **falsifier sources**, not coverage checklists. They enter the consuming skill's decision flow as concrete evidence the executor can cite to dismiss, demote, promote, or block a finding or proposed change.

Canonical anchor moves – consuming skills compose these into their own gates:

- **Contradicts a Non-Goal / Out-of-Scope statement / explicit deferral** → dismiss the finding (or refuse the change) with the artifact cited as the falsifier.
- **Flags missing behavior the artifact defers to a later story** → real but out-of-scope for *this* change set; demote to a note-class finding, do not auto-apply.
- **Contradicts a stated Expected Outcome** → promote, regardless of where severity heuristics would otherwise land it. A real intent violation outweighs a low severity score.
- **Violates a Project Rules Context rule** → surface as a finding with the rule cited by source. Route severity through the consuming skill's own review or mutation policy; this shared reference supplies trace evidence, not a uniform blocking mandate.

Boy Scout cleanup (when permitted by the consuming skill) is bound by these anchors: a cleanup that would alter behavior covered by an Expected Outcome, change a structure the artifact explicitly chose, or contradict a Non-Goal is **out of scope for the cleanup pass** even when the code-quality heuristic favors it.


## Output contract

When a consuming skill emits findings, a report, or a fix proposal:

- Cite the source (file + section) of any rule a finding traces to.
- When Intent Context was loaded, name the anchor on each routing decision in one short clause: `dismissed: Non-Goal in <FIS path>`, `demoted to note: deferred to story 03`, `promoted: contradicts OC02`.
- When no governing artifact was discoverable, say so explicitly so downstream consumers (e.g. the `andthen:remediate-findings` skill) know the upstream routing operated without an Intent anchor and may need to re-anchor themselves.

The citation requirement is what makes this trace-based instead of assertion-based. A `Guardrails Coverage: N checked, M findings` line records that the rules pass ran; per-finding rule citations record what it actually checked.


## When to skip

- The skill is pure read/analysis with no proposed mutation (e.g. the `andthen:map-codebase` skill or the `andthen:visualize` skill). Intent loading is optional.
- The change set is a trivially scoped fix (single-line config change, single-character typo) where the lookup cost outweighs the drift risk. The consuming skill decides; do not invent a fixed threshold here.

Skipping the bundle in any *other* shape – including "the FIS is probably fine" or "I already read it once" – is the named failure mode this reference exists to prevent.
