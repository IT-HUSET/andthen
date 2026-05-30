# Large-Diff Fan-Out

Partition-based sub-agent fan-out for `code` and `gap` lenses when the diff is
too large for a single reviewer's working context. Each partition is reviewed
by a fresh-context sub-agent applying the same lens rubric; a boundary pass
then attacks cross-partition surface.

> **Distinct from `--council`**: council fans out by **lens specialist**
> (correctness, architecture, security, …) over the **same** scope. This file
> fans out by **partition of the scope** under the **same** lens. They compose
> – council multiplies a partition's depth-of-perspective, partition fan-out
> multiplies a council's breadth-of-coverage.


## Contents

Trigger · Partition Strategy (1. Vertical slice · 2. Package/module · 3. Language · Anti-pattern) · Execution · Composition with `--council` · Cost / Latency Note · Reporting


## Trigger

Apply when any one fires (auto-detection):

- Changed file count ≥ 20
- Changed LOC ≥ 1000 (excluding generated / vendored / lockfile noise)
- Diff spans 3+ top-level packages, modules, or app entry points
- Caller passed `--fanout` explicitly

Below the threshold, run the lens inline. `--no-fanout` forces off even when
auto-trigger fires (useful for interactive review where latency matters more
than coverage).


## Partition Strategy

Target **2–5 partitions** of roughly equal change weight. Above 5, merge
overhead and boundary-surface growth dominate. Below 2, the partition is the
whole diff – run inline.

Choose the first applicable strategy:

### 1. By vertical slice (PREFERRED)

A **vertical slice** is a feature- or concern-shaped group of files that
together implement one demoable change end-to-end (the same "vertical slice"
shape the `andthen:plan` skill uses for stories). Slices cut **through** layers;
they do not cut **between** layers.

Detect slices from the strongest signal available – first match wins:

1. **Active FIS Task IDs** (`TI01`, `TI02`, …) – files cited in or implied by
   the same Implementation Task are one slice. The FIS itself is the most
   reliable slice map for FIS-driven implementations.
2. **Plan Story IDs** (`S01`, `S02`, …) – when reviewing a plan rollout, each
   story is one slice; its files map to the story's FIS.
3. **Per-commit clustering** – when the diff has multiple commits with
   distinct, coherent messages, each commit is a slice candidate. Squashed
   commits or "fix typos" / "address review" commits are not slice signals.
4. **FIS Work Areas** – when no task-level mapping exists, each declared Work
   Area is a slice candidate.
5. **Concept clustering** – files sharing a feature name, module prefix, or
   strongly connected sub-graph in the diff's import/reference graph
   (e.g. `skill_registry.dart` + `skill_registry_impl.dart` + their callers).

### 2. By package/module (FALLBACK)

When no slice signal resolves – or the change is a uniform sweep across
packages – partition by top-level package: `packages/<name>/`,
`apps/<name>/`, `crates/<name>/`, top-level Python packages, Go modules,
SwiftPM targets. One partition per touched package.

### 3. By language (LAST RESORT)

When the diff mixes languages with disjoint review concerns
(e.g. backend Go + frontend TypeScript + IaC YAML), and neither slice nor
package partitioning produces useful groups.

### Anti-pattern: horizontal slicing

Do **not** partition by architectural layer (`api/`, `domain/`, `infra/`,
`tests/`). Cross-layer invariants – the deletion whose caller lives one layer
up, the cache whose consumer lives one layer down, the validation whose test
moved between layers – are exactly the issues partition fan-out exists to
surface, and horizontal slicing hides them between partitions instead.

If layered organization is the only natural shape the diff offers, that is a
signal to fall back to package partitioning, not to slice horizontally.


## Execution

1. Compute partitions per the strategy above. Record the partition map in the
   final report under a one-line "Partition map" entry (slice name → file
   count) so the user can audit how the diff was split.
2. Per partition, spawn a fresh-context sub-agent applying the primary lens
   rubric (`lens-code.md` / `lens-gap.md`) scoped to that partition's files.
   Pass:
   - The full primary-lens reference
   - The partition's file list (explicit; do not let the sub-agent re-detect scope)
   - `refactor-invariants.md` (sibling reference) when its triggers fire on the
     partition's slice of the diff
   - `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and the
     lens-specific calibration
   - Target map, Intent Context, and Project Rules Context from Step 1
3. After all partitions return, run a **boundary pass** inline (or as a final
   sub-agent when the diff is very large). The boundary pass:
   - Re-runs `refactor-invariants.md` checks 1 (deletion completeness), 2
     (resolve-once-consume-many), and 6 (parameter threading) across partition
     boundaries – these are the checks where the second site can live in a
     different partition than the first
   - Looks for contradictions between partitions (slice A's report passes a
     surface that slice B's report flags)
   - Tags findings `reviewer: Boundary Pass`, `scope_relation: primary`,
     `source_partition: boundary`
4. Merge findings: deduplicate by `(location, finding)` keeping the strongest
   framing. Cross-partition findings from the boundary pass merge into the
   normal severity sections – do not segregate.
5. Apply the existing Findings Filter (Devil's Advocate, Synthesis Challenger)
   to the merged set, using the structured finding contract from
   `council-mode.md`.


## Composition with `--council`

`--council` and `--fanout` compose:

- **Council alone**: N specialists × 1 scope (the whole diff) – depth of
  perspective, no scope split.
- **Fan-out alone**: 1 specialist (the primary lens) × M partitions – breadth
  of coverage, single perspective per area.
- **Both**: each council specialist fans out across the M partitions. Total
  fan-out is `specialists × partitions`. The boundary pass still runs once
  over the merged finding set.
- **In a chain** (2+ lenses): each lens's partitions join the chain's single
  flat batch as further leaf sub-agents (see SKILL.md Step 4 *Chain*), never
  nested under a per-lens wrapper.

**Concurrency**: dispatch the full leaf set as one flat parallel batch from the
orchestrator and let the host schedule it – do not impose an artificial
sub-agent count limit. Council × fan-out (× chain) multiplies the leaf count
quickly, so the real control is choosing the **fewest partitions and
specialists that still give distinct coverage** – without silently dropping
either, since each covers what the other can't.

When `--team` is used with `--fanout`, partitions become team tasks. Re-use
the team-mode orchestration from `council-mode.md` § 3a; the per-partition
review prompt replaces the per-specialist review prompt.


## Cost / Latency Note

Each partition adds roughly one full review's cost. Fan-out trades wall time
and token spend for coverage of changes that exceed the inline working set.

For automation contexts (PR-review hooks, CI annotations), fan-out only when
the threshold fires – the typical small PR pays nothing extra. For interactive
review where the user is waiting on output, `--no-fanout` is the override; the
report will then state "Fan-out suppressed; inline review over <N>-file diff"
so the user can re-request with fan-out if the inline result feels thin.


## Reporting

The consolidated report (Step 5b in the skill workflow) gains two lines under
the Executive Summary block when fan-out ran:

```markdown
Partition strategy: <vertical-slice | package | language>
Partition map: <slice-name>(<n> files), <slice-name>(<n> files), …
```

Per-partition section ordering follows the partition map. The boundary-pass
findings (if any survive filtering) render in a `## Boundary Findings` H2
between per-partition sections and the overall verdict – analogous to the
`## Cross-Lens Synthesis` section that `--council` chains produce, but for
partition boundaries within a lens rather than for lens boundaries within a
chain.
