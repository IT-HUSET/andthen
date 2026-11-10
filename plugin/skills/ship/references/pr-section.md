# Ship Summary Template

> The section `ship` ends every pull request body with, under a project's template too. `{{…}}` is filled in; a `>` note is guidance, never body text.
>
> It restates facts the prose above it already gives, so a viewer can join the pull request to its requirements, proof, and reviews without an agent run.
> Downstream tooling parses the heading, the `PRD:` and `Undo:` labels, the table headers, the lens names, and the tokens as spelled here, so write them exactly.
> The section runs from its heading to the next `## ` heading or the body's end, once per body, and text added to the body later goes above the section, outside its `<details>` block.
> Where the host renders no `<details>`, leave out the block's three tag lines.
> Every cell is one line without bold. Write a `|` inside a cell as `\|`, and an absent value as `-`, the ASCII hyphen, never an en or em dash.

<details>
<summary>Ship summary (tables for tooling)</summary>

## Ship summary

PRD: {{the requirements file's path at the pull request's head, its tracker issue's URL under `Record: tracker`, or -}}

> One `PRD:` line per distinct `prd` the plans name, else per requirements file their stories' `sourceRefs` cite.

| Story | Plan | Outcome | Requirements | Outcome proof |
|---|---|---|---|---|
| {{story ID}} | {{plan.json path}} | {{one Expected Outcome bullet verbatim, its `[OCnn]` tag included}} | {{bare FR IDs, comma-separated, such as `FR1, FR3`}} | {{the story's `verified.summary`}} |

> One row per Expected Outcome, grouped per story in plan order, and one row with Outcome `-` for a story whose FIS has none; a `skipped` story has no row.
> Without a plan, each outcome the body states is one untagged row, with Story, Plan, and Outcome proof `-`.
> Requirements are the bare IDs, spelled as the PRD's `#### FRn:` headings spell the ID and without the title after it (`FR3`, never `FR3: Its title`), of the Feature Specifications this outcome answers, traced through its story's `sourceRefs` anchors and its FIS's Required Context. Write `-` rather than copy a story's whole set onto an outcome that does not answer it.
> With two or more `PRD:` lines, a `PRD` column after `Requirements` carries the outcome's `PRD:` value verbatim.

| Lens | Verdict | Reviewed commit | Remediated |
|---|---|---|---|
| code | {{PASS / FAIL / not reviewed}} | {{Revision}} | {{yes / -}} |
| gap | {{PASS / FAIL / not reviewed}} | {{Revision}} | {{yes / -}} |
| security | {{PASS / FAIL / not reviewed}} | {{Revision}} | {{yes / -}} |
| outcome | {{PASS / FAIL / not reviewed}} | {{Revision}} | {{yes / -}} |

> All four rows, in this order. Each takes the latest review report that ran the lens: the PASS or FAIL its verdict gives the lens, and its `**Revision**` verbatim, a `-dirty` suffix kept.
> Remediated is `yes` on every row a report carrying a `**Remediated**:` line supplies, a mixed report's included, because its verdict predates the fixes and no review has re-run the lens since.
> A report written before verdicts were PASS or FAIL maps `Ready` to `PASS`, and `Needs Fixes` and `Blocked` to `FAIL`.
> A lens no report gave a verdict is `not reviewed` with commit and Remediated `-`, and gets an `unchecked` row below.

| Read closely | Files | Note |
|---|---|---|
| {{most-harm / no-check / unchecked / after-review}} | {{`path`, comma-separated}} | {{one sentence}} |

> One row per item the body's "Where to read closely" names, its token the bullet it comes from: `most-harm` the files where an error does the most harm, `no-check` a choice no check can judge, `unchecked` a check, lens, or surface skipped, unavailable, or `not reviewed`, and `after-review` work after the latest report's `**Revision**`.
> A review narrowed to stories or paths gets an `unchecked` row naming what it left out.

Undo: {{what undoes the change and what no revert restores, or revert the merge}}

</details>
