# The Prove-It Pattern – Test-First for Bugfixes

Canon: Feathers (characterization tests), Beck (test-first), the Beyonce Rule (Bender & Winters).

A bug is fixed only when an automated test reliably fails *before* the fix and passes *after*, and that test stays as the regression guard.

## Workflow

1. **Reproduce** – write the smallest automated test expressing the defect and run it. It fails, the output matches the reported symptom, and a stranger could identify the bug from its name and message. When the defect cannot be reproduced as a test, resolve which case it is before touching production code:
   - under-specified – ask the reporter for the missing conditions;
   - environmental – capture the data, config, or version as a fixture (a fixed clock, a seeded RNG, canned config);
   - non-existent – close the report with the passing test as proof.
2. **Fix** – the minimum production change that flips red to green. Gate: the repro test is green and the rest of the suite still passes.
3. **Refactor on green** – tidy the code this fix changed, plus Boy Scout tidies. A Boy Scout tidy is a behavior-preserving fix to a smell or problem in a function or doc section the change edits, or to a minor one elsewhere when the fix is mechanical, touches only comments or docs, or is covered by checks that would catch a mistake in it. In an edited function, an obvious small bug fixed under a test that fails first is a tidy too. What no tidy can fix is reported.
4. **Keep the test**; the Anti-Cheat Invariant applies. Rename and relocate freely – "it's old" is how regressions return. A slow repro runs at the integration tier or behind a regression tag: slow beats absent. Gate: the regression test is named with its file.

## Characterization tests – for untested legacy code

When the bug sits in code with no coverage, pin current behavior with a characterization test before changing it. Then add the test asserting the *correct* behavior and watch it fail. Fix: the correct test passes and the characterization test fails, so delete or update it.

## Output contract

A `prove-it` report includes the **pre-fix failure output** (the exact message, not "it failed"), **the minimum change** that flipped it green, and **the retained regression test** by name and file. Without the first, the bug was never proven to exist.
