# Intent and Rules Context

The two context bundles behind critiquing or applying a change to a codebase: what goes in each, and how each routes a decision.

## What to collect

Before any finding pass, routing decision, or mutation:

### Project Rules Context

- The project-tier instructions the host loaded, plus the local rule / guideline files they reference (typically under `docs/guidelines/`, `plugin/references/`, or whatever the project uses).
- The **Review Policy** document when the Project Document Index carries that entry – an optional, project-authored calibration of the review itself, not a rule set about the code. Three citable sections: `## Excluded Paths` (globs for generated, vendored, or migration paths), `## Extra Passes`, `## Verdict Thresholds`. The entry ships in the init template; the file does not, and no skill creates it. Absent file: nothing degrades, the defaults are the policy.
- Skip process rules the diff cannot verify.
- Record source paths (file + section) so any finding that traces to a rule can cite the rule by source.

### Intent Context

- The governing artifact(s) for the change set, or for what is about to be authored: the Product document (project-level vision; default `docs/PRODUCT.md` via the Project Document Index `Product` row when present), PRD, FIS, `clarify` output, or active plan story. Any tier present contributes its falsifiers – higher tiers (Product, PRD) anchor strategic intent; lower tiers (FIS, plan story) anchor feature- and story-level intent.
- Extract: **Intent**, **Expected Outcomes**, **Non-Goals / anti-goals / Out-of-Scope**, any explicit **deferrals** to later stories, and the Product document's **Proportionality** facts – stage, scale, standing technical non-goals. Anti-goals is the Product-tier naming for the same semantic role as Non-Goals at the FIS tier – treat them identically for routing.
- Locate by walking up from changed paths; when present, consult the **Project Document Index** in the project instructions the host loaded. Do not invent intent the artifact does not state.
- Record source paths (with tier) so any routing decision against the bundle can cite the anchor – e.g. `dismissed: anti-goal in docs/PRODUCT.md`, `demoted: Non-Goal in <FIS path>`.

If no governing artifact is discoverable, omit the Intent Context bundle entirely – routing then operates on severity, confidence, and scope alone. Do not synthesize intent from the code itself.


## How to use the bundles

Both bundles are **falsifier sources**, not coverage checklists – evidence the executor cites to dismiss, demote, promote, or block. Canonical anchor moves, composed into your own gates:

- **Contradicts a Non-Goal / Out-of-Scope statement / explicit deferral** → dismiss the finding with the artifact cited as the falsifier. A change the user asked for that contradicts one is a decision for the user, not the run: ask it attended; unattended, leave the change unmade and record `ASSUMPTION: <Non-Goal> stands – the user revising it`, citing the artifact.
- **Flags missing behavior the artifact defers to a later story** → real but out-of-scope for *this* change set; demote to a note-class finding, do not auto-apply.
- **Contradicts a stated Expected Outcome** → promote, regardless of where severity heuristics would otherwise land it. A real intent violation outweighs a low severity score.
- **Violates a Project Rules Context rule** → surface as a finding with the rule cited by source. Route severity through your own review or mutation policy; this reference supplies trace evidence, not a uniform blocking mandate.
- **Falls inside a Review Policy exclusion, or under one of its calibrated thresholds** → in the `andthen:review` skill's Guardrails pass, drop it with the policy cited exactly as a Non-Goal is; elsewhere surface the hit instead. Policy calibrates *coverage and severity* and nothing else, and only stricter – a policy that would widen the Fix bar, change the finding contract, or empty a pass's coverage is out of scope: surface it and review under the defaults.

Boy Scout cleanup, where permitted, is bound by these anchors: a cleanup that would alter behavior covered by an Expected Outcome, change a structure the artifact explicitly chose, or contradict a Non-Goal is **out of scope for the cleanup pass** even when the code-quality heuristic favors it.


## Output contract

Findings, reports, and fix proposals cite the source (file + section) of any rule they trace to, and – when Intent Context was loaded – name the anchor on each routing decision in one clause: `dismissed: Non-Goal in <FIS path>`, `demoted to note: deferred to story 03`, `promoted: contradicts OC02`. When no governing artifact was discoverable, say so, so downstream consumers know the upstream routing had no Intent anchor and may need to re-anchor.

Citation is what makes this trace-based rather than assertion-based: a `Guardrails Coverage: N checked, M findings` line records that the rules pass ran; per-finding citations record what it actually checked.


## When to skip

Only two shapes: pure read/analysis with no proposed mutation (the `andthen:describe` skill), and a trivially scoped fix where lookup cost outweighs drift risk – your call, no fixed threshold here.

Skipping in any *other* shape – "the FIS is probably fine", "I already read it once" – is the named failure mode this reference exists to prevent.
