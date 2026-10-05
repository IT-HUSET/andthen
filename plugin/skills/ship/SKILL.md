---
description: Ship the current branch – land the plan's FIS Implementation Observations worth keeping and delete its bundle, commit, then push and open the pull request on one ask. Trigger on 'ship it', 'open the PR', 'close out the plan'.
argument-hint: "[--auto] [plan.json path] [notes for the pull request]"
---

# Ship

Close out the current branch and open its pull or merge request. A branch carrying a plan bundle – `plan.json` and the FIS files beside it – first lands what its FIS files learned, then deletes the bundle, because a plan's specs govern one branch and never merge.

## Input

`$ARGUMENTS` minus flags is optional: a `plan.json` path, and anything the pull request should target or say.

- `--auto` makes the run unattended: read [`unattended-runs.md`](../../references/unattended-runs.md) and follow it.
- A branch with a plan bundle: read [`plan-schema.md`](../../references/plan-schema.md), whose § Shipping says when the plan is ready.

`Learnings`, `Decisions`, and `Visual Validation` are **Project Document Index** entries.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Story intent survives the merge.** Leave the story commits unsquashed and unreworded, because each message holds its FIS's Intent and Expected Outcomes once the bundle is deleted.
- **Publishing waits for a yes.** Commits and the bundle's deletion run unasked, because the branch history keeps both. A push and a pull request leave the machine, so they wait for the user's yes.
- **Commit only the branch's own work.** Stage by path, never `-A` or `-u`, and commit by path (`git commit -- <paths>`), because a plain commit takes whatever another session has staged. A change you cannot tie to the branch stays uncommitted, because it may be another session's work in progress.

## Workflow

1. **Check for open work.** Open work is what keeps a plan from being ready under § Shipping, and on any branch a CRITICAL or HIGH finding the latest review of its work leaves open. Name it and ask once whether to ship anyway, recommendation first. While the plan is not ready, recommend keeping the bundle, skipping step 2 and the deletion, because its remaining stories and reviews still read it. **Gate**: nothing open, or the user's answer.

2. **Land the observations** (plan bundle only), because nobody reads a FIS once step 4 deletes it. Read every FIS's `## Implementation Observations`, and write each trap as one `Learnings` bullet under its fitting topic, admitted against its header note. Recommend the rest worth keeping in the output, because decisions and upstream documents stay the user's. A design change no ADR or `Decisions` entry records yet becomes a recommended `Decisions` line, or a run of the `andthen:decide` skill where alternatives are still open. **Gate**: every observation written, recommended, or judged not worth keeping.

3. **Write the pull request** for a reviewer deciding whether to merge: what the change is for, the outcomes it delivers, and the proof of each. It is the one record of them that merges, because the bundle is deleted, the review report is usually never committed, and a squash merge may keep only this body. Take the intent from the commits and from the plan's source: the file its `prd` names, else what its stories' `sourceRefs` cite. Link a cited tracker item so the merge closes it. Take the proof from each story's `verified.summary` in `plan.json` and from the latest review's verdict. Name what the change knowingly leaves open, such as a finding or story the user shipped past. A project's pull request template or named PR process sets the layout, and this content fills it. Put what the merge decision needs first and fold per-story detail below it, because a body the reviewer must scroll goes unread. Where a flow, structure, or state change reads faster as a picture, add the smallest view that makes the point: a Mermaid diagram where the host renders one, an SVG, or a pseudocode or tree block. **Gate**: a title, and a body that states the intent, the outcomes, and their proof before any per-story detail.

4. **Commit.** Commit the fixes left in the working tree. With a plan bundle, commit the landed entries and the bundle's deletion too: `plan.json` and its FIS files go, and the requirements file its `prd` names stays. A bundle file git does not track has no copy in history and never reaches the merge, so leave it in place. Repoint each committed link into a deleted file at what survives it, such as the requirements file, an ADR, or the story commit, because a dead link fails silently. **Gate**: the branch's own work committed, no tracked bundle file left unless step 1 kept the bundle, and no committed link into a deleted file.

5. **Publish.** Show the base branch, the commits leaving, the title, and the body, marking each commit made after the latest review report's `**Revision**`, other than this run's own. Ask once whether to push and open it, offering screenshots or a recording for a visible UI change the request said nothing about, and end the turn on the question. Before the push, capture the screenshots or recording the request asked for or the answer took up, per the `Visual Validation` document. Attach each image through an upload the host accepts, else list it for the user to attach. Under `--auto`, stop before the push. **Gate**: the pull request's URL, or its title, body, and the commands still to run to open it.

## Output

Report:

- each `Learnings` bullet written, each recommendation, and each observation judged not worth keeping, with its reason;
- the commits made and the bundle files deleted;
- each change left uncommitted and each untracked bundle file left in place;
- the pull request's URL and each image left for the user to attach, or its title, body, and the commands still to run.
