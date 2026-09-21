# ADR-006: Let installed roles own model and effort

**Status:** Accepted

**Recorded:** 2026-09-07 (retrospective)

## Context

Delegation needs model and effort settings that hold on every spawn. Setting them per spawn call is easy to skip, and repeating selection rules in skills creates competing authorities.

## Decision

The nearest Subagent Model Policy owns selection. Prompts carry task shape, persona, reference inputs, and read-only constraints. Four optional role definitions supply the pins:

- `oracle`: top model/xhigh for user-assigned judgment or hard problems handed over by an agent.
- `implementer`: top/high for substantial pinned work, including implementation and research that weighs evidence.
- `reviewer`: top/medium for independent reviews.
- `worker`: cheap/medium for small, specified, verifiable tasks.

Roles never auto-load. Without them, the spawn call steers – the model where the host's spawn tool offers one, and on Codex the effort too – and unset values inherit from the session, whose model is the ceiling. Routine judgment stays in the session; agents do not select the oracle for ordinary advice or unsolicited second opinions.

## Rationale

Role definitions pin the tier once, for every spawn of that role, instead of relying on each spawn call to set it. Earlier oracle routing over-delegated judgment that needed the session's context. Review effort at xhigh produced analysis-paralysis and scope creep; medium separates review from implementation's high default. Oracle xhigh also distinguishes its depth from implementation, beyond model choice alone.

## Consequences

Projects can replace role definitions without rewriting skills. The generic fallback preserves portability but cannot promise the installed roles' model or effort.

## Evidence

- History: `67c7943` introduces optional roles; `dc702e3` revises oracle scope; `07b6815` preserves the recorded policy rationale.
- Current contract: [delegation shape](../../plugin/skills/exec-spec/SKILL.md#ownership) and [role guide](../MODEL-EFFORT-SELECTION-GUIDE.md#the-model-four-optional-roles-one-generic-fallback).
