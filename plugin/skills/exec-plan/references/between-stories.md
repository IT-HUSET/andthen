# Between Stories

A dispatched story run never takes these steps: its plan run takes them for it.

## Discovery triage

Carry each discovery in the finished story's `## Discovered Requirements` and `## Implementation Observations`, Drift Notes included, to each unstarted story it affects, whose executor reads only its own FIS.

- A constraint is appended under that story's `## Discovered Requirements` per `fis-mutability.md`. One that contradicts a scenario or Expected Outcome there also needs a revision folding it in.
- A scope change, such as a PRD rule or `sharedDecisions` entry that no longer holds, or a story the plan lacks or no longer needs, never goes into a FIS: recommend the `andthen:clarify` skill's amendment.

For a contradiction or scope change, ask before the next story builds on the old spec whether to make the revision or amendment first, recommending it; the answer sets Follow-up's line or whether a plan run continues, and a decline to revise a contradiction goes into the appended bullet's Interpretation.
Unattended, the run decides instead: it writes its resolution there, names the revision's route or the amendment in its report, and continues on the current plan, a story run's `Next` line on the next story.

Commit these writes before the next story starts, because its run treats an uncommitted edit to its own FIS as foreign. A direct story run commits them with its story, a plan run as one `chore` commit with no story trailers before the next dispatch. Report each FIS changed.

## Simplify

Make it work, then make it good, before the next story builds on it: each `done` story is simplified once.

Dispatch a fresh implementer subagent that invokes the `andthen:simplify-code` skill with `--auto` on the code paths changed by commits carrying the story's `Story-ID:` and `Plan:` trailers. Name `plan.json` and leave the commit to you. In a plan run, pass the focused checks exercising those paths as its baseline and recheck commands. Hand over green results for the same tree. Under `--worktree`, one pass covers the merged batch and runs those checks on the merge for its baseline.

Confirm its rechecks cover the edits and run any invalidated proof still outstanding locally. Commit per `verification-evidence.md` § The commit rule as one `refactor` with the story's trailers, or only the `Plan:` trailer for a merged batch. Report what it applied, deferred and re-ran.
