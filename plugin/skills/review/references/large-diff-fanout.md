# Large-Diff Fan-Out

Partition-based subagent fan-out for the `code` and `gap` lenses when the diff is too large for one reviewer's working context. This fans one lens pass over scope partitions for breadth.


## Trigger

- **Large surface** – ≥20 changed files, ≥1000 changed LOC excluding generated/vendor/lockfile noise, or 3+ top-level packages/modules/app entry points.
- The caller asked for a partitioned review explicitly.

Below these, the single lens pass runs. Each partition costs about one full review, so fan-out is the skill's one automatic cost multiplier and fires on surface size alone, never on phrasing; a caller who asks to keep it inline suppresses it, and the report line is contract: `Fan-out suppressed; inline review over <N>-file diff`.


## Partition Strategy

Target **2–5 partitions** of roughly equal change weight – below 2, the partition is the whole diff, so run the single lens pass. First applicable strategy:

1. **By vertical slice** (preferred) – a feature- or concern-shaped group of files that together implement one demoable change end-to-end, the shape the `andthen:plan` skill uses for stories. Detect from the strongest signal, first match wins: active FIS Task IDs (`TI01`, `TI02`, … – files cited in or implied by one Implementation Task are one slice, the most reliable map for FIS-driven work); Plan Story IDs (`S01`, `S02`, … – one story, one slice, its files from the story's FIS); per-commit clustering (commits with distinct, coherent messages; squashed or "fix typos" / "address review" commits are not signals); FIS Work Areas; concept clustering (files sharing a feature name, module prefix, or a strongly connected sub-graph of the diff's import/reference graph).
2. **By package/module** (fallback) – when no slice signal resolves or the change is a uniform sweep: one partition per touched top-level package (`packages/<name>/`, `apps/<name>/`, `crates/<name>/`, Python packages, Go modules, SwiftPM targets).
3. **By language** (last resort) – when the diff mixes languages with disjoint review concerns (backend Go + frontend TypeScript + IaC YAML) and neither slice nor package partitioning produces useful groups.

Never partition by architectural layer (`api/`, `domain/`, `infra/`, `tests/`): cross-layer invariants – the deletion whose caller lives one layer up – are exactly what fan-out exists to surface, and horizontal slicing hides them between partitions. A diff whose only natural shape is layered falls back to package partitioning.


## Execution

1. Compute partitions and record the partition map in the report (slice name → file count) so the user can audit the split.
2. Each partition pass applies its resolved lenses' rubrics to its own file list; its matrix rows carry its own evidence, never orchestrator back-fill.
3. After every partition returns, a **boundary pass** attacks what no partition owns: `refactor-invariants.md` checks 1 (deletion completeness), 2 (resolve-once, consume-many), and 6 (parameter threading) across partition boundaries – the checks whose second site can live in another partition – and contradictions between partitions (slice A passes a surface slice B flags). Its findings tag `reviewer: Boundary Pass`, `scope_relation: primary`, `source_partition: boundary`.
4. Merge every partition's findings with the boundary pass's into one set, deduplicated by `(location, finding)` keeping the strongest framing, in the report's one `## Findings` section – never segregated by partition; the `reviewer` field keeps the boundary pass identifiable. The Findings Filter then runs once over the merged set, at Step 4.


## Reporting

Two lines in the Executive Summary when fan-out ran:

```markdown
Partition strategy: <vertical-slice | package | language>
Partition map: <slice-name>(<n> files), <slice-name>(<n> files), …
```
