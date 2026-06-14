# Spec Flow Example – Sub-Wave Batching

Worked illustration of Step 5 sub-wave batching for the `andthen:plan` skill.

```
8-story plan (after Step 3 Consolidation Pass) → 8 FIS files

Step 5 (MAX_PARALLEL=4):
  Sub-wave 1: spec-S01, spec-S02, spec-S03, spec-S04 (parallel)
  Sub-wave 2: spec-S05, spec-S06, spec-S07, spec-S08 (parallel)
  → After each sub-wave: re-read plan.json and verify each story's fis + status landed
    (spec sub-agents drive the ops writes; orchestrator only repairs on miss)
```
