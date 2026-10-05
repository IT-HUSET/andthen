# ADR-014: Run the story where the skill is invoked

**Status:** Accepted

**Recorded:** 2026-09-13; rewritten 2026-09-28 to the decision as it now holds – `exec-plan` merged into `exec-spec` ([ADR-020](ADR-020-one-authoring-and-one-execution-skill.md)), and the `ops` verbs it once named are gone ([ADR-003](ADR-003-runtime-state.md)); amended 2026-09-29 – the story writes its own `plan.json` row, where the run session wrote it.

## Context

The design this replaces kept coordination in the invoking session for one reason: a subagent returning before its own reviewers left no reliable collector, so the session that dispatched an implementer child stayed active and owned the review, the amendments, completion, and the commit. A plan run followed by executing the story procedure in its own session per story, where 0.x `main` had spawned one subagent per story that invoked `exec-spec`.

The harness fact behind the collector problem no longer holds. Checked 2026-09-13 against Claude Code's sub-agents documentation: a subagent may spawn subagents up to three layers below the session and may invoke a skill with arguments; Codex CLI supports the same. An `exec-spec` that is itself a subagent can dispatch its own reviewer and collect it. On 2026-09-13 the maintainer recorded the in-session plan run as a regression from `main` and approved the model below.

## Decision

**The story runs where the skill is invoked.** `exec-spec` on a FIS implements it in its own context: admission, the tasks in FIS order with each task's `Verify`, its own tier – the full tier, or the fast tier under `--no-full-tier` – then every `Proof` and `Verify` target and Final Validation Checklist item, the `verified` record quoting one of those output lines, and the commit. It always spawns one fresh reviewer subagent that invokes the `andthen:review` skill with `--quick --fix --intent <fis>` (plus `--auto` in an unattended run) over the changed paths, carrying the Chain Attestation as the claims to falsify; that subagent applies the Fix-routed findings as the story's one repair round and returns every finding, and `exec-spec` re-runs what those fixes invalidated. There is no gate report and no verdict grammar: open findings are enforced in the separate `review` → `implement-fix` step.

**A plan run schedules and gates.** `exec-spec` on a plan directory spawns, per ready story, one fresh implementer subagent that invokes the `andthen:exec-spec` skill with `--auto --no-full-tier <fis>`, and adds no review of its own. The story writes its own row and commits it with its work; the run session writes none. The run executes the full tier each story deferred, once, on the final tree; its repair round is a fresh subagent that invokes the `andthen:triage` skill with `--auto` on the failing checks and the affected FIS paths.

Retired: the implementer child inside `exec-spec` with its continuation and replacement protocol, the Ownership table, the verifier subagent, the in-session story procedure, and the per-story review gate.

## Rationale

Completion is bound to proof the executing context ran. The founding incident is observed: on 0.x a story reached `done` with 237 checked boxes and no probe executed – a story whose author certified its own work with nobody instructed to run anything, never a case for a script parsing FIS prose. Independence comes from who verifies, not from what runs the command: the proof lines are tool results `exec-spec` saw, and the fresh reviewer is the change's independent read. `exec-spec` writes the change, so its own pass is not the independent one, and the reviewer runs on every story instead of only when the change seems to earn one. The review stays quick; depth stays at the plan-level review.

Each story runs in its own context, so the earlier reason for a separate verifier – proofs run in the coordinator pile N stories' output into one session – no longer applies.

A plan run → `exec-spec` → reviewer is three layers, the documented limit. `exec-spec` dispatches reviewers, lookups, and visual validation, never another executor on a FIS.

## Consequences

One quick review runs per story in a plan run as well as on a direct run. One tier runs per story: the full tier on a direct run, the fast tier under `--no-full-tier` – how a plan run keeps the full tier to one run, on the final tree. A failed story returns its `## Failed Story Report` from its own subagent, so failure evidence and partial progress are attributed to one story's context rather than to the run's. The plan run's report quotes each story's `Reviewed:` line rather than reviewing anything itself.

Where no reviewer subagent can be spawned, `exec-spec`'s own diff pass against the FIS is the review and its `Reviewed:` line says so. Reopens on a story reaching `done` with a proof `exec-spec` did not run.

## Evidence

- Implementation: `9a6d76e` (exec-spec implements the FIS itself, verifier retired, one quick reviewer always); `8eb5d60` (one fresh exec-spec subagent per story, repair round through triage); `fc5c039` retires the story gate from `ops`.
- Current contract: [`plugin/skills/exec-plan/SKILL.md`](../../plugin/skills/exec-plan/SKILL.md), [`references/story.md`](../../plugin/skills/exec-plan/references/story.md), [`references/plan-run.md`](../../plugin/skills/exec-plan/references/plan-run.md).
