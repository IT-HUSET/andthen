# The Prove-It Pattern – Test-First for Bugfixes

Canon: Feathers (characterization tests), Beck (test-first), the Beyonce Rule (Bender & Winters). "Prove-It Pattern" is AndThen's name for the failing-test-first bugfix flow.

A bug is fixed only when an automated test reliably fails *before* the fix and passes *after*, and that test stays as the regression guard. "Works on my machine" and "I stepped through it" are not proof.

## Flow

1. **Reproduce** – the smallest automated test expressing the defect. Run it: it fails, the output matches the reported symptom, and a stranger could identify the bug from the name and message. When it cannot be reproduced as a test, resolve *which* before touching production code: under-specified (ask the reporter for the missing conditions), environmental (capture the data/config/version as a fixture – a fixed clock, seeded RNG, canned config), or non-existent (close the report with the passing test as proof). **Do not fix before you can fail** – a patch without a failing test is a guess.
2. **Fix** – the minimum production change that flips red to green. No drive-by cleanup.
3. **Refactor on green** – tidy the code this fix just changed. Anything pre-existing is out of scope per the Boy Scout rule in CRITICAL RULES; standalone cleanup is the `andthen:simplify-code` skill's job.
4. **Keep the test.** Delete it only when the behavior it pins is intentionally removed (replace with a test for the new behavior) or the whole surface is deleted; the Anti-Cheat Invariant applies. Rename and relocate freely – "it's old" is how regressions return. A slow repro runs at the integration tier or behind a regression tag; slow beats absent.

## Characterization tests – for untested legacy code

When the bug sits in code with no coverage, pin current behavior before changing it: exercise the module with a realistic input, assert whatever it actually produces (even if wrong), watch it pass; then add the test asserting the *correct* behavior, watch it fail; fix; the correct test passes and the characterization test fails, so delete or update it. Refactoring untested code without this net is indistinguishable from rewriting it.

## Output contract

A `prove-it` report includes the **pre-fix failure output** (exact message, not "it failed"), **the minimum change** that flipped it green, and **the retained regression test** by name and file. Without the first item the bug was never proven to exist.
