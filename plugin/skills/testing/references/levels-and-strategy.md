# Levels and Strategy – Where to Test, What to Cover

Sources: Kent C. Dodds (*Testing Trophy*), Dave Farley (trust-boundary tests, feedback economics), Martin Fowler (pyramid critique).

Home mode: `strategy`. Also load for `write` and `tdd` when picking a level.


## The three levels – real criteria

"Unit = small, E2E = big" is useless for placing a specific behavior. Use trust boundaries and IO crossings.

| Level | Crosses | Controls | Time budget | Quantity |
|---|---|---|---|---|
| **Unit** | No trust boundary. No real IO. | Pure logic, calculations, transformations, policy rules, state machines, parsers. | Milliseconds; thousands run in seconds. | Many – most of the suite. |
| **Integration** | One trust boundary at a time (DB, filesystem, queue, HTTP to *your* services). | Module collaboration, persistence correctness, transaction semantics, adapters, infrastructure contracts. | 100ms–few seconds; hundreds run in a minute or two. | Moderate – the ones that matter. |
| **E2E** | Many boundaries, often including a real browser / full stack. | Critical user journeys, release-risk flows, cross-service contracts. | Seconds each; dozens take minutes. | Few – the ones you can't sleep without. |

**Trust boundary** = a line you don't own the other side of at runtime: filesystem, DB engine, third-party API, browser event loop, OS. Crossing one turns a unit test into an integration test – the file count is irrelevant.


## Shape: Testing Trophy, not Pyramid

The pyramid (massive unit, small integration, tiny E2E) made sense when integration tests were slow and brittle. Modern tooling (Testcontainers, Playwright) moved integration into the sweet spot.

```
         ╱╲       E2E         (few)
        ╱══╲      Integration (many)  ← trophy body
       ╱    ╲     Unit        (shape of the problem, not a ratio)
      ╱______╲    Static      (types, lint)
```

- **Integration is the default.** Real behavior in real conditions.
- **Unit** – for logic dense enough to merit direct coverage, or for permutations too slow/many to run at integration.
- **E2E** – journeys the business can't ship without. Small number, heavily maintained.
- **Static** (types, lint, dependency audits) – free on every keystroke, catches a class of bugs dynamic tests don't.

**Farley's caveat**: over-rotating to integration slows the feedback loop below the point developers run tests locally. Use the time budget column as a gate – if integration takes more than a couple of minutes, parallelize or demote some to unit.


## Signals you're at the wrong level

### "Unit" test that's actually integration
- Arrange wires up five collaborators.
- Heavy stubbing of non-external things.
- Assertions depend on concrete collaborator behavior.

**Fix**: promote to integration with real collaborators.

### "Integration" test that's actually E2E
- Spins up multiple services, a browser, a real queue.
- Covers a workflow across bounded contexts.

**Fix**: split. Contract tests at each boundary + per-service integration tests give faster, more localized failures than one fragile E2E.

### "E2E" test that's actually unit
- Asserts on a computed value that never leaves the backend.
- No user action simulated.

**Fix**: demote. Don't spend E2E budget on what a unit test can prove.


## Coverage strategy

Coverage *percentage* is a vanity metric. Coverage *at the point of greatest risk* is the goal.

Rank targets by:

1. **Blast radius of a silent failure** – money, data loss, security, legal, user-visible correctness.
2. **Change frequency** – hot files attract bugs; cold files are stable by virtue of not being touched.
3. **Structural risk** – deep inheritance, many callers, cycles → more failure modes.
4. **Reversibility** – idempotent / rollback-able code is cheaper to get wrong than code mutating durable state.

| Risk | Change | Priority |
|---|---|---|
| High | High | **1** – cover first, integration-heavy, tag as regression-critical. |
| High | Low | **2** – cover; unit may suffice if logic-dense. |
| Low | High | **3** – cover lightly; churn alone doesn't justify depth. |
| Low | Low | **4** – skip or rely on types/lint. |

Avoid "cover everything" – trains the team to ignore the suite. Avoid "cover only what's broken" – you discover hot spots by getting burned.


## Coverage theatre – refuse

- **Did-not-throw tests.** Smoke at best; no behavior proven.
- **100% line coverage without assertions on output semantics.** Execution ≠ verification.
- **Matrix tests over indistinct input combinations.** Runtime without confidence.
- **Mock-heavy tests that pass when collaborators break.** Rot silently; miss the refactors they should catch.


## Handoff: persistent E2E suites

This skill (`andthen:testing`) covers up to integration and handles *design* of an E2E suite. Running it interactively and discovering journeys lives with the `andthen:e2e-test` skill. Default to the `andthen:testing` skill for strategy and authoring; hand off when the work shifts to live browser interaction.
