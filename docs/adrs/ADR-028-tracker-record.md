# ADR-028: Keep a feature's record in the issue tracker, opt-in per project

## Status
Accepted. Recorded 2026-10-06.

Extends ADR-026: `ship` gains the final tracker refresh. It reverses one recorded statement: the Cookbook's published child issue no longer carries "PRD anchors, a commit-pinned FIS link" (Working in a team). It narrows others to `Record: repo`: `docs/ARCHITECTURE.md`'s "`prd.md` ... is the surviving product record", and the Cookbook's "`prd.md` outlives the bundle", "`prd.md` stays", and "The pipeline does not change per tracker". All are rewritten when this lands. "Never a second source of truth" still holds, because the bundle stays the truth while a plan runs. The Still Current notes on a nullable `prd` and on scripts never parsing a FIS hold unchanged.

*Amended 2026-10-06: the projection moves from `tracker.py` into the `tracker` skill's prose, and the script goes. It had grown to 377 lines and 448 test lines of bookkeeping the agent does by reading, namely marker search, numbering in two passes, sealing, and a hash per section, and every defect still open after review sat in that code. The parent's numbered `## Stories` checklist now names the children, and a search runs only for a story it does not link yet. A closed issue is the shipped record, so the merge's closing links replace `--seal`. `publish` previews what each write changes and asks once, which replaces the hash. Issues an earlier release candidate published are not found again. The `ops` script and `wire.py` were retired for prose the same way.*

## Context

**Some teams want no requirements documents in the repo.** Their PRDs and stories live in GitHub issues, and the issues plus the PR are the lasting record. AndThen supports half of that today. `plan <issue-url>` reads an issue as its requirements, the gap lens reads that URL as its baseline, and `ship` writes the PR body and deletes `plan.json` and the FIS files before the merge (ADR-026). Three gaps remain:

- **The PRD never reaches the issue.** `clarify` always writes `prd.md` under Specs & Plans, even when its input is an issue, and `ship` keeps that file. A project that gitignores the specs folder keeps the PRD only as the summary `ship` writes into the PR body.
- **Published issues point at files that disappear.** `tracker publish` gives each child issue the story's scope plus `PRD: <path>` and `FIS: <path>@<sha>` lines (`tracker.py`, `child_payload`). `ship` deletes the FIS, and under the ADR-026 amendment of 2026-10-06 no branch commit is a link target, because a squash merge leaves it out of the base branch. A teammate or a later reader of the issue gets no intent, outcomes, or acceptance. `tracker triage` already bars this for its own text: its Durability rule says published bodies name behavior and interfaces, "never file paths, line numbers, or code snippets".
- **The outcome lens needs a PRD file.** Without one "the pass is unavailable" (`lens-outcome.md` § Baseline), while the gap lens falls back to the tracker item a plan's `sourceRefs` cite.

## Decision

**A project chooses where a feature's requirements record lives after the merge: in the repo, as today, or in the issue tracker. While a plan runs, its bundle (`prd.md`, `plan.json`, the FIS files) committed on the feature branch stays the source of truth, and sync stays one way, bundle to tracker.**

