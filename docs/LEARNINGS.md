# Project Learnings

<!-- Traps only, one bullet each: `- **{title}** – …` under 200 chars, trap + pointer; postmortem
     depth lives in the spec archive or an ADR. Bar: "Would a competent developer with code and
     git access still get bitten?" Skills read this index whole – keep it lean. Maintain via the
     `andthen:ops` skill (`update-learnings` forms), which owns the 150-line ceiling and
     `learnings/` shard graduation. Delete entries once encoded as checks or stale. -->

## Agent Workflows

- **Audit/review fan-out subagents may edit source despite read-only prompts** – expect post-run changes only in `.agent_temp/`; save recovery diffs and confirm provenance (user WIP) before restoring.
- **`isolation: "worktree"` is silently ignored for Claude Code team agents; manual `git worktree` + `cd` moves only Bash** – other tools resolve the session CWD; use `EnterWorktree`.

## Cross-Agent Packaging

- **Never add `name: andthen-<x>` skill frontmatter** – Codex plugins register `<plugin>:<frontmatter-name>`, so it stutters as `andthen:andthen-x`.
- **Codex `$` sigil parsing rejects dots in loose-skill names** – hyphen prefixes only; a dot prefix once silently disabled explicit skill injection for every installed skill.
- **No generated/duplicated artifact trees in the repo** – both hosts read the single `plugin/` source verbatim via thin manifests; a full dist/ build pipeline was tried and rejected.

## Error Patterns
<!-- Log recurring errors. Deterministic errors (bad schema, wrong type) → conclude immediately.
     Infrastructure errors (timeout, rate limit) → log, no conclusion until pattern emerges.
     Conclusions are promoted into the relevant topic section (or its shard). -->

| Error | Type | Conclusion |
|-------|------|------------|

## Process & Tooling

- **Parallel-authority enumerations drift** – installer asset arrays, the ARCHITECTURE shared-assets table, REQUIREMENTS-SPEC bullets, plugin/README, and the skill-reference catalog desync repeatedly; audit all five on any change to one.
- **Spec-pipeline cost is remediation-shaped, not review-shaped** – 2026-08 benchmark: fix rounds 41% vs authoring 14% of cost; fixer dispatches outcost small fixes. Mitigated 0.38.1 (see CHANGELOG).
