# Research: Worktree-Based Parallelization for exec-plan-team

**Date**: 2026-03-20
**Status**: Research / Not yet implemented


## Problem Statement

The current `exec-plan-team` pipeline runs **spec → impl → review** per story with all Agent Teams agents sharing a single working directory and branch. Even when stories are independent (`[P]`), implementers and reviewers compete for the same working tree — creating unnecessary serialization.

### Where Parallelism Breaks Down

```
Current exec-plan-team (shared working directory):

  S01: [spec]──[impl]──────[review+fix]
  S02:                  ⏳ blocked ⏳──[spec]──[impl]──[review]
  S03:                  ⏳ blocked ⏳──────────────────[spec]──[impl]──...

  Even when S01, S02, S03 are independent [P] stories, implementers
  and reviewers compete for the same working tree.
```

**Specific bottlenecks:**
1. **Impl blocked by review** — Reviewer for S01 may be doing fix loops while implementer for S02 waits, even though stories are independent
2. **Multiple implementers can't run simultaneously** — Two agents editing files in the same working tree creates race conditions and conflicts
3. **Review fix loops contaminate** — A reviewer fixing S01 code could inadvertently affect S02's in-progress implementation


## Claude Code Worktree Capabilities

### Two Built-In Mechanisms

| Mechanism | Scope | Use Case |
|---|---|---|
| `isolation: "worktree"` on `Agent` tool | Sub-agent gets its own worktree + branch | Parallel sub-agent work |
| `EnterWorktree` / `ExitWorktree` tools | Main session enters a worktree | Interactive worktree sessions |

### Key Behaviors of `isolation: "worktree"`

- Creates worktree at `.claude/worktrees/<name>/` with branch `worktree-<name>`
- Branch is based on HEAD at creation time
- If sub-agent makes **no changes** → worktree + branch auto-deleted
- If sub-agent makes **changes** → worktree path and branch name returned in result
- Each worktree has **fully isolated git state** (different branch, separate working tree)
- **Environment is NOT shared** — `node_modules`, venv, etc. need re-installation per worktree

### Existing Support in exec-plan

The non-team `exec-plan` skill (SKILL.md line 120) already instructs:

> *Use `isolation: "worktree"` for parallel sub-agents to avoid file conflicts. If worktree isolation is not available, execute parallel stories sequentially to avoid file conflicts.*

But it lacks a **merge-back step** — there's no explicit merge orchestration after worktree sub-agents complete.


## Architecture Options

### Option A: Worktree Sub-Agents (No Agent Teams)

Drop Agent Teams entirely. Use worktree-isolated sub-agents coordinated by the orchestrator.

```
Orchestrator (main branch):
  ├── spawn sub-agent (isolation: "worktree") → worktree-S01
  │     └── spec → impl → review (full pipeline)
  ├── spawn sub-agent (isolation: "worktree") → worktree-S02
  │     └── spec → impl → review (full pipeline)
  ├── spawn sub-agent (isolation: "worktree") → worktree-S03
  │     └── spec → impl → review (full pipeline)
  │
  ├── [all complete] → merge worktree-S01, S02, S03 back to main
  └── final verification on main
```

