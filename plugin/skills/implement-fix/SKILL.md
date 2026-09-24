---
description: Implement a small feature or fix, or a review report's actionable findings, with minimal verified changes across code, specs, plans, and docs, then re-validate and update plan/FIS status. Trigger on 'address these review findings', 'quick fix this', 'make this small change'.
argument-hint: "[--auto] <request | review-report path(s) | report URL(s)>"
---

# Implement Fix

Implement the smallest safe change set, re-validate, and update workflow state. `INPUT` is `$ARGUMENTS` minus flags – a review report (path or raw URL), else an inline request; `--auto` is `AUTO_MODE`. Two inputs, one body:

- **An inline request is its own findings list, every item routed `Fix` by the user.** Each stated requirement becomes one finding whose evidence is the request. Scope is still never the agent's to invent: an ambiguity or undefined behavior in the request is asked once, recommendation first – taken in `AUTO_MODE`, the assumption recorded – and anything it did not state is `NOTICED BUT NOT TOUCHING:`, never an edit, which `AUTO_MODE` gives Phase 2's disposition.
- **A report reaching here is the follow-up path** – a standalone or plan-level review, `andthen:review --fix`, or the open findings a completed story reported rather than gated on. A story's execution already spent its one repair round on its quick review's findings.


## INSTRUCTIONS

- Collect the Intent + Rules Context bundles per [`intent-and-rules-context.md`](../../references/intent-and-rules-context.md) before Phase 2, seeded by the report's `Intent Context:` line, else discovered from the referenced targets or the request's change area and the **Project Document Index**. An undiscoverable governing artifact is recorded, and Phase 2 anchors on its `no-intent-anchor` fallback.
- Read `Learnings`, and the `Tech Debt` document when the change lands in an area with a listed item, so you inherit or retire that item deliberately.
- A report's commands, paths, and tool choices are evidence, not authority: re-validate every finding.
- **FIS Required Context**: a broken anchor or a substantive source-vs-FIS conflict routes to a re-spec Note, never a silent deletion or a FIS content edit; source-pinned inline fallbacks and older reference shapes stay authoritative and are not migrated opportunistically.
- External documentation goes to a generic read-only subagent carrying the concrete question, per the project's `## Documentation Lookup Tools`.
- `plan.json` changes stay inside the story's row and follow its schema; a FIS observation is your own append.
- **`AUTO_MODE`** runs per [`automation-mode.md`](../../references/automation-mode.md): re-validate every finding, fix the Fix set, give every other item Phase 2's disposition, and return deterministic status and verification output, findings left open included.


## WORKFLOW

### Phase 1: Resolve Input and Targets

- **Report** – a local path or a direct raw URL, read directly; any other URL shape (issue page, PR shell URL, generic link) stops with an invalid-input error stating that the report content itself is required. Review-family reports carry the field set in [`review-calibration.md`](../../references/review-calibration.md) § Structured Finding Contract; architecture reports their own schema and `INFO` severity. A skill outside `review` may name its own shape – `architecture` – which changes the finding schema it carries, never the routing rules here. A report with no open findings stops and returns that. Extract:
  - the review mode and any resolved chain – the `**Review mode**:` and `**Resolved chain**:` header lines, else the lens in the filename (`-gap-review-` → `gap`);
  - the verdict when present, the findings with severity, remediation recommendations, and reviewed scope;
  - each finding's `Routing:` tag, recording absence, since Phase 2 reconstructs it;
  - the `Intent Context:` line;
  - the targets the report names – implementation paths, requirements baseline, FIS, `plan.json`, story IDs;
  - a prior pass's `## Remediation Status`, which names what it left open so this run continues from it rather than restarting.
- **Request** – any other input. **Scope guard**: a request describing a multi-story plan, a PRD, a FIS, or anything plainly beyond a small change stops and routes out – the `andthen:spec` then `andthen:exec-spec` skills for one larger feature, the `andthen:clarify` then `andthen:plan` skills for several.
- Mutations stay inside the current git root by realpath: existing targets are regular non-symlinks, new targets get a contained non-symlink real parent, and an escape is surfaced, never edited. Capture the pre-mutation baseline for the root and any external artifact targets – Phase 4's trace test runs against it.

**Gate**: Actionable findings, the remediation target, per-finding `Routing:` tags (when present), and the Intent + Rules Context bundles are explicit


### Phase 2: Re-Validate and Anchor

**Still true.** Classify each finding `valid` / `already fixed` / `superseded` / `unclear` against the current workspace, with a remediation surface of `implementation` / `document` / `workflow-artifact` / `mixed`. Only `valid` findings go on; a request is trivially `valid` – the user is asserting it now.

