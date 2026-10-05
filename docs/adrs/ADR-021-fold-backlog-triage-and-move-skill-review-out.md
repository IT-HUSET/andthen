# ADR-021: Fold `backlog-triage` into `tracker`, and move `skill-review` to project level

## Status
Accepted. Recorded 2026-09-25.

Amends [ADR-018](ADR-018-one-plugin.md): the list of skills that moved into core unchanged.

## Context

ADR-018 (2026-09-20) moved `backlog-triage`, `simplify-code`, `skill-review`, `spike` and `tracker` into core unchanged. Two of them add entry points that plugin users do not need.

**`backlog-triage`**

- It has zero recorded invocations. So does `tracker`.
- Its name clashes with `triage`, so each description has to point at the other.
- The two skills are the only tracker writers, and each carries its own Issue Tracker resolution, near-identical: `backlog-triage/SKILL.md:21` against `tracker/SKILL.md:22`.
- Four skills load `project-document-templates.md` (2,891 words) only to offer the Issue Tracker document when handed a non-GitHub URL.

**`skill-review`**

- It is used 112 times, all by the maintainer inside this repo, and nowhere else on record. It is a prompt-authoring tool, not part of the spec-driven workflow.
- Folding it into `review` as a lens was measured at about 8,400 loaded words against 6,826 today (+23%), because `review` always loads its report template and verdict reference (`review/SKILL.md:136`).
- Moving it out with copies of its three shared references would bring back the copy machinery ADR-018 retired.
- A project-level skill in this repo avoids both problems: it reads `plugin/references/` in place.

**New evidence against ADR-018's reopen conditions.** ADR-018 reopens its split "if a host gains per-skill install or a core-only user base is measured". This is not a split. It removes a maintainer tool from the shipped surface, and the evidence is the usage record: all use is in-repo, by the maintainer.

**Weighted criteria:**

| Criterion | Weight |
|---|---|
| Entry points and name clash removed | 30 |
| Words loaded per path | 25 |
| Contracts kept | 25 |
| Migration cost | 10 |
| Precedent | 10 |

## Decision

**`backlog-triage` becomes `tracker triage`.** `tracker` becomes a router over three modes:

- `publish` stays in the body;
- `triage` is today's `backlog-triage` procedure and agent brief, as a mode reference;
- `setup` writes the Issue Tracker document.

The two copies of the tracker-resolution rule become one. Every other skill that needs a tracker backend and finds no Issue Tracker document routes to `tracker` setup instead of loading the template set.

**`skill-review` leaves the plugin for this repo's project level.**

- Canonical home: `.claude/skills/skill-review/`.
- Codex copy: `.agents/skills/skill-review` is a symlink to it.
- Its references to the three shared canonicals become `../../../plugin/references/…`.
- It is invoked as `skill-review` on both hosts.
- A separate authoring plugin is left for later, if demand appears outside this repo.

**Result:** 19 skills become 17, after ADR-020.

## Consequences

**Easier**

- Two entry points leave the plugin listing, and the `triage`/`backlog-triage` name clash ends.
- The four skills that met a non-GitHub tracker URL stop loading 2,891 words for it.
- The shipped surface drops about 4,300 words (`skill-review`'s own files) plus the tracker duplication.
- `skill-review` keeps its path unchanged at 6,826 words, and keeps `--fix` with zero contract loss.

**Harder**

- Plugin users and loose-skill installer users lose a documented skill. `plugin/README.md:448-457` recommends it for their own skills. "Zero uses elsewhere" comes from one machine's log, and user scale is unknown. This is an accepted cost.
- The project skill reads the working-tree `review-calibration.md`, while an installed `review` reads the released one. That is fine for dogfooding, but the two can differ between releases.
- There are two directory entries (`.claude/skills/`, `.agents/skills/`), kept as one directory and a symlink.

**Unchanged**

- `tracker publish`'s idempotent marker and its script.
- The Structured Finding Contract that `skill-review` and `review` share.
- Loose-skill installs keep their shape, minus the two skills.

## Alternatives Considered

1. **A – fold `backlog-triage` into `tracker` only.** Rejected: 410 against 425. It leaves a maintainer-only tool in every user's skill listing. It is the fallback if the ADR-018 amendment is not accepted.
2. **B – fold both, with `skill-review` as a `review` mode reference.** Rejected (405). The lens path measures +23% unless `review`'s report step also becomes per-mode.
3. **C – merge `skill-review` naively into the `review` body.** Rejected (355): 10,300–11,200 loaded words.
4. **D – move `skill-review` out of the plugin with copies of its references.** Rejected (350). It brings back the copy-and-sync machinery ADR-018 removed.
5. **Floor option: keep both skills and trim their descriptions.** Rejected (350). It keeps two entry points and the name clash for no path saving.

## Reopens

If a user outside this repo asks for `skill-review`, which becomes the case for a separate authoring plugin, or if `review` becomes a router for other reasons and a measured lens path stays within +5% of 6,826 words.

## Project Compliance

- **Product Decision Rule.** It removes an entry point nobody invokes and a maintainer tool from every user's listing, and adds no machinery. "Only `plugin/` ships" (Learnings) holds: no shipped file names the project skill.
- **ADR-018's word budget.** Lowered in the same commit.

## References

- Research, 2026-09-25: DartClaw's public repo never names `backlog-triage`, so the fold needs no lockstep change there. The fold saves about 250 body and 51 description words, and routing tracker setup to `tracker` drops four inlined copies of `project-document-templates.md`, 11,564 words, from loose-skill installs.
- Usage, 2026-09-25: skill invocations counted in the maintainer's local Claude Code and Codex transcripts, subagent calls included; `skill-review`'s 112 were recorded under the `andthen-some:` namespace. The GitHub repo had no issues or discussions, so there was no external signal.
- Related: ADR-018, ADR-020.