**Pros:** Simple, uses proven Claude Code feature, true parallel isolation
**Cons:** Loses Agent Teams coordination (shared task list, inter-agent messaging), each story is one monolithic sub-agent (can't split spec/impl/review across specialized agents)


### Option B: Agent Teams + Worktree Isolation (Ideal, Uncertain Feasibility)

The `Agent` tool accepts both `team_name` and `isolation: "worktree"` as parameters. If they can be combined, teammates would coordinate via shared task list while working in isolated worktrees.

```
Team "plan-pipeline":
  spec-1 (team + worktree) ──→ produces FIS docs
  impl-1 (team + worktree) ──→ implements in worktree-S01
  impl-2 (team + worktree) ──→ implements in worktree-S02
  review-1 (team + worktree) ──→ reviews in worktree-S01
```

**Pros:** Best of both worlds — coordination + isolation
**Cons:** **Untested** — unclear if `team_name` + `isolation: "worktree"` actually work together. Inter-agent messaging across worktrees raises questions.


### Option C: Hybrid — Worktree Sub-Agents + Orchestrator Coordination (Recommended)

Use worktree-isolated sub-agents with the orchestrator managing coordination via task tools. Captures essential benefits of both approaches.

```
Orchestrator (main branch):
  │
  │ Wave 1 — Specs (on main, low conflict risk):
  ├── spawn spec-creator (opus, NO worktree) → creates FIS for S01, S02, S03
  │
  │ Wave 1 — Impl+Review (parallel worktrees):
  ├── spawn story-S01 (sonnet, worktree) → impl + review in worktree-S01
  ├── spawn story-S02 (sonnet, worktree) → impl + review in worktree-S02
  ├── spawn story-S03 (sonnet, worktree) → impl + review in worktree-S03
  │     (review starts immediately after impl — no blocking!)
  │
  │ Wave 1 — Merge:
  ├── sequentially merge worktree-S01, S02, S03 → main
  ├── clean up worktrees
  ├── verify build + tests on merged main
  │
  │ Wave 2 (branches from updated main):
  ├── spawn story-S04 (sonnet, worktree) → worktree-S04
  │     (branches from main that now includes S01+S02+S03)
  ...
  │
  └── FINAL: verification on main
```

**Pros:**
- Builds on exec-plan's existing worktree support
- Doesn't depend on experimental Agent Teams
- Clean orchestrator pattern (parse → spawn → merge → verify)
- Gracefully degrades to sequential if worktrees unavailable

**Cons:**
- Loses Agent Teams inter-agent messaging (orchestrator mediates instead)
- Environment setup overhead per worktree


## The Merge Step (New Component)

This is the critical new step that doesn't exist in either skill today.

### Wave-Based Merge Strategy

```bash
# After all Wave N stories complete and pass review:

git checkout main

# Merge each story branch sequentially
for story in S01 S02 S03; do
  git merge worktree-story-${story} --no-ff -m "Merge story ${story}: <story name>"
  # If conflict → spawn conflict-resolution agent
done

# Clean up worktrees
for story in S01 S02 S03; do
  git worktree remove .claude/worktrees/story-${story}
  git branch -d worktree-story-${story}
done

# Verify build + tests pass on merged main
# If broken → spawn troubleshooter on main

# Wave N+1 worktrees branch from main (which includes all Wave N changes)
```

### Why Wave-Based Merge Works Well

| Property | Benefit |
|---|---|
| **Dependencies respected** | W2 stories depend on W1 → W2 branches from post-W1-merge main |
| **Conflicts minimized** | Stories in same wave are independent by plan design |
| **Integration verified incrementally** | Build/test after each wave merge catches issues early |
| **Rollback granularity** | Can revert a single story's merge if needed |

### Conflict Resolution Strategy

1. **Auto-resolve trivial conflicts** (e.g., both stories add to same import list)
2. **Spawn conflict-resolution agent** for non-trivial conflicts with context from both stories
3. **Escalate to user** if conflict implies a plan dependency was missed


## Proposed Pipeline Comparison

```
With worktree parallelization (Option C):

  S01: [spec]──[impl ──── review+fix]─────────────┐
  S02: [spec]──[impl ──── review+fix]──────────┐   ├── MERGE → main → verify
  S03: [spec]──[impl ──── review+fix]───────┐  │   │
                                             │  │   │
                    (all truly parallel in   └──┴───┘
                     separate worktrees)

vs. current exec-plan-team (shared working tree):

  S01: [spec]──[impl]──────[review+fix]
  S02:              ⏳ wait ⏳──[spec]──[impl]──[review+fix]
  S03:                           ⏳ wait ⏳──[spec]──[impl]──[review+fix]
```


## Practical Considerations

### Environment Setup Overhead

Each worktree needs its own dependency installation. Mitigation:
- **Parallel setup**: Install dependencies in all worktrees concurrently before starting implementation
- **Selective worktrees**: Only create worktrees for stories that modify code (skip for docs-only stories)
- **Project setup script**: Check if project has a setup script and run it per worktree

### Plan.md Updates

`plan.md` lives on the main branch. Worktree agents can't update it directly.
- **Orchestrator updates plan.md** after each story completes (orchestrator is on main)
- Agent reports results via return value, orchestrator writes to plan

### Reviewer in Implementer's Worktree

Two approaches for review stage:
1. **Impl sub-agent includes review** — worktree sub-agent runs both impl + review stages (simpler, recommended)
2. **Sequential sub-agents to same worktree** — implementer completes, then reviewer spawns targeting the same worktree directory

Option 1 is simpler and avoids needing to target an existing worktree.


## Open Questions

1. **Can `team_name` + `isolation: "worktree"` be combined?** → Quick test: spawn one Agent with both params
2. **Can a second sub-agent target an existing worktree?** → Needed if splitting impl/review across agents
3. **What's the actual overhead of worktree env setup?** → Project-dependent (npm install time, etc.)
4. **How does the orchestrator access worktree branch names?** → Agent tool result should include worktree path and branch when changes are made


## Recommendation

Go with **Option C (Hybrid)** as an enhancement to `exec-plan` rather than a separate skill:

1. Builds on exec-plan's existing worktree support (line 120)
2. Doesn't depend on experimental Agent Teams feature flag
3. The merge step is the only truly new component to add
4. Gracefully degrades to sequential when worktrees unavailable
5. Can be ported to exec-plan-team later if `team_name` + `isolation: "worktree"` is validated

If Option B (Agent Teams + worktrees) proves feasible, it could be added as a separate enhancement to exec-plan-team.
