# ADR-003: Separate runtime state from specification prose

**Status:** Accepted. Amended by [ADR-013](ADR-013-scripts-read-json-agents-read-markdown.md) on 2026-09-11 – the standalone sidecar retires; a standalone FIS is a one-story `plan.json`, and the `update-fis` forms retire with the agent editing Implementation Observations directly. Amended on 2026-09-21 – `plan.json` still owns runtime state, but the mutation contract is gone with the `ops` skill: the run session executing the plan or spec is the file's only writer, editing rows with its file tools per `plan.schema.json`, and a story subagent reports its state instead of writing it. One writer replaces locking – the failure locking existed for was two writers, and there is now one.

**Recorded:** 2026-09-07 (retrospective)

## Context

Execution must resume from durable progress without repeatedly rewriting the specification. Duplicating progress across FIS prose and a separate state record creates competing truths; concurrent mutations can also lose updates.

## Decision

Schema v2 `plan.json` owns bundle intent, dependencies, and runtime state, including story status, FIS pointer, owner, and completed task IDs. A standalone FIS uses an adjacent schema v1 `<fis-stem>.state.json` containing status and completed task IDs.

The `andthen:ops` skill owns runtime mutations. Writes lock, re-read, validate, and atomically replace state. `read-state` projects either form without writing. Scheduling groupings are derived rather than persisted.

Ordinary progress updates never change FIS prose. After execution begins, only the documented `update-fis` amendment and observation forms may change it. Schema versions count breaking changes against a release, not unreleased intermediate designs.

## Rationale

This replaces FIS task checkboxes as execution state. Keeping progress beside its owning artifact avoids a central state document and leaves the specification stable for review. Serialization prevents cooperating writers from overwriting each other's updates.

## Consequences

A standalone specification has a companion state file; reading its Markdown alone no longer reveals progress. Tools must use the canonical state and mutation contracts. Locking depends on writers using those operations; direct file edits bypass them.

## Evidence

- History: `9d9a2ac` introduces external FIS state; `07aaa67` refines locking; `ae14dd2` settles release schema v2.
- Current contracts: [plan and state schema](../../plugin/references/plan-schema.md), [the machine schema](../../plugin/references/plan.schema.json), and [FIS mutability](../../plugin/references/fis-mutability.md).
