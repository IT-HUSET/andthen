---
description: Ship the current branch – land the plan's FIS Implementation Observations worth keeping, delete or keep its bundle and design folders, commit, then push and open the pull request. Trigger on 'ship it', 'open the PR', 'close out the plan'.
argument-hint: "[--auto] [plan.json path] [notes for the pull request]"
---

# Ship

Close out the current branch and open its pull or merge request.
A branch carrying a plan bundle – `plan.json` and the FIS files beside it – first lands what its FIS files learned, then deletes the bundle unless the user keeps it, because a plan's specs govern one branch and go stale once it merges.

## Input

`$ARGUMENTS` minus flags is optional: a `plan.json` path, and anything the pull request should target or say.

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.
- A branch with a plan bundle: read [`plan-schema.md`](../../references/plan-schema.md), whose § Shipping says when the plan is ready.

`Learnings`, `Decisions`, `Issue Tracker`, `Visual Validation`, `Wireframes`, `Mockups`, and `Agent Temp` are **Project Document Index** entries.
`Record:` is a line of the `Issue Tracker` document, `repo` without one.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Publishing needs the user's yes.**
  `--auto` supplies it for pushing the branch, refreshing a published plan's issues, publishing under `Record: tracker`, and opening the pull request with its images.
- **Commit per [`verification-evidence.md`](../../references/verification-evidence.md) § The commit rule.**
  Its feature-branch ask joins step 1's question, because step 2 is the first edit.
  Under `--auto` on the remote's default branch, start a feature branch before step 2 using the project's branch-start convention, else `<type>/<slug>`, so the push can open a pull request from it.
  This skill runs no checks, so in place of its green-work bullet it commits what step 1's gate cleared, and step 3's proof says what was verified.
  A change you cannot tie to the branch stays uncommitted, because it may be another session's work in progress.

## Workflow

### 1. Check for open work

The pull request's **base** is the first of:

- the branch the request names;
- this branch's open pull request's base;
- the one other remote branch holding the plan's `plan.json` that heads no pull request, open or merged, into a branch holding it;
- the remote's default branch.

Where two or more branches fit the third, ask which, or unattended end on `BLOCKED:` naming them, because the wrong base ships the wrong stories.
The **covered** stories are this `plan.json`'s stories whose rows the branch's own commits changed, and every story when the base has no `plan.json`, because each story the base holds had its own pull request.

Open work is:

- a covered story neither `done` nor `skipped`, unless every covered story is `pending`;
- once every story is `done` or `skipped`, on a pull request into the remote's default branch or a base with no `plan.json`, what else keeps the plan from ready under § Shipping;
- on any branch, a CRITICAL or HIGH finding the latest review of its work leaves open.

Name it and ask once whether to ship anyway, recommending finishing first, and unattended end on `BLOCKED:` naming it.
A plan that is not ready keeps its bundle, because its remaining stories and reviews still read it.
Where this step asks, the same question offers deleting it, recommending keeping it.
The commit rule's feature-branch ask joins that question, or is the question when nothing is open.

**Gate**: nothing open and no feature-branch ask, or the user's answer.

### 2. Land the observations

Only with a ready plan's bundle, or one step 1's answer deletes.
Read every FIS's `## Implementation Observations`, those in `superseded/` included.
- Write each trap as one `Learnings` bullet under its fitting topic, admitted against its header note.
- Recommend the rest worth keeping in the output, because decisions and upstream documents stay the user's.
- A design change no ADR or `Decisions` entry records yet becomes a recommended `Decisions` line, or a run of the `andthen:decide` skill where alternatives are still open.

**Gate**: every observation written, recommended, or judged not worth keeping.

### 3. Write the pull request

With a plan bundle and either an `Issue Tracker` document whose `Backend:` is not `none` or, without one, a GitHub remote, read the plan's parent issue read-only, through that document's operations or `gh`; otherwise say nothing about the tracker.
The parent is the open issue the PRD's header or the plan's `sourceRefs` name, else the open one holding the plan's parent `andthen-projection` line, as the `andthen:tracker` skill defines it.
The plan is **published** when the parent carries a `## Stories` checklist, which links the children.