- **The setting.** A `Record: repo | tracker` line in the `Issue Tracker` document. A missing line means `repo`, so existing projects keep today's behavior. `Backend: none` implies `repo`.
- **The PRD's home in `tracker` mode is the source issue.** The PRD goes into the issue body below a marker, refreshed in place, with the original request kept untouched above it, as `tracker triage` already appends its `## Agent Brief`. When the work did not start from an issue, the first write creates one, and that issue becomes the plan's parent issue.
- **`clarify` in `tracker` mode** writes `prd.md` as today, because its self-review reads the file, then after one confirmation writes the PRD into the source issue, or creates one. Its closing note says the local `prd.md` is a working copy and optional to keep, since on `main` it may stay uncommitted. Amending a PRD that lives in an issue is the same round trip: `clarify` on the issue copies its PRD section into `prd.md`, amends it, and writes it back after one confirmation.
- **`plan` on an issue that carries a PRD section copies it into the bundle as `prd.md`.** The plan's `prd` names that file and the issue URL stays in `sourceRefs`, so review and `ship` read one file. During the plan, amendments go to the bundle's `prd.md`, and the next publish or `ship` carries them to the issue.
- **One issue shape in both modes.** The parent issue holds the PRD. Each child issue holds its story's scope, Intent, Expected Outcomes, and Acceptance Scenarios without their Proof lines, plus its dependencies as issue links. Once the story is done, the child also carries its verification summary, and the PR's closing link ties it to the PR. The mode decides only whether `clarify` writes the issue and whether `ship` deletes `prd.md`.
- **No file path or commit reference in any issue.** The Durability rule moves from `tracker triage` to every tracker write. The agent writes every body: the story sections from the FIS, the rest from `plan.json` and `prd.md`. A hidden line opening each projected part names its source's path, as identity only.
- **`ship` writes the final record under `Record: tracker`.** Inside its one confirmation before push and PR, it publishes the final issues from the bundle, and the PR's closing links close them at merge. A closed issue is the shipped record, which `publish` never edits, so a later plan gets a new parent issue that links it. It then deletes the bundle, `prd.md` included, before the push. When nothing was published, `prd.md` stays, because it is then the only copy, and with no push the whole bundle stays for the next `ship` run. Under `Record: repo` the issues stay a projection the team refreshes with `tracker publish`, which also serves teams that want the breakdown visible while the plan runs.
- **Edits made in the issue are shown, and nothing more.** `publish` shows what each write changes and asks once before the first write, so an edit made in the tracker is seen before it is replaced and can be taken into `prd.md` through `clarify` first. `ship` puts that preview in its one confirmation, and an unattended run reports what each update replaced. There is no history and no merge.
- **The outcome lens falls back to the tracker item** when the plan has no PRD file, the way the gap lens does.

## Consequences

**Easier**
- A team can keep its requirements entirely in the tracker: `clarify` writes the issue, `plan` picks it up later from the URL, and after the merge the issues and the PR hold intent, outcomes, acceptance, and proof with no repo file behind them.
- A child issue can be read on its own. A teammate claiming a story, or anyone reading it after the merge, sees what the story is for and how it was accepted.
- The outcome lens runs on issue-sourced plans.

**Harder**
- During a plan the PRD exists twice, in the bundle and in the issue. A human edit to the issue shows only in the next publish's preview.
- `clarify`, `plan`, `ship`, and `tracker publish` each gain a tracker step, and `ship`'s one confirmation now also covers the issue writes.
- Issues an earlier release candidate published are not found again: a re-publish creates new ones, and nothing migrates the old.
- No unit test covers the projection, because no script is left to test. A malformed plan surfaces when the agent reads it.

**Unchanged**
- `plan.json` is the agent's truth while the plan runs, and a reprioritization made in the tracker is a re-plan.
- `prd` stays a nullable repo path with no URL form, and a plan from an issue without a PRD section keeps `prd: null`.
- Tracker setup stays first-use (`Backend:` and now `Record:` are lines in one document).

## Alternatives Considered

1. **Tracker record whenever a backend is configured, with no setting.** Rejected: such a project could no longer keep PRDs in the repo.
2. **Both, always: refresh the issues and keep `prd.md`.** Rejected: the requirements still persist in the repo, which is what these teams want to avoid.
3. **A new parent issue for the PRD**, linking and closing the source issue. Rejected: the record splits across two issues.
4. **The PRD as a comment on the source issue.** Rejected: the current PRD ends up buried in the thread.
5. **`plan` reads the issue each time instead of copying it.** Rejected: the PRD is never on the branch, and every step that needs it must reach the tracker.
6. **`clarify` writes the issue only, with no local `prd.md`.** Rejected: its self-review and amendments would read and write through the tracker.
7. **Overwrite edits made in the issue.** Rejected: a human edit vanishes from the body without notice. **Post each refresh as a comment** was rejected for the same burial as 4.
8. **Remove the marker at `ship` instead of sealing it.** Rejected: tooling can no longer identify a shipped record. Moot since the amendment: the marker stays, and a closed issue is the shipped record.
9. **Write the issues only at `ship`, or only through `tracker publish`.** Rejected: the first stops teams claiming stories mid-plan, which the Cookbook's team recipe relies on; the second leaves the final refresh to memory.
10. **Floor option: extend `tracker publish` only**, replacing the `PRD:` and `FIS:` lines with the story sections. Rejected: the PRD still never reaches the issue and `prd.md` still persists in the repo, so the requirement is unmet. Its body change is part of the Decision.
11. **Keep the projection in `tracker.py`**, the decision until the amendment. Rejected: see the amendment.

