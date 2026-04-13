# Anti-Rationalization

Use this reference when you notice yourself talking your way out of load-bearing discipline: clarifying scope, writing tests, verifying work, or keeping changes surgical.

Keep this as a **shared reference**, not duplicated inside every skill. Link it only from skip-prone moments.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "This is too small for a spec." | Small work still needs explicit scope and acceptance criteria. A short artifact is enough; no artifact is not. |
| "I'll verify after the next group." | Defects compound across dependent work. Verification is cheapest before more work builds on a bad assumption. |
| "I'll just fix this adjacent issue too." | Scope creep hides regressions, muddies diffs, and creates false confidence that more was safely covered than actually was. |
| "I know this API from memory." | Confidence decays more slowly than accuracy. Framework patterns, signatures, and best practices change. Verify before baking stale patterns into code. |
| "This failing check is probably unrelated." | Stop-the-line applies. Pushing past a failing test or build makes every later result less trustworthy. |
| "I'll update status/docs/checklists at the end." | Deferred bookkeeping drifts from reality. The source of truth is most reliable when updated immediately at the gate where work is verified. |

## Use It For

- Implementation work that can quietly skip verification
- Bug fixes that tempt you to patch symptoms
- Refactors that start widening in scope
- Orchestrated workflows where status updates or gates feel "optional"