Write the pull request for a reviewer deciding whether to merge the covered stories.
The body is where the intent and proof outlive the branch, because the bundle is usually deleted and the review report usually never committed.
A project's pull request template or named PR process sets the layout, and this content fills it.
Put what the merge decision needs first, because a body the reviewer must scroll goes unread.
Collapse per-story detail in a `<details>` block where the host renders one.
Give each `<details>` block a blank line after `</summary>`, because without it the host shows the markdown inside as raw text.
- **Intent and outcomes.**
  Take them from each FIS's Intent and Expected Outcomes and from the plan's source: the file its `prd` names, else what its stories' `sourceRefs` cite.
  Without a plan, take them from the commits and the request.
  Add a closing link for each issue the merge finishes: the parent once the plan is ready, and the child of each covered story `done` or `skipped`; without a plan, the tracker item the request cites.
  A link closes only from a pull request into the remote's default branch, so for another base the step 5 question and the output name the issues that stay open for the user to close after the merge.
- **Proof** of each outcome, from each story's `verified.summary` in `plan.json`, the latest `Reviewed:` line in its FIS, and the latest review report's verdict.
  Where that report carries a `**Remediated**:` line, say its verdict predates the fixes, because a FAIL alone reads as findings still open.
- **Door and blast radius.**
  Say whether the change is a one-way or two-way door and what its blast radius is, linking the ADR that settled a one-way door.
  Where reverting the merge would not undo the change, say what does and what no revert restores.
- **Where to read closely**, because no check covers it or a mistake there costs most:
  - the files where an error does the most harm;
  - each choice no check can judge that the `## Decided without asking` section does not list, such as a pattern others will copy or a call on scope;
  - each check, lens, or surface that was skipped, unavailable, or marked `not reviewed`;
  - all work after the latest review report's `**Revision**`, committed or still in the tree, except this run's `Learnings` bullets and bundle commit.
    Say which of it the report's `**Remediated**:` line marks as fixes.
    A `-dirty` Revision cannot show which work the review read, so say so.
    With no report, say so.
- **What stays open**: what the change knowingly leaves open, such as a finding or story the user shipped past.
- **Decided without asking**: each `ASSUMPTION:` line, and each Drift Note or Discovered Requirement Interpretation whose reading a run chose, because the reviewer answers for them.
  Read them from the covered stories' FIS files, the branch's review reports, and the lines the branch's commits added.
  [`pr-section.md`](references/pr-section.md) fixes their section, which stays visible, outside any `<details>` block.
- **Pictures**: where a flow, structure, or state change reads faster as a picture, add the smallest view that makes the point.
  Draw it as a Mermaid diagram where the host renders one, else as a pseudocode or tree block, because both stay text in the body.
  Draw an SVG only for what Mermaid cannot lay out legibly, and reference it in the body by relative path for step 5 to attach:
  - write it under the `Agent Temp` location, so no commit takes it;
  - give it an opaque background, so it reads in either theme;
  - render it and look at it before using it.
- **Ship summary**: `pr-section.md` also fixes the section that ends the body, filled from the facts above, because a viewer parses it to join the pull request to its requirements, proof, and reviews.

**Gate**: a title, and a body that states the intent, outcomes, proof, door and blast radius, where to read closely, and what was decided without asking before any per-story detail, then ends on the Ship summary.

### 4. Commit

- Commit the fixes left in the working tree.
- With a plan bundle, commit the landed entries, and leave the bundle to step 5's answer.
  Where every covered story is `pending`, the pull request carries the bundle and the requirements file its `prd` names, so commit them.
  Where git ignores them, end the run saying there is nothing to open a pull request from.
  With a covered story past `pending`, an untracked bundle file never reaches the merge, so never delete it or ask about it.

**Gate**: the branch's own work committed, the bundle with it where every covered story is `pending`, and no tracked bundle file deleted.

### 5. Publish

