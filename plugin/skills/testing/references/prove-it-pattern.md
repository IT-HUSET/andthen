# The Prove-It Pattern — Test-First for Bugfixes

Sources: Addy Osmani (Prove-It Pattern), Michael Feathers (*Working Effectively with Legacy Code*), Kent Beck (test-first discipline).

Home mode: `prove-it`. Use for any bug report, disputed behavior, or regression concern.


## Premise

*"Works on my machine" is not proof.* Neither is *"I stepped through it and it looked right."*

A bug is fixed only when an automated test reliably fails *before* the fix and passes *after*. That test stays in the suite as the regression guard.

Reinforced by the **Beyonce Rule**: *"If you liked it, you should have put a test on it."* Behavior anyone depends on must be pinned — otherwise a future refactor silently breaks it (cf. Hyrum's Law).


## Flow

### 1. Reproduce — turn the report into a failing test

Smallest automated test that expresses the defect. Run it. Confirm:

- It fails.
- The output matches the reported symptom (wrong value, exception, 500, etc.).
- A stranger could identify the bug from the test name and failure message.

If you cannot reproduce it as a test, resolve *which* before touching production code:

1. **Under-specified** — ask the reporter for missing conditions.
2. **Environmental** (data, config, version) — capture the condition as a fixture.
3. **Doesn't exist** — close the report with the passing test as proof.

**Do not fix before you can fail.** A patch without a failing test is a guess.

### 2. Fix — minimum change to flip red to green

Same as `tdd` mode:
- Smallest production change that turns the red test green.
- No drive-by cleanup. That's a separate commit.

### 3. Refactor — on green

Boy Scout Rule, bounded to files already touched: fix a typo, tighten an adjacent assertion, remove obvious dead code. Keep the blast radius reviewable without re-loading context.

### 4. Keep the test

The bug test is a regression guard. It stays. Delete only when:

- The behavior it pins is intentionally removed (replace with a test for the new behavior).
- The entire surface is deleted.

Rename and relocate freely. "It's old" is not a reason — that's how regressions return.


## Characterization tests — for untested legacy code

Feathers' technique. When the bug is in code with no coverage, pin current behavior before changing it.

1. Exercise the module with a realistic input.
2. Assert whatever it actually produces — even if wrong.
3. Run it. It passes. Current behavior is now characterized.
4. Add a test asserting the *correct* behavior. It fails.
5. Fix the code. Correct test passes; characterization test now fails (it pinned wrong behavior).
6. Delete or update the characterization test. Keep the correct one.

**Do not refactor untested code without a characterization safety net.** Refactoring untested code is indistinguishable from rewriting it.


## Anti-rationalization table

| Excuse | Rebuttal |
|---|---|
| "I already see the bug — I'll just fix it." | Five minutes for a failing test buys permanent regression protection. Skipping costs an hour when it regresses. |
| "Environmental — can't easily reproduce in a test." | Capture the environment as a fixture (fixed clock, seeded RNG, canned config). If you can fix it precisely, you can test it precisely. |
| "I'll add the test in a follow-up PR." | You won't. You already know this. |
| "Too slow for every build." | Run it at the integration tier or behind a regression tag. Slow beats absent. |
| "One-off — nobody will hit it again." | Then a five-second test protects you from being wrong about that. |


## Output contract

A `prove-it` report must include:

- **Pre-fix failure output** — exact message, not "it failed".
- **The minimum change** that flipped it green.
- **The retained regression test** — name and file location.

Without the first item, you have not proven the bug existed, let alone fixed it.
