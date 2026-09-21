---
description: Answer one named design question by building a throwaway runnable spike, then report a verdict – evidence, not product. Not for shippable code (the andthen:implement-fix skill or the spec-driven path) nor screen/flow mockups (the andthen:ui-ux-design skill). Trigger on 'spike', 'prototype this', 'which approach is feasible'.
argument-hint: "[the one design question | approach A vs approach B]"
---

# Spike

Answer exactly one named design question with throwaway runnable code – a **spike**.


`$ARGUMENTS` is the single design question to settle by building.


## INSTRUCTIONS

- **One question.** A spike answers one design question with a checkable outcome ("is approach A faster than B under load?", "can this library stream partial results?"). Name the single question in your first response; when a human invoked you, confirm it is the one to answer before building. An orchestrating skill that passed a pre-named question needs no confirmation.
- **Redirect what building cannot settle.** An input that names no answerable-by-building question, or bundles several, cannot be scoped as a spike:
  - an under-specified or open-ended requirements question – the `andthen:clarify` skill;
  - a choice between architectural options – the `andthen:architecture` skill in `--mode trade-off`;
  - a screen, flow, or interaction-design question – the `andthen:ui-ux-design` skill.
- **Evidence, not product**: spike code **never merges and is never reused directly** – it is deliberately isolated on its own branch and left there. Reusing it directly reintroduces the shortcuts a spike is allowed to take (skipped tests, hard-coded inputs, ignored edge cases) into production. Real implementation is authored fresh through the spec-driven path, informed by the verdict.
- **The caller's checkout is not yours.** Other work – the user's dirty files, a concurrent session's edits – lives in the checkout you were invoked from, so the spike runs in its own worktree and every file-writing tool is bound to that root. Never stash, clean, switch, or stage the caller checkout: a stash or `git add -A` there swallows work that arrived after you looked. If isolation cannot be established, stop before writing anything.
- **Exempt from testing and review discipline.** Because the code is throwaway, the usual test-first, review, and coverage gates do not apply – optimize for reaching the answer fast.
- **Bounded and honest.** Build the smallest thing that produces the deciding observation. Measure, don't assert – if the question is "faster", produce numbers; if "feasible", produce it working or the concrete wall it hit. State what the spike did not cover.


## WORKFLOW

### 1. Scope the question

Restate the one design question and the outcome that would answer it (a number, a working/not-working result, the failure mode). Apply the **One question** rule.

**Gate**: exactly one question, with a stated deciding outcome.

### 2. Open the spike worktree

The spike lives on a throwaway branch in its own worktree off the current HEAD.

1. Derive a kebab-case `<slug>` from the question. If `spike/<slug>` already exists, suffix a short disambiguator (`-2`, `-3`, …) and record it in the Verdict's Evidence.
2. Create it: `git worktree add <caller-root>/.agent_temp/spike/<slug> -b spike/<slug>` (an untracked directory the caller's own `.agent_temp/` ignore already covers). Any failure stops with `BLOCKED: could not create a spike worktree – <verbatim git error>` before a byte is written.
3. Bind every tool to that root: use the host's worktree mechanism when it has one (Claude Code's `EnterWorktree`; a shell `cd` moves only shell commands, so without such a mechanism write through absolute paths under the spike root). Confirm with `git rev-parse --show-toplevel` from inside that every write lands there.

**Gate**: `spike/<slug>` checked out in its own worktree; every file-writing tool resolves paths under it; the caller checkout untouched.

### 3. Build and run

Write the smallest spike that produces the deciding observation, run it, and capture the evidence (numbers, output, the error it hit). Commit the files the spike owns, by path, bypassing repo hooks since throwaway code must not fight them: `git add <spike paths> && git commit --no-verify -m "spike: <question>"`. A question answered without code (nothing to commit) is fine – note it in the Verdict's Evidence instead.

**Gate**: the question is answered by something that actually ran; any spike code is committed on `spike/<slug>`.

### 4. Return and report

Commit anything the Verdict's Evidence cites so the run stays reproducible, then remove the worktree and keep the branch: `git worktree remove <spike root>` (`--force` only for build artifacts and scratch output that reproduce nothing); a removal failure is reported, never worked around with a clean or checkout in the caller checkout. The spike stays on `spike/<slug>` as durable evidence – never merge it. Emit the **Spike Verdict** (see OUTPUT).

**Gate**: the worktree is removed or its removal failure reported; `spike/<slug>` still exists, unmerged, carrying everything the Verdict's Evidence cites; the Spike Verdict is emitted.


## OUTPUT

```
## Spike Verdict

**Question**: <the one question>
**Answer**: <direct answer + the deciding observation (numbers / working / the wall it hit)>
**Evidence**: `spike/<slug>` – run with `<exact command>`
**Caveats**: <what the spike did not cover; what would differ in real implementation>
```

When the decision is load-bearing, register it durably so it outlives the branch – an ADR via the `andthen:architecture` skill in `--mode trade-off`, or – for a FIS-local choice – the decision stated in the FIS prose it governs by the owning `andthen:spec` skill. Register the *decision and its evidence pointer*, not the code.
