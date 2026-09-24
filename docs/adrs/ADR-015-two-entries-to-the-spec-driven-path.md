# ADR-015: Two entries to the spec-driven path

**Status:** Accepted

**Recorded:** 2026-09-14

**Amends:** [ADR-013](ADR-013-scripts-read-json-agents-read-markdown.md).

## Context

ADR-013 made every FIS a plan story and ADR-014 made `exec-plan` N × `exec-spec`, so the framework already had one execution shape. The entries to it had not followed: `spec` still took a description, file, or issue and wrote a one-story `plan.json` beside its FIS, while `prd → plan` took the same inputs for several stories, and the user picked between them by size. Requirements had two skills – `clarify` interviewing into `intent.md`, `prd` synthesising `prd.md` – which the README already called a pipeline, not a choice, and the user picked between them by how complete the input looked. The docs presented that as three paths plus a quick one. Architecture trade-offs and UI design were drawn as pre-work before requirements existed, although `plan`'s preflight already sends a fork to `architecture --mode trade-off` once the PRD is on the table.

On 2026-09-14 the maintainer decided the collapse below, with three bounds: `plan` requires a PRD as a source, not as a document `clarify` must have written; `spec → exec-spec` stays as the quick track for one story; `prd: null` stays for the one-story plan `spec` writes.

## Decision

*Amended 2026-09-15, see `docs/DECISIONS.md` § Still Current: `--auto` retires and `--brief` writes `intent.md`. Amended 2026-09-24 ("Where work starts: two questions, not one"): `spec` takes a PRD too, so story count alone picks `spec` or `plan`.*

**`clarify` is the requirements skill and writes the PRD.** It absorbs `prd`: input resolution and amendment, the Discovery & Ideation interview, the PRD template and its validation, the fresh-context doc self-review, and the Product non-goals rule. An attended run interviews at least once – a complete brief gets one short confirmation round; `--auto` synthesises with recorded assumptions and the Vague-Input Bailout. Feature scope writes `<specs-root>/<feature>/prd.md` (`issue-{n}-<slug>/` for a tracker item); product scope writes `PRODUCT.md` as before. `intent.md` is no longer an output – a hand-written intake stays an input that `clarify` folds into the PRD. It ends on the `plan` command and recommends `architecture --mode trade-off` when the PRD leaves a design fork and `ui-ux-design` when UI is in scope with no design system or wireframes. It needs nothing downstream: a stakeholder refining requirements into a document is a complete use. `prd` retires.

**`plan` is the entry for PRD-backed work and always has a PRD source**: a directory holding `prd.md` or that file's path, a requirements file, or a tracker item URL. Inline text is not a PRD and redirects to `clarify`. Output lands beside `prd.md`, otherwise under the Specs & Plans root as `clarify` names its directories. `prd` in `plan.json` is the in-repo source path, or `null` for a tracker item; `sourceRefs` cite the source either way. One story is a normal outcome, and story breakdown stays here – a PRD's user stories are requirements, not implementation stories.

**`spec` keeps the quick track.** `spec <description | file | issue URL | brief>` writes one FIS plus a one-story `plan.json` with `prd: null` beside it – a single story earns no PRD – and `exec-spec` runs it. It also authors one plan story under `plan --batch` and re-authors a `blocked` or `spec-ready` story. `plan` is for several stories, or for one when the PRD is wanted as the record.

`exec-plan` and `exec-spec` are unchanged; the user runs `exec-spec` per story by hand or lets `exec-plan` run them.

## Rationale

`plan` decides the story count for anything with a PRD behind it, and `spec` stays for the story that has none; one requirements skill moves the interview-or-synthesise decision from a README table into the skill that knows the input. A single feature now leaves a requirements record – the `prd.md` or the issue it came from – where before its only requirements lived in a FIS deleted at close-out, and its FIS cites source anchors instead of restating them. `prd` stays nullable because a URL branch in the schema and validator buys nothing `sourceRefs` do not already carry. Trade-offs and UI design sit after the PRD because they answer it.

Rejected: a mandatory `prd.md` for every feature (ceremony for issue-sourced work the issue already specifies); naming the merged skill `prd` (`clarify` is the name users know, and the interview is its value); retiring `spec`'s standalone entry (the maintainer kept it on 2026-09-14: the quick track must stay two commands with no PRD).

## Consequences

`prd` retires with no alias; `clarify` gains `--auto` and loses Interactive-by-Contract as an absolute – it holds for attended runs. `spec` is unchanged in shape; its `prd` redirect points at `clarify`. `now-what`, the `backlog-triage` Agent Brief, the docs, the overview figure, the glossary, and the migration table follow. The 1.0 skill count drops to 18.

Reopens if the two entries drift apart in bundle shape, or if `clarify --auto` proves too thin to stand in for the retired `prd` synthesis.

## Evidence

- Current contract: [`plugin/skills/clarify/SKILL.md`](../../plugin/skills/clarify/SKILL.md), [`plugin/skills/plan/SKILL.md`](../../plugin/skills/plan/SKILL.md), [`plugin/skills/spec/SKILL.md`](../../plugin/skills/spec/SKILL.md).