- Show the base branch, the commits leaving, the title, and the body.
- Where step 3's read succeeded, invoke the `andthen:tracker` skill with `publish <plan.json> --dry-run` before asking, and the question below covers its preview, in each case:
  - the plan is published;
  - the run is under `Record: tracker`;
  - the plan is unpublished under `Record: repo` with every story `pending` and an `Issue Tracker` document or a cited tracker item.
    This case is an offer with no recommendation, and unattended it publishes nothing and names the command.
- Pass `--only` naming each covered story, and `prd` where the branch's commits changed the PRD, leaving out any the base changed after the branch left it, because the merge, not this branch, holds its current text.
  Pass none when the base has no `plan.json` or the plan is ready or unpublished, so a first or final publish is whole.
- Outside `--auto`, ask once whether to push and open it, and end the turn on the question.
  For a ready plan's tracked bundle, the same question asks whether to delete it, recommending deletion.
  It also names each feature folder under the `Wireframes` or `Mockups` locations that the branch added or the plan cites (`assetRefs`, its FIS files), never a location itself, and asks whether to delete them.
  Recommend deleting them unless their build is still to come: the plan is not ready, or the branch changed nothing outside design and spec folders.
  With no remote, ask only about the bundle, those folders, and the issues.
  For a visible UI change the request said nothing about, it offers screenshots, recommending them where the `Visual Validation` document exists.
- On a yes, or under `--auto` outside the offer, invoke the previewed publish without `--dry-run`.
  Add step 3's closing links from the issues it reports, and under `Record: tracker` put the parent issue's URL on `pr-section.md`'s `PRD:` line.
- A deletion (step 1's delete answer included), the `> **Shipped**:` stamp, and the `shipped` marker happen only when the push goes ahead or there is no remote.
- On a delete, commit the deletion before the push: `plan.json`, its FIS files, any `intent.md` beside them, and any `superseded/` folder go, and the requirements file its `prd` names stays.
  A `prd.md` that stays gains a `> **Shipped**: <UTC ISO-8601 minute>` header line in the same commit.
  Under `Record: tracker`, that file goes too once the issues are published, because they then carry the record, and until then the bundle stays, because the issue bodies are written from it.
- With either deletion, repoint each committed link into a deleted file at what survives it, such as the requirements file, its issue, or an ADR, because a dead link fails silently.
  A branch commit is no such target, because a squash merge leaves it out of the base branch.
- When a ready plan's bundle stays by the user's answer or untracked, write its `shipped` marker, so later runs read the plan as a record.
  A tracked one is committed before any push, then once the pull request opens its `pr` is set, committed, and pushed.
  An untracked one is written once the pull request opens, else at the run's end with `pr` null, and left uncommitted.
- Before the push, capture the screenshots or recording the request asked for or the answer or `--auto` took up, per the `Visual Validation` document.
  Capture the commit being pushed, in the fewest screens that show a reviewer what changed, because an earlier capture can predate a fix.
  Keep a capture only when it shows the state its alt text names, and reference each kept one in the body by relative path above the Ship summary.
- With consent and a remote, push the branch and open the pull request.
  Attach every kept capture and step 3's SVGs through the host's upload, such as `gh pr create --attach <file>` (gh 2.99 or later), which swaps the body's relative reference for the uploaded copy.
  A create that exits non-zero after printing the pull request's URL opened it without the files that failed, and the publication is complete without them.
  Remove the body's reference to each file not uploaded, and list it for the user to attach, with its reason.

**Gate**: no push before any bundle or design-folder deletion or tracked `shipped` marker is committed, and the pull request's URL, or its title, body, and the commands still to run to open it.
Under `--auto` with a remote, an incomplete publication ends on `BLOCKED:`.

## Output

Report:

- each `Learnings` bullet written, each recommendation, and each observation judged not worth keeping, with its reason;
- the commits made, the bundle files and design folders deleted, and the bundle or each design folder kept, with the `ASSUMPTION:` line of an unattended run;
- each change left uncommitted, each file left in the bundle's directory, and whether the plan was marked `shipped`;
- the pull request's URL, each issue published, each story or PRD the publish left out, a tracker read that failed, each issue left for the user to close, and each image or recording not uploaded, with its reason, or its title, body, and the commands still to run.