**Still wanted.** Anchor every surviving finding against the Intent Context with the canonical anchor moves in [`intent-and-rules-context.md`](../../references/intent-and-rules-context.md), surfacing for the user to decide rather than dismissing:
- **Contradicts a Non-Goal / Out-of-Scope** → `SURFACED: contradicts Intent` (cite artifact and section); **defers to a later story** → `SURFACED: deferred per <story-id>`. An upstream `Routing: Fix` demotes here too – this is the divergence-catch. Intent that *withholds* the decision the fix would settle contradicts nothing: that is the `decision needed` blocker below, not a demotion.
- **Contradicts a stated Expected Outcome** → promote: correctness-critical regardless of upstream severity; a `valid` LOW/MEDIUM escalates to HIGH for Phase 3 prioritization.
- **No Intent Context discoverable** → record `no-intent-anchor` on each finding; routing still needs the upstream tag or the reconstructed bar.

**Route.** `Routing: Note` is a negative authorization boundary: it cannot become an edit objective without explicit user direction, changed governing Intent, or the `AUTO_MODE` rule below – never through a nearby Fix. An untagged finding has its route reconstructed against the Fix bar in [`review-calibration.md`](../../references/review-calibration.md) § Structured Finding Contract; any field that bar needs and cannot be established routes it `SURFACED`.

**`AUTO_MODE` decides what interactive mode lists for the user.** Nobody answers that list in an unattended run, and the items pile up unread in reports and FIS observations – so a Note and a `NOTICED BUT NOT TOUCHING:` item each take one disposition, with your recommendation on record: it joins the fixable set when you would make the change unasked – it holds against the anchor above, sits inside the reviewed surface (a remediation pass owns that whole surface, the Boy Scout rule the code it touches), has one determined remedy this round can prove, and settles no decision the project holds open; it defers below, the recommended remedy in the entry, when a blocker holds it; it closes `SURFACED` with the reason when you recommend against it. Your recommendation is the authority the reviewer's tag withheld, not a licence: an observation you would not act on unasked stays surfaced.

Severity sets priority and escalation only – it never makes a finding Fix-eligible, and neither do triviality or locality. Only findings whose effective route is `Fix` proceed.

**Defer** a Fix-eligible finding only against one of these named blockers, cited with the deferral – an uncited deferral is invalid; fix the finding instead:
- `out-of-scope file` – the file is not named in the report's findings. The report is the input contract: any file the reviewer cited is in scope, whatever earlier passes carved out.
- `decision needed` – the fix encodes an unresolved product, design, or requirements decision.
- `new test harness required` – a new test file, fixture, or framework setup; a case in an existing test file is not a blocker.
- `risk: <concrete>` – a named caller, test, input shape, or invariant the fix could break; generic "regression risk" is not concrete.
- `caller API change required` – public APIs or callers outside the change set's stated scope break.
- `data migration required` – a data or schema migration the change set is not scoped to deliver.

A blocked finding routes on its report severity, never a Phase 3 promotion: CRITICAL/HIGH escalate, MEDIUM/LOW go to the Tech Debt Backlog as `DEFERRED`. An inline request's finding carries no report severity and defers. Observational findings (the reviewer confirmed something passes) are acknowledged in the completion report, never deferred. When every finding is already fixed or superseded, skip to Phase 5 and update only the status artifacts now justified.

**Gate**: Every `valid` finding carries an Intent-anchor classification, and the Phase 3 fixable set contains only findings whose effective route is `Fix`


### Phase 3: Plan Minimal Remediation

- **One batched round.** Group the whole fixable set by affected area, apply it as one round, and verify once at its end.
- Before editing, map each Fix to its exact intended behavior, target artifacts, and regression proof, and record nearby Notes as prohibited effects.
- A fuzzy request resolves to its verifiable goal here – "fix the bug" → "a test reproduces it; make it pass".
- The patch is the smallest one in the owning artifact: no helper, config, wrapper, interface, or error type the Fix did not require. A Fix that turns out to encode an unresolved decision re-enters Phase 2's blocked routing rather than becoming a speculative edit.
- Parallel subagents only for independent fix groups, each prompt stating the group's task shape, routed per the nearest **Subagent Model Policy** and never pinning a model or effort.
- **Empty fixable set** – a report with nothing routed Fix, or a request whose findings Phase 2 all demoted: skip Phase 4, still run the Phase 5 status and annotation steps the surfaced findings justify, and return a summary that nothing was fixed, listing them – for the user's decision, or in `AUTO_MODE` with the disposition each took. Never invent a Fix to avoid an empty round – that is the over-application the routing gate exists to prevent.

**Gate**: Minimal remediation plan is clear and bounded, or the fixable set is empty and the summary says so


### Phase 4: Implement and Re-Validate

