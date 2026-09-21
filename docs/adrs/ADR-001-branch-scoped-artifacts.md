# ADR-001: Keep implementation artifacts branch-scoped

**Status:** Accepted

**Recorded:** 2026-09-07 (retrospective)

## Context

Plans and FIS files govern implementation and verification. Keeping them synchronized with code indefinitely would create a second record that must remain accurate after their delivery purpose ends.

## Decision

Implementation artifacts are branch-scoped. Preserve product intent, decisions, and learnings beyond the work; do not maintain completed FIS files as living specifications.

`plan.json` and the FIS files are deleted before the merge, after each FIS's Implementation Observations have been read and what belongs in Learnings or Decisions has landed there. The PRD stays; a review report is a working file of one review run, ignored or committed per project (amended 2026-09-19). The FIS head travels in the squash-merge message, and every story commit carries `Story-ID:`/`Plan:` trailers, so the linkage outlives the deletion.

## Rationale

The recorded alternative was a “Living Spec” kept synchronized after merge. That offers ongoing audit traceability but requires maintaining another artifact alongside the implementation. AndThen keeps governing traceability during execution and preserves durable knowledge before the merge.

## Consequences

There is less material to keep current, but no maintained post-merge spec–code correspondence. Durable observations must leave the working artifacts before deletion. Story commit provenance retains linkage; it does not replace a maintained specification.

Reconsider when users require ongoing spec–code synchronization, rather than because that approach becomes fashionable.

## Evidence

- History: `63973fd` records the rationale; `ae14dd2` makes deletion explicit; `07b6815` refines receipt handling.
- Current behavior: the artifact-lifecycle paragraph in [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) and the path-staged story commit with its trailers in [`exec-spec`](../../plugin/skills/exec-spec/SKILL.md) Step 5.