## Implementation Notes

Implemented directly, not through a plan, because the work is skill text. The details left open here settled in it and its amendment:

- A body's projected part opens with `<!-- andthen-projection <source> -->`, where the source is the PRD's path, else the plan's. A child's line is `<!-- andthen-projection <id> <source> -->`, led by the story id so a search for the parent's line never matches it. The token holds no `andthen:`, so the loose-skill installer's prefix rewrite leaves it the same on every install. Text above the line is kept.
- The parent is the first open issue among the one the PRD's header names, a tracker item the plan cites, and the one whose line names the source, else a new one that links a closed candidate. Its title is the PRD's heading, else `Plan: <directory name>`. Its `## Stories` checklist links each child by number, which is how a re-run finds them, and each child joins it as soon as it is created. A story the checklist does not link is first searched by its child's line, so a run that stopped between creating a child and the checklist write never duplicates it.
- A plan without a PRD writes only its checklist, so no plan summary is later read back as a PRD. A `prd.md` alone keeps the checklist already in its issue.
- Issues are created parent first and stories in plan order, then each body still missing an issue number it names is edited.
- A found parent keeps its title, so `publish` needs no title operation.
- `clarify` and `ship` invoke the `tracker` skill's `publish`, so only `tracker` writes to the tracker. Its preview is their one question.
- `ship` refreshes the issues only under `Record: tracker` (review finding, accepted by the maintainer 2026-10-06): under `Record: repo` nothing tells `ship` whether a plan was ever published, and creating issues there would add a tracker record that mode does not keep.
- The installer's `SKILL_NS` rewrite and its `<skill-dir>` baking served only the script, and go with it.

Surfaces it touches:

1. `tracker`: `SKILL.md` (the Durability rule for every write, the projection in prose, the preview, the source issue as parent), `references/triage.md` (its Durability rule now cites the skill-level one). `scripts/tracker.py` and its tests are deleted.
2. `project-document-templates.md`: the `Record:` line in `ISSUE-TRACKER.md`.
3. `clarify`: the `tracker`-mode issue write, reading a PRD section from an issue for amendment, and the closing note.
4. `plan`: copying an issue's PRD section into the bundle.
5. `review`: the outcome lens fallback in `lens-outcome.md`.
6. `ship`: final issue bodies before the deletion, their preview in the one confirmation, a closing link per issue, and `prd.md` deleted under `Record: tracker`.
7. Records: `docs/ARCHITECTURE.md`, the Cookbook's team section, its tables, and the worked example's close-out, `README.md`, `plugin/README.md`, `CHANGELOG.md`, and `docs/UBIQUITOUS_LANGUAGE.md`, whose PRD row calls `prd.md` "the record that survives the merge".
8. With the amendment: `scripts/install-skills.py` and its tests, the CI workflow's script steps, `docs/PRODUCT.md`'s Runtime fact, and `docs/TESTING-STRATEGY.md`.

## Project Compliance

- **Standing technical non-goals.** No hosted control plane and no central workflow database: workflow state stays in `plan.json`, and the tracker holds a record, not state.
- **Lean.** One setting, one hidden line per issue, and a closed issue as the record. No script, no history, no merge, no two-way sync.
- **Still Current notes.** A nullable `prd` path with no URL form holds, because `plan` copies an issue's PRD into a file. No script parses a FIS, because no script is left. Tracker setup stays first-use.
- **ADR-026.** `ship` keeps its one confirmation before anything leaves the machine; the issue writes join it.

## Reopens

- If the preview buries an edit a team relied on, or asking on every publish proves a burden.
- If a re-publish creates a duplicate issue on a recorded run.
- If a backend in the Operation Table cannot edit an issue body in place, which the PRD section and the checklist both need.

## References

- This session's interview with the maintainer, 2026-10-06.
- ADR-026 and its amendment of 2026-10-06.
- `plugin/skills/tracker/references/triage.md` (Durability rule) and `references/agent-brief.md` (the appended-section precedent).
- `plugin/skills/tracker/SKILL.md`, `plugin/skills/review/references/lens-outcome.md`, `lens-gap.md`.
- `docs/DECISIONS.md` Still Current: the `ops` script's and `wire.py`'s retirement for prose.