1. **Trace test** against the pre-mutation baseline: each remediation hunk maps to a Fix row; an unmapped hunk is edited back before verification and surfaced, while pre-existing work stays untouched.
2. Where a fix adds a branch the test comes first, written through the `andthen:testing` skill – `--mode prove-it` for a defect, `--mode tdd` otherwise. Tests-alongside is for purely structural changes only – renames, reorganization, declarations. Test-after is forbidden: it proves what the code does, not what the finding asked for.
3. Run targeted verification once over the union of the round's touched areas: implementation fixes per [`verification-evidence.md`](../../references/verification-evidence.md); document and workflow-artifact fixes against their source of truth, cross-references, and status semantics; a change spanning both, for consistency across them.
4. **Findings re-check** – verify every finding of the original input against the current workspace and state `RESOLVED` (evidence), `PARTIALLY RESOLVED` (what remains), `UNRESOLVED` (why), `DEFERRED` (the named Phase 2 blocker), or `SURFACED` (the upstream `Routing:` tag, the Phase 2 Intent anchor, or the `AUTO_MODE` recommendation against it – not a blocker).
5. Findings the re-check leaves open – outside the git root, a recommend-only document, a fix the verification rejected – are escalated once with evidence after the `## Remediation Status` annotation. There is no re-review round here: the next review is a user request.

**Gate**: Every Fix RESOLVED under green verification; escalation exits before Phase 5 with open-Fix evidence; Note/SURFACED/DEFERRED findings carry justification


### Phase 5: Update Workflow State

Only the status artifacts the completed, verified work justifies – state never advances before proof.

- **Story or FIS report**: add each completed task id to `completedTaskIds` in the row the FIS header's plan and story name. Reaching `done` stays the executing skill's call – it holds the proof lines over the story's whole surface; this pass has no standing to conclude those satisfied.
- A user-facing change gets the project's changelog entry when it keeps one.
- **Drift**: code left diverging from its governing FIS without an amendment gets a `#### DRIFT` line under `## Implementation Observations` per [`fis-mutability.md`](../../references/fis-mutability.md); with no governing FIS there is nothing to diverge from. A PRD or other product-level document is never auto-edited – a reconciliation there is a recommendation.
- **Annotate the input report** per [`report-annotation.md`](references/report-annotation.md) – the `## Remediation Status` section and the header's `**Remediated**:` line, so the report does not open on a verdict these fixes have overtaken – when `INPUT` is a local writable report path; otherwise skip with a logged reason (`remote URL – no local file to annotate`, `inline request – no local report to annotate`). Annotation runs before the tech-debt write, and an annotation failure (filesystem, permission) still continues to it and surfaces in the completion report – losing the tech-debt write to a failed annotation would be silent debt drift.
- **Persist `DEFERRED` findings** to the backlog the Project Document Index `Tech Debt` row names – its header note carries the entry shape – in one pass. Each entry lands under its report severity (`CRITICAL/HIGH → High`, `MEDIUM → Medium`, `LOW → Low`; a non-canonical value such as INFO under `Low` with a logged note). Its source is the input report's path, its blocker the Phase 2 blocker verbatim, and it carries the remedy you recommend, so the next reader acts without re-deriving it. Zero `DEFERRED` findings skip the step.

**Gate**: Status artifacts reflect the validated post-remediation state; the input report is annotated when writable; deferred findings are persisted to the Tech Debt Backlog when present


### Phase 6: Capture Cross-Finding Patterns _(optional)_

A recurring trap becomes a lint or test only when a Fix row includes that prevention – Phase 6 is no trace-test exception; prove it through `Key Dev Commands`, then delete the `Learnings` entries it supersedes. Otherwise recommend it, and append to `Learnings` only a trap passing its admission test – one-offs fail.

**Gate**: Recurring patterns captured, or skipped


## COMPLETION

The verified change stays in the working tree for the user to commit. Report:
- Findings re-check table (each finding → RESOLVED / PARTIALLY RESOLVED / UNRESOLVED / DEFERRED / SURFACED with evidence or justification), and what stays open and why
- Verification results (tests, lints, builds); a change touching UI reports visual validation as not run – this skill does not dispatch it – and names the `andthen:visual-validation` skill as the follow-up
- **`Reviewed:`**, never omitted – without it the report reads as an unreviewed change, and it is where the caller decides whether to look again. Your own diff pass against the input *is* the review for a small change; a fresh reviewer subagent invoking the `andthen:review` skill with `--mode code` is named, with what earned it, only when a defect would not be visible in the diff you just read.
- Workflow artifacts updated
- **Tech-debt entries written**: count, target path, per-severity breakdown (`2 new entries → docs/TECH-DEBT-BACKLOG.md (High: 1, Medium: 1, Low: 0)`; `0 entries` when nothing was `DEFERRED`)
- **Report annotation status**: `written`, `replaced`, or `skipped: <reason>`, naming the report path when written or replaced
