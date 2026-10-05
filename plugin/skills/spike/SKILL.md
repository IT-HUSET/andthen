---
description: Answer one named design question by building a throwaway runnable spike, then report a verdict – evidence, not product. Not for shippable code (the andthen:implement-fix skill or the spec-driven path) nor screen/flow mockups (the andthen:ui-ux-design skill). Trigger on 'spike', 'prototype this', 'which approach is feasible'.
argument-hint: "[the one design question | approach A vs approach B]"
---

# Spike

A **spike** answers exactly one design question with throwaway runnable code.

## Input

`$ARGUMENTS` is the single design question to settle by building.

## Rules

- Print each recommended skill invocation as a complete, paste-ready line in the host's syntax, including its target path or request and required arguments.

- **Evidence, not product.** Spike code **never merges and is never reused directly**. Reusing it would carry the shortcuts a spike is allowed to take – skipped tests, hard-coded inputs, ignored edge cases – into production. The real implementation is authored fresh through the spec-driven path, informed by the verdict.
- **The caller's checkout is not yours.** Other work – the user's dirty files, a concurrent session's edits – lives in the checkout you were invoked from, so the spike runs in its own worktree with every file-writing tool bound to that root. Never stash, clean, switch, or stage the caller checkout: a stash or `git add -A` there swallows work that arrived after you looked. If isolation cannot be established, stop before writing anything.
- **Exempt from testing and review discipline.** The code is throwaway, so the test-first, review, and coverage gates do not apply: optimize for reaching the answer fast.
- **Bounded and honest.** Build the smallest thing that produces the deciding observation. Measure, don't assert: for "faster", produce numbers; for "feasible", produce it working or the concrete wall it hit. State what the spike did not cover.

## Workflow

### 1. Scope the question

An input that names no question building can answer is not a spike:

- an under-specified or open-ended requirements question – the `andthen:clarify` skill;
- a choice between architectural options – the `andthen:decide` skill;
- a screen, flow, or interaction-design question – the `andthen:ui-ux-design` skill.

Restate the one design question and the outcome that would answer it: a number, a working or not-working result, the failure mode. When a human invoked you, confirm it is the one to answer before building; a question an orchestrating skill passed pre-named needs no confirmation.

**Gate**: exactly one question, with a stated deciding outcome.

### 2. Open the spike worktree

1. Derive a kebab-case `<slug>` from the question.
2. Create it: `git worktree add <caller-root>/.agent_temp/spike/<slug> -b spike/<slug>`. The directory is untracked, and the caller's own `.agent_temp/` ignore already covers it. Any failure stops the run with the verbatim git error before a byte is written.
3. Bind every tool to that root with the host's worktree mechanism when it has one (Claude Code's `EnterWorktree`); without one, write through absolute paths under the spike root. Confirm with `git rev-parse --show-toplevel` from inside that every write lands there.

**Gate**: `spike/<slug>` is checked out in its own worktree, every file-writing tool resolves paths under it, and the caller checkout is untouched.

### 3. Build and run

Write the smallest spike that produces the deciding observation, run it, and capture the evidence: numbers, output, the error it hit.

Commit the files the spike owns by path, bypassing repo hooks, since throwaway code must not fight them: `git add <spike paths> && git commit --no-verify -m "spike: <question>"`. A question answered without code, with nothing to commit, is fine: note it in the Verdict's Evidence instead.

**Gate**: the question is answered by something that actually ran, and any spike code is committed on `spike/<slug>`.

### 4. Return and report

Remove the worktree and keep the branch: `git worktree remove <spike root>`, with `--force` only for build artifacts and scratch output that reproduce nothing. Report a removal failure; never work around it with a clean or checkout in the caller checkout. The spike stays on `spike/<slug>` as durable evidence, never merged.

Emit the Spike Verdict, as under Output.

**Gate**: the worktree is removed or its removal failure reported; `spike/<slug>` still exists, unmerged, carrying everything the Verdict's Evidence cites; the Spike Verdict is emitted.

## Output

```
## Spike Verdict

**Question**: <the one question>
**Answer**: <direct answer + the deciding observation (numbers / working / the wall it hit)>
**Evidence**: `spike/<slug>` – run with `<exact command>`
**Caveats**: <what the spike did not cover; what would differ in real implementation>
```

## Follow-up

When the decision is load-bearing, register it durably so it outlives the branch: an ADR through the `andthen:decide` skill, or, for a FIS-local choice, the decision stated in the FIS prose it governs, through the owning `andthen:plan` skill. Register the *decision and its evidence pointer*, never the code.
