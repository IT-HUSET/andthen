---
description: Answer one named design question by building a throwaway runnable spike, then report a verdict – evidence, not product. Trigger on 'spike', 'prototype this', 'answer by building', 'which approach is faster/feasible'. Not for shippable code – that is the `andthen:quick-implement` skill or the spec/exec chain; not for screen/flow design or interactive mockups – that is the `andthen:ui-ux-design` skill.
argument-hint: "[the one design question | approach A vs approach B]"
---

# Spike

Answer exactly one named design question with throwaway runnable code – a **spike**. The spike is evidence, not product: the *decision* flows onward through the normal spec/exec chain, the code does not.


## VARIABLES

QUESTION: $ARGUMENTS – the single design question to settle by building.


## INSTRUCTIONS

- **One question.** A spike answers one design question with a checkable outcome ("is approach A faster than B under load?", "can this library stream partial results?"). If the input names no answerable-by-building question, or bundles several, you cannot scope a spike – redirect: an under-specified or open-ended requirements question to the `andthen:clarify` skill; a choice between architectural options to the `andthen:architecture` skill in `--mode trade-off`; a screen, flow, or interaction-design question to the `andthen:ui-ux-design` skill in `--mode wireframes`. Name the single question in your first response; when a human invoked you, confirm it is the one to answer before building. An orchestrating skill that passed a pre-named question needs no confirmation.
- **Evidence, not product** (hard rule): spike code **never merges and is never reused directly**. It exists to produce an answer under real execution, not to become the implementation – so it is deliberately isolated on its own branch and left there. Reusing it directly reintroduces the shortcuts a spike is allowed to take (skipped tests, hard-coded inputs, ignored edge cases) into production. Real implementation is authored fresh through the spec/exec chain, informed by the verdict.
- **Exempt from testing and review discipline.** Because the code is throwaway, the usual test-first, review, and coverage gates do not apply – optimize for reaching the answer fast. This exemption is the whole point of quarantining the spike on a branch; it is *only* safe because the code never ships.
- **Bounded and honest.** Build the smallest thing that produces the deciding observation. Measure, don't assert – if the question is "faster", produce numbers; if "feasible", produce it working or the concrete wall it hit. State what the spike did not cover.


## WORKFLOW

### 1. Scope the question

Restate the one design question and the outcome that would answer it (a number, a working/not-working result, the failure mode). Apply the **One question** rule – redirect rather than build if it does not resolve to a single answerable-by-building question. Confirm with the user unless the question was passed pre-named by an orchestrating skill.

**Gate**: exactly one question, with a stated deciding outcome.

### 2. Open the spike branch

The spike lives on a throwaway branch off the current HEAD so it stays isolated and never touches the working line.

1. Record the current branch: `git rev-parse --abbrev-ref HEAD`.
2. Derive a kebab-case `<slug>` from the question. If `spike/<slug>` already exists, suffix a short disambiguator (`-2`, `-3`, …) and record it in the Verdict's Evidence.
3. **Clean-tree guard**: run `git status --porcelain`. If the tree is dirty, announce and stash it under a named stash (`git stash push -u -m spike/<slug>`) before branching, so the spike's `git add -A` cannot swallow caller work onto the spike branch; it is restored with `git stash pop` after the original branch is checked back out (same base commit, so the pop is conflict-free). Any stash failure stops with `BLOCKED: could not stash uncommitted changes on <branch> – commit or stash before spiking`.
4. Branch: `git checkout -b spike/<slug>`.

**Gate**: on `spike/<slug>`, original branch recorded, any dirty tree stashed.

### 3. Build and run

Write the smallest spike that produces the deciding observation, run it, and capture the evidence (numbers, output, the error it hit). Skip tests, review, and polish – this code is throwaway. Commit it as the primary source, bypassing repo hooks since throwaway code must not fight them: `git add -A && git commit --no-verify -m "spike: <question>"`. A question answered without code (nothing to commit) is fine – note it in the Verdict's Evidence instead.

**Gate**: the question is answered by something that actually ran; any spike code is committed on the branch.

### 4. Return and report

Clean the spike tree before leaving it – a dirty tree must not ride the checkout onto the working line. Default to committing any remaining spike changes (`git add -A && git commit --no-verify -m "spike: <question>"`) so the code the Verdict's Evidence cites stays reproducible; discard only leftovers not needed to reproduce the Answer – build artifacts, scratch output – e.g. `git clean -fd`, never `git checkout -- .` over tracked code the Evidence points at. Restore the working line: `git checkout <original-branch>`; a checkout failure stops with `BLOCKED: could not restore <original-branch> from spike/<slug> – <verbatim git error>` (the caller's stash stays intact for manual recovery). Then, once on the original branch, restore any stashed caller work with `git stash pop` – conflict-free at the same base commit; a pop failure stops with `BLOCKED: could not restore stashed changes on <original-branch> – resolve the stash manually`. The spike stays on `spike/<slug>` as durable evidence – never merge it. Emit the **Spike Verdict** (see OUTPUT).


## OUTPUT

```
## Spike Verdict

**Question**: <the one question>
**Answer**: <direct answer + the deciding observation (numbers / working / the wall it hit)>
**Evidence**: `spike/<slug>` – run with `<exact command>`
**Caveats**: <what the spike did not cover; what would differ in real implementation>
```

When the decision is load-bearing, register it durably so it outlives the branch – a FIS decision Note via the `andthen:ops` skill (`update-fis <fis> decision-note`), or an ADR via the `andthen:architecture` skill in `--mode trade-off`. Register the *decision and its evidence pointer*, not the code. Real implementation routes through the normal spec/exec chain.
