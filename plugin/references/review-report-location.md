# Review Report Location

Single source of truth for where review skills write their consolidated report files. Consumed by the `andthen:review` and `andthen:architecture` skills (and any future skill that produces a review-style report). The report **content** format lives elsewhere – this reference governs only the filename and directory.

The consuming skill contributes:
- a **`<feature-name>` token** for the filename (e.g. `<feature-name>` for code/gap, `<spec-name>` for doc, `<scope-or-topic>` for architecture)
- a **report suffix** (e.g. `code-review`, `gap-review`, `architecture`) – usually held in the consuming skill's own mode/invocation table; this asset never invents a suffix
- whether the primary target is a **doc artifact** or a **source-code artifact** – this gates whether tier 2 fires (see the Source-Code Subdirectory Guard below)
- optionally, a **substituted tier-2 destination** for modes where "next to target" is wrong by construction (e.g. architecture's `advise` / `trade-off` modes write to the project's research/ADR location). When supplied, the substitute replaces tier 2's destination; tier 1 still wins and tiers 3/4 still apply on miss.


## Filename

`<feature-name>-<suffix>-<agent>-<YYYY-MM-DD>.md`

- On collision, append `-2`, `-3`, …
- `<agent>` is the executing agent's short name (`claude`, `codex`, etc.; fall back to `agent`)
- Date is the local date at write time, `date +%Y-%m-%d`

On completion, print the report's path **relative to the project root**.


## Directory Priority

Resolve in order; first match wins. Tiers 2–4 are skipped when an earlier tier matches.

1. **`--output-dir <path>`** (when the caller passes it) – explicit override. Validate up-front: the path must exist and be writable. In `AUTO_MODE`, fail with `BLOCKED: --output-dir <path> not writable`. In default mode, **print a warning** naming the unusable path and **fall through to the heuristic tiers** – the skill stays headless and the next-best location is loud-by-default because the resolved relative path is printed on completion. Do not auto-create deep paths – only the report file itself.

2. **Spec directory** – when the review centers on, lives in, or is adjacent to a spec/FIS/plan/PRD directory. Any of the following qualifies:
   - The reviewed artifact (or the requirements baseline, when one exists) **lives inside** a spec directory per the **Project Document Index**'s `Specs & Plans` row (default `docs/specs/<feature>/`)
   - The reviewed feature has an **associated spec directory** discoverable from the Project Document Index, the input arguments, or surrounding context (e.g. a PR description that references a FIS path, a recent commit message naming the spec, a sibling FIS in the same directory)
   - The requirements baseline path itself **is** the spec directory or a file inside one

3. **Current feature directory** – when no spec directory resolves, infer the active feature from `STATE.md` (per the Project Document Index `State` row, default `docs/STATE.md`). The destination is `dirname(row.FIS)` – i.e. the feature directory that holds the active FIS:
   - **Single in-progress row** → use its `dirname(FIS)`
   - **Multiple in-progress rows** → use a row's `dirname(FIS)` only when that directory is unambiguously this review's feature directory. The reliable signal is **directory ancestry**: `dirname(FIS)` is an ancestor of the review target's path. Skip the tier when no row's `dirname(FIS)` is an ancestor of the target, or when more than one row's directory is an ancestor (impossible in practice for a sane spec layout, but defined for safety). Do not rely on name-overlap or fuzzy matching – a wrong inference would land the report in someone else's feature directory.
   - **Skip** when `STATE.md` is missing, the **Active Stories** section is missing, or no rows are in progress

4. **Agent Temp** – `<agent-temp>/reviews/`, where `<agent-temp>` is the path from the Project Document Index `Agent Temp` row (default `.agent_temp/`). Always writable; the safe fallback.


## Source-Code Subdirectory Guard

Review reports must not litter source trees. This guard affects **tier 2 only** – tiers 3 and 4 already write to feature directories or agent-temp, and tier 1 is the caller asserting they actually want the path.

- **Doc target** (matches a doc-type row in the Project Document Index – spec/FIS/PRD/plan/ADR/design/wireframe – or lives inside such a directory): tier 2 may co-locate next to the target document.
- **Source-code target** (everything else: typical implementation roots – `src/`, `lib/`, `app/`, `pkg/`, `internal/`, `cmd/`, `Sources/`, `packages/<n>/src/`, framework- or language-specific equivalents – plus any ambiguous non-root subdirectory not classified as a doc target): tier 2 fires only via the spec-directory match above; otherwise fall through to tier 3, then tier 4.

When in doubt, classify as source-code – falling through is the safer default than dropping a report into an unfamiliar tree.


## Decision Trace

Include a one-line note in the report body naming which tier resolved the location and (when useful) why – e.g. "tier 2 spec-directory match", "tier 4 fallback (no spec or current-feature directory inferable)". Wording is freeform; the trace is diagnostic, not contractual, and downstream skills do not parse it.
