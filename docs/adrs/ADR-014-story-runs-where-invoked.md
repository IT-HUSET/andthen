# ADR-014: Run the story where the skill is invoked

**Status:** Accepted. Amended on 2026-09-21 – the `ops` verbs the Decision names are gone: task ids and the `verified` line are written into the story's `plan.json` row by the run session, and a dispatched story reports them instead of writing. Who runs the story, and who reviews it, is unchanged.

**Recorded:** 2026-09-13

**Supersedes:** [ADR-002](ADR-002-execution-ownership.md), [ADR-011](ADR-011-per-story-code-review.md). **Amends:** [ADR-013](ADR-013-scripts-read-json-agents-read-markdown.md).

## Context

ADR-002 kept coordination in the invoking session for one reason: a subagent returning before its own reviewers left no reliable collector, so the session that dispatched the implementer stayed active and owned the review, the amendments, completion, and the commit. The `andthen:exec-plan` skill followed by running the `andthen:exec-spec` skill's procedure in its own session per story instead of invoking that skill, where `main` had spawned one subagent per story that invoked it.

The harness fact behind the collector problem no longer holds. Checked 2026-09-13 against Claude Code's sub-agents documentation: a subagent may spawn subagents up to three layers below the session and may invoke a skill with arguments; Codex CLI supports the same. An `exec-spec` that is itself a subagent can dispatch its own reviewer and collect it. On 2026-09-13 the maintainer recorded the in-session `exec-plan` as a regression from `main` and approved the model below.

## Decision

The story runs where the skill is invoked. `exec-spec` implements the FIS in its own context: admission, the tasks in FIS order with each task's `Verify` and `complete-task`, its own full tier (or the fast tier under `--no-full-tier`), every `Proof` and `Verify` target and Final Validation Checklist item, `complete-story --verified` quoting one of those output lines, and the commit. It always spawns one fresh reviewer subagent that invokes the `andthen:review` skill with `--quick --fix --intent <fis>` over the changed paths, carrying the Chain Attestation as the claims to falsify; that subagent applies the Fix-routed findings as the story's one repair round and returns every finding, and `exec-spec` re-runs what those fixes invalidated. Lookup and visual-validation dispatches are unchanged. Carried forward from ADR-011: no gate report and no verdict grammar, open findings enforced only in the separate `review` → `remediate-findings` step, and `review --quick` as the quick path.

`exec-plan` schedules and gates. Per ready story it spawns one fresh implementer subagent that invokes the `andthen:exec-spec` skill with `--auto --no-full-tier <fis>`, and adds no review of its own. It runs the full tier each story deferred, once, on the final tree; its one repair round is a fresh subagent that invokes the `andthen:triage` skill with `--auto` on the failing checks and the affected FIS paths.

Retired: the implementer subagent inside `exec-spec` with its continuation and replacement protocol, the Ownership table, the verifier subagent, and the in-session story procedure.

## Rationale

Each story now runs in its own context, so ADR-013's reason for a separate verifier – running the proofs in the coordinator accumulates N stories' output in one `exec-plan` session – no longer applies, and its rejected option, the coordinator running the proofs itself, is what this record adopts. Independence moves with the code: `exec-spec` writes the change, so its own pass is no longer the independent one, and the fresh reviewer per story supplies what the implementer split used to. ADR-011's sizing rule – a reviewer only when the change earns it, the coordinator's diff pass otherwise – retires because `exec-spec` now writes the code; the review stays quick, so the depth that rule sized away stays at the plan-level review.

`exec-plan` → `exec-spec` → reviewer is three layers, the documented limit. `exec-spec` dispatches reviewers, lookups, and visual validation, never another executor.

## Consequences

One quick review runs per story under `exec-plan` as well as on a direct run, where before a story could complete with no reviewer dispatched. One tier runs per story: the full tier on a direct `exec-spec` run, the fast tier under `--no-full-tier` – how `exec-plan` keeps the full tier to one run, on the final tree. A failed story returns its `## Failed Story Report` from its own subagent, so failure evidence and partial progress are attributed to one story's context rather than to the run's. `exec-plan`'s aggregate report quotes each story's `Reviewed:` line rather than reviewing anything itself.

Where no reviewer subagent can be spawned, `exec-spec`'s own diff pass against the FIS is the review and its `Reviewed:` line says so. Reopens on a story reaching `done` with a proof `exec-spec` did not run.

## Evidence

- Implementation: `9a6d76e` (exec-spec implements the FIS itself, verifier retired, one quick reviewer always); `8eb5d60` (exec-plan spawns one fresh exec-spec subagent per story, repair round through triage).
- Current contract: [`plugin/skills/exec-spec/SKILL.md`](../../plugin/skills/exec-spec/SKILL.md), [`plugin/skills/exec-plan/SKILL.md`](../../plugin/skills/exec-plan/SKILL.md).
