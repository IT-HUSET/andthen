---
description: Ship the current branch – land the plan's FIS Implementation Observations worth keeping, delete or keep its bundle, commit, then push and open the pull request on one ask. Trigger on 'ship it', 'open the PR', 'close out the plan'.
argument-hint: "[--auto] [plan.json path] [notes for the pull request]"
---

# Ship

Close out the current branch and open its pull or merge request.
A branch carrying a plan bundle – `plan.json` and the FIS files beside it – first lands what its FIS files learned, then deletes the bundle unless the user keeps it, because a plan's specs govern one branch and go stale once it merges.

## Input

`$ARGUMENTS` minus flags is optional: a `plan.json` path, and anything the pull request should target or say.

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.
- A branch with a plan bundle: read [`plan-schema.md`](../../references/plan-schema.md), whose § Shipping says when the plan is ready.

`Learnings`, `Decisions`, `Issue Tracker`, and `Visual Validation` are **Project Document Index** entries.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Publishing waits for a yes.**
  Commits run unasked, because the branch history keeps them.
  A push and a pull request leave the machine, so they wait for the user's yes.
- **Commit only the branch's own work.**
  Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged.
  A change you cannot tie to the branch stays uncommitted, because it may be another session's work in progress.

## Workflow

### 1. Check for open work

Open work is what keeps a plan from being ready under § Shipping, and on any branch a CRITICAL or HIGH finding the latest review of its work leaves open.
Name it and ask once whether to ship anyway, recommendation first.
While the plan is not ready, the same question asks whether to keep the bundle, recommending keeping it, because its remaining stories and reviews still read it.

**Gate**: nothing open, or the user's answer.

### 2. Land the observations

Only with a plan bundle step 1 did not keep, because its specs go stale once the plan ships.
Read every FIS's `## Implementation Observations`.
- Write each trap as one `Learnings` bullet under its fitting topic, admitted against its header note.
- Recommend the rest worth keeping in the output, because decisions and upstream documents stay the user's.
- A design change no ADR or `Decisions` entry records yet becomes a recommended `Decisions` line, or a run of the `andthen:decide` skill where alternatives are still open.

**Gate**: every observation written, recommended, or judged not worth keeping.

### 3. Write the pull request

Write it for a reviewer deciding whether to merge.
The body is where the intent and proof outlive the branch, because the bundle is usually deleted and the review report usually never committed.
A project's pull request template or named PR process sets the layout, and this content fills it.
Put what the merge decision needs first and fold per-story detail below it, because a body the reviewer must scroll goes unread.
- **Intent and outcomes.**
  Take them from each FIS's Intent and Expected Outcomes and from the plan's source: the file its `prd` names, else what its stories' `sourceRefs` cite.
  Without a plan, take them from the commits and the request.
  Link a cited tracker item so the merge closes it, unless the plan is not ready, because its work is then unfinished.
- **Proof** of each outcome, from each story's `verified.summary` in `plan.json` and the latest review report's verdict.
- **Door and blast radius.**
  Say whether the change is a one-way or two-way door and what its blast radius is, linking the ADR that settled a one-way door.
  Where reverting the merge would not undo the change, say what does and what no revert restores.
- **Where to read closely**, because no check covers it or a mistake there costs most:
  - the files where an error does the most harm;
  - each choice no check can judge, such as a pattern others will copy or a call on scope;
  - each check, lens, or surface that was skipped, unavailable, or marked `not reviewed`;
  - all work after the latest review report's `**Revision**`, committed or still in the tree, except this run's `Learnings` bullets and bundle commit.
    Say which of it the report's `**Remediated**:` line marks as fixes.
    A `-dirty` Revision cannot show which work the review read, so say so.
    With no report, say no review ran.
- **What stays open**: what the change knowingly leaves open, such as a finding or story the user shipped past.
- **Pictures**: where a flow, structure, or state change reads faster as a picture, add the smallest view that makes the point.
  Use a Mermaid diagram where the host renders one, an SVG, or a pseudocode or tree block.

**Gate**: a title, and a body that states the intent, the outcomes, their proof, the door and blast radius, and where to read closely before any per-story detail.

### 4. Commit

- Outside `--auto`, when the current branch is the remote's default branch, ask once whether to start a feature branch first, because commits land on the current branch and the pull request opens from it.
  Recommend starting it the way the project's written convention for starting work says, else as `<type>/<slug>`.
- Commit the fixes left in the working tree.
- With a plan bundle, commit the landed entries, and leave the bundle to step 5's answer.
  A bundle file git does not track has no copy in history and never reaches the merge, so never delete it and ask nothing about it.

**Gate**: the branch's own work committed, and the tracked bundle untouched.

### 5. Publish

- Show the base branch, the commits leaving, the title, and the body.
- Under `Record: tracker` with a plan bundle, invoke the `andthen:tracker` skill with `publish <plan.json> --dry-run` before asking.
  The question below also covers its preview and a closing link in the body for each issue the merge finishes, because the merge closes them into the record.
  While the plan is not ready, those are only the open issues of stories `done` or `skipped`, so the parent and the unfinished stories stay open for a later ship.
- Ask once whether to push and open it, and end the turn on the question.
  For a ready plan's tracked bundle, the same question asks whether to delete it, recommending deletion.
  With no remote, ask only about the bundle, except under `Record: tracker`, where it waits for a publish.
  Offer screenshots or a recording for a visible UI change the request said nothing about.
- On a yes under `Record: tracker`, invoke the `andthen:tracker` skill with `publish <plan.json>`, and add the closing links from the issues it reports.
- On a delete, commit the deletion before the push: `plan.json`, its FIS files, and any `intent.md` beside them go, and the requirements file its `prd` names stays.
  A `prd.md` that stays gains a `> **Shipped**: <UTC ISO-8601 minute>` header line in the same commit, so later runs read it as a record.
  Under `Record: tracker` in the `Issue Tracker` document, that file goes too once the issues are published, because they then carry the record.
  Without a publish under `Record: tracker`, the bundle stays for the next run, because the issue bodies are written from it.
- With the deletion, repoint each committed link into a deleted file at what survives it, such as the requirements file, its issue, or an ADR, because a dead link fails silently.
  A branch commit is no such target, because a squash merge leaves it out of the base branch.
- When a ready plan's bundle stays, kept or untracked, write its `shipped` marker unless the user declines the push, so later runs read the plan as a record.
  A tracked one is committed before any push, then once the pull request opens its `pr` is set, committed, and pushed.
  An untracked one is written once the pull request opens, else at the run's end with `pr` null, and left uncommitted.
- Before the push, capture the screenshots or recording the request asked for or the answer took up, per the `Visual Validation` document.
  Attach each image through an upload the host accepts, else list it for the user to attach.
- Under `--auto`, stop before anything leaves the machine.

**Gate**: no push before any bundle deletion or tracked `shipped` marker is committed, and the pull request's URL, or its title, body, and the commands still to run to open it.

## Output

Report:

- each `Learnings` bullet written, each recommendation, and each observation judged not worth keeping, with its reason;
- the commits made, and the bundle files deleted or the bundle kept, with the `ASSUMPTION:` line of an unattended run;
- each change left uncommitted, each file left in the bundle's directory, because a later `now-what` reads it as work in progress once no record is left beside it, and whether the plan was marked `shipped`;
- the pull request's URL, each issue published, and each image left for the user to attach, or its title, body, and the commands still to run.
