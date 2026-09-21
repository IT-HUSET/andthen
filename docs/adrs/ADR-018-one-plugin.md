# ADR-018: Ship AndThen as one plugin

**Status:** Accepted

**Recorded:** 2026-09-20

**Supersedes:** [ADR-005](ADR-005-optional-satellite.md). **Amends:** [ADR-004](ADR-004-shared-plugin-sources.md) – the satellite-copy clause.

## Context

ADR-005 split optional tools into `andthen-some` so a workflow install would not carry every tool. Measured on the `1.0` branch at `71ae505`:

- The saving is eight skill descriptions, about 2,400 always-loaded characters. Skill bodies load on invocation only, and ADR-005's own amendment records that the size win came from compressing references, not from the split.
- The boundary's recurring cost sits in core: 14 "when installed; otherwise …" fallback sites in 12 files plus 4 bare namings, regrown after the amendment removed four; 6 byte-identical reference copies with their sync and byte-diff machinery in `install-skills.py`; six version locations, two READMEs, two entries per marketplace file; and a Learnings trap – a satellite skill cannot load a core skill's own reference.
- Dependency is one-way: the satellite names core skills about 30 times and is installable alone but useless alone.
- `andthen-some:<name>` becomes a public name at 1.0. After ship, the reversal is a breaking rename.

Three satellite skills were weighed on the Product Decision Rule while deciding the merge, because folding a skill after the move means touching its files twice.

## Decision

**One plugin, `andthen`, from `plugin/`.** The satellite directory, its manifests, its reference copies, and the `andthen-some` namespace retire before 1.0 ships. `backlog-triage`, `simplify-code`, `skill-review`, `spike`, and `tracker` move into core unchanged, and every offer-when-installed site becomes a plain skill reference.

Three skills do not move:

- **`council` dissolves; nothing is added.** Its two filter phases spawn fresh subagents to run the Findings Filter that `review` runs inline by design, under the Devil's Advocate and Synthesis Challenger roles `review-calibration.md` already names. Its seat fan-out is an N× cost multiplier that no phrasing may trigger. The one unmeasured shape – a finding visible only at a lens boundary – is graded in the `review` eval case, not written into the prompt.
- **`security-review` folds into the core `security` lens, essentials only.** The lens gains the exposure-modifier table, two contrastive severity pairs, and the scan script's semgrep-JSON compaction: about 295 words that load only under `--mode security`. The five OWASP checklists retire – dated with no gate that could notice, and their pattern fallback generates the false positives the calibration then spends its traps neutralising. Depth beyond that is pointed at from `README.md`, never from skill content; the lens already reports unavailable scanner depth.
- **`e2e-test` retires.** Nothing dispatches it, nothing reads its report, no eval covers it, and its body is what a model with a browser tool does unprompted. Its two contracts – fix only when asked, the report shape – name no run where the model went wrong without them. The `outcome` lens keeps its walked path, driven by hand or through `visual-validation`.

**The shipped prompt surface gets one aggregate word budget:** a fast-tier test over the `.md` files under `plugin/` excluding READMEs, set a few percent above the count after the merge and the cuts have landed – a ceiling, not the current count, since a budget pinned to the count fails on the next fix and buys unrelated trims (2026-09-21) – and raised only by editing that number in the same commit. Per-file ceilings are rejected: 85% of quiet-period growth arrived as new files, which a per-file manifest does not see, and a 25-file move would rewrite every key. The budget is the last commit of the initiative because its baseline is the number every earlier phase moves.

## Rationale

The merge: the boundary costs core prose and installer machinery on every change while saving about 600 always-loaded tokens. ADR-005's amendment already ran this experiment for `architecture-analysis` and `describe` with the same result – placement is bookkeeping, the content cut is the work.

The budget: no gate in the suite fails on surplus – six assert presence, and the one ceiling is `DESCRIPTION_CAP`. Removal has been owner-driven: 38 campaign commits out of 224 did 75.5% of six weeks' removal. The project's own measurements say a prose principle does not bind (0 of 6, then no effect) and a numeric cap does (101–115 words against 238–275, 3 of 3). A gate moves the cost of accretion to the point of edit, one reviewed line in a diff. The surface is not on a ratchet – 192,695 words at its August peak, 100,716 today – so the gate races no rate; it exists so the down-stroke stops depending on one person. It is a budget on an authored artifact, the same class as the shared description budget in the authoring guidelines, not the numeric output shaping the prompt guidelines reject.

Rejected: **keeping `council` and `security-review` as skills in the merged plugin** – the first keeps the N× multiplier for zero words saved, the second ships 6,900 words of which about 295 are load-bearing. **A `review` mode switch for the council** – every candidate trigger is inference from phrasing, which three shipped documents forbid. **Folding `e2e-test` into `testing`** – different artifact, no source changes, and three of `testing`'s four shared sections would need an except-clause. **Per-file ceilings** – above.

## Consequences

- Every user gets 21 skills, and all descriptions compete in one listing: about 5,800 characters today against Codex's 8,000 fallback budget, each held by `DESCRIPTION_CAP`.
- `install-skills.py` loses `_satellite_assets`, `--sync-satellite-assets`, and the byte-diff check; `docs/ARCHITECTURE.md` loses its two-plugin section and the `*` markers; the Learnings trap dies with the boundary; four version locations instead of six. Loose-skill installs keep their shape.
- After the rename the old satellite stays *installed* on both hosts while gone from the manifest, and every eval measures a stale two-plugin install until it is uninstalled by hand.
- Every legitimate growth commit carries a budget line.

Reopens: **the split**, if a host gains per-skill install or a core-only user base is measured rather than assumed; **`e2e-test`**, on an `outcome` or `testing` run over a UI product where the model fails to walk journeys unprompted; **the council's seats**, on a review where partition fan-out demonstrably misses what concern fan-out would catch; **the budget**, if within one release 80% or more of its raises land with no discussion in the commit – the falsifier the gate carries.

## Evidence

- Retiring: `plugin-some/`, the `andthen-some` entries in both marketplace files, `plugin-some/skills/{council,e2e-test,security-review}/`.
- Measured at `71ae505`: surface 100,716 words in 107 files; `rg -n 'andthen-some' plugin/ --glob '!README.md'` → 18 lines in 16 files; the one ceiling at `tests/test_skill_review.py:27`.
- History: `31c4211` establishes the satellite; `19a4326` returns `architecture-analysis` and `describe` to core (ADR-005 amendment).
- Working notes (local, gitignored): `docs/temp/research/2026-09-20-streamline-and-merge-brief.md` (decisions D1–D10 with sources), `2026-09-20-single-plugin-merge-brief.md` (the merge surface), `2026-09-20-single-plugin-merge-plan.md` (file-level phases); audits under `.agent_temp/ops-audit/`.
