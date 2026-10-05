# The Prove-It Pattern – Test-First for Bugfixes

Canon: Feathers (characterization tests), Beck (test-first), the Beyonce Rule (Bender & Winters). "Prove-It Pattern" is AndThen's name for the failing-test-first bugfix flow.

A bug is fixed only when an automated test reliably fails *before* the fix and passes *after*, and that test stays as the regression guard. "Works on my machine" and "I stepped through it" are not proof.

## Workflow

1. **Reproduce** – write the smallest automated test expressing the defect and run it. It fails, the output matches the reported symptom, and a stranger could identify the bug from its name and message. **Do not fix before you can fail**: a patch without a failing test is a guess. When the defect cannot be reproduced as a test, resolve which case it is before touching production code:
   - under-specified – ask the reporter for the missing conditions;
   - environmental – capture the data, config, or version as a fixture (a fixed clock, a seeded RNG, canned config);
   - non-existent – close the report with the passing test as proof.
2. **Fix** – the minimum production change that flips red to green. Gate: the repro test is green and the rest of the suite still passes.
3. **Refactor on green** – tidy the code this fix changed, plus Boy Scout tidies. A Boy Scout tidy in a file the change touches is small and behavior-preserving, or fixes an obvious small bug under a test that fails first. A larger issue is reported.
4. **Keep the test**; the Anti-Cheat Invariant applies. Rename and relocate freely – "it's old" is how regressions return. A slow repro runs at the integration tier or behind a regression tag: slow beats absent. Gate: the regression test is named with its file.

## Characterization tests – for untested legacy code

When the bug sits in code with no coverage, pin current behavior with a characterization test before changing it. Then add the test asserting the *correct* behavior and watch it fail. Fix: the correct test passes and the characterization test fails, so delete or update it. Refactoring untested code without this net is indistinguishable from rewriting it.

## Output contract

A `prove-it` report includes the **pre-fix failure output** (the exact message, not "it failed"), **the minimum change** that flipped it green, and **the retained regression test** by name and file. Without the first, the bug was never proven to exist.
