# Skill Trigger Evals

Minimal trigger-eval setup for the highest-value AndThen routing skills.

This is intentionally small. The goal is to catch obvious routing regressions in skill `description` changes without building a heavyweight eval framework.

## Scope

Current query coverage focuses on the core workflow boundaries:

- `clarify`
- `spec`
- `plan`
- `exec-spec`
- `review`
- `review-gap`

These skills are the most likely to be confused with each other, and they carry the most value from precise routing.

## Files

- Query corpus: [`evals/skill-trigger-queries.json`](../evals/skill-trigger-queries.json)
- Eval runner: [`scripts/eval-skill-triggers.sh`](../scripts/eval-skill-triggers.sh)

## How To Run

Evaluate the full corpus once:

```bash
./scripts/eval-skill-triggers.sh
```

Evaluate one skill only:

```bash
./scripts/eval-skill-triggers.sh --skill spec
```

Run multiple times per query when tuning descriptions:

```bash
./scripts/eval-skill-triggers.sh --skill review --runs 3
```

## Notes

- The script currently targets the `claude` CLI because the repo's native plugin environment is Claude Code and its JSON output exposes Skill tool calls directly.
- `jq` is required.
- The runner uses a simple majority rule when `--runs` is greater than `1`.
- The runner uses `--tools Skill`, low effort, and verbose stream JSON, then stops at the first observed `Skill` tool call. This keeps the eval focused on routing instead of paying for full downstream skill execution.
- Start with `--runs 1` while iterating. Use `--runs 3` only when you want a more stable read on borderline routing.

## Query Design

The corpus includes both:

- `should_trigger: true` prompts that directly or indirectly express the skill's user intent
- `should_trigger: false` near-miss prompts that should route to adjacent skills instead

The negative cases matter as much as the positive ones. For example:

- `spec` should not fire on "execute this FIS"
- `plan` should not fire on "create a spec for story S02"
- `review-gap` should not fire on "review this spec before implementation"

## When To Extend It

Only expand this setup when real routing problems show up.

Good reasons to add more cases:

- repeated false triggers between adjacent skills
- repeated misses for common AndThen phrasing
- large edits to many skill descriptions
- changes to client-specific skill metadata or invocation policy

Bad reasons:

- trying to cover every skill before any routing issue has appeared
- building client-agnostic automation before the current Claude-focused check is insufficient
