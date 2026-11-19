---
description: Recalibrate the role agents' model and effort pins in `plugin/skills/init/templates/agents/` from current benchmarks and measured cost per task, by the rule in `docs/MODEL-EFFORT-SELECTION-GUIDE.md`, and keep that guide's method current. Trigger on 'recalibrate the roles', 'are the role pins current', a provider shipping or repricing a model, and every release.
---

# Recalibrate Roles

Re-picks each role template's model and effort against the hosts' current lineups and benchmarks, and changes only the pins the rule moves.
`docs/MODEL-EFFORT-SELECTION-GUIDE.md` § Choosing a role's pin is the **Single Authority** for the rule (sources, Stage 1, Stage 2, the change rule, Copilot lists); this skill is its procedure.
`Role Pin Record` (`docs/ROLE-PINS.md`) holds the last run's sources, margins, and shortlist.

## Rules

- Every number in the shortlist carries the URL it was read from; a number not read from a page stays blank, because a recalled score is how a wrong pin ships.
- Edit only the templates' model and effort lines, the guide's method, `Role Pin Record`, and `CHANGELOG.md`; the role bodies and descriptions are the `init` skill's.

## Workflow

### 1. Lineups

List, per host (Claude Code, Codex, Copilot CLI), every model a user can select today with its exact ID, from the providers' and GitHub's official model pages.
Gate: each host has a dated lineup with source URLs, and every Copilot ID is one GitHub publishes for Copilot CLI.

### 2. Sources

Run the guide's admission test on each fixed source against its current leaderboard, and read its last verdict from `Role Pin Record` for the guide's replacement condition.
Then search for coding benchmarks published or refreshed since the last record's date, and run the guide's check test on each.
Search too for provider positioning and practitioner reports that bear on Stage 1.
Match each source's model names to the lineups from step 1 by its own model pages, and leave a pair unmatched rather than guess.
Gate: every fixed and found source has a verdict, passes or the item or clause it fails, with its URL; the scorer passes with its margins, else the run stops and reports why; and Stage 1 has a keep-or-change verdict naming its evidence.

### 3. Shortlist

Write to `.agent_temp/recalibration-<date>/shortlist.md`:

- every eligible (model, effort) pair's coding score, general score, and measured cost;
- per role and host, the Stage 2 pick and the change rule's verdict against the current pin;
- each admitted check's comparison with that pick, which holds the pin where the check conflicts.

Gate: each role on each host shows the current pin, the rule's pick, the arithmetic that decided it, each check's agreement or the reason it could not compare, and keep, change, or held.

### 4. Apply

- Edit the pins whose verdict is change.
- Update the guide where the run showed its method wrong, such as a new provider rung or a Stage 1 change.
- Overwrite `Role Pin Record` with this run's source verdicts, margins, Stage 1 evidence, and deciding rows.
- Write a `CHANGELOG.md` bullet on its index entry's terms when a pin changed.

Gate: every hunk this run made is a pin line, a guide method line, the record, or the CHANGELOG bullet.

### 5. Verify

Dispatch the `reviewer` role, else a generic subagent, with the shortlist and this run's hunks, to re-read each deciding number from its source page and check every edit against the shortlist; it returns discrepancies with locations.
Then run the `skill-review` skill over the changed templates and the `fast` tier from `Key Dev Commands`.
Gate: no unresolved discrepancy, and the fast tier passes.

## Output

- `.agent_temp/recalibration-<date>/shortlist.md`: lineups, every candidate pair with its numbers and URLs, and the per-role tables.
- `Role Pin Record` and the other edited files, uncommitted.

The report lists, per host and role, kept or changed with the deciding numbers, then each held pin's check conflict for the user to settle, then every source's verdict, and a proposed fixed-set change when the guide's replacement condition holds.

## Follow-up

Commit by path once the user asks.
