# Diagnostic Methodology

Systematic debugging methodology for runtime failures, build breakages, regressions, and unclear bugs. Hypothesis-driven, evidence-first, parallel-investigation.

## Phase 1: Information Gathering

Gather evidence before forming hypotheses. Run diagnostic commands in parallel where possible:
- Error capture: collect error messages, stack traces, build logs, test output
- Timeline: when did the issue begin? What changed?
- Scope: isolated incident or recurring pattern?

## Phase 2: Hypothesis-Driven Root Cause Analysis

Apply "5 Whys" reasoning to each identified error:

1. **Why did this error occur?** – identify the immediate trigger
2. **Why did that trigger exist?** – find the underlying condition
3. **Why did that condition develop?** – trace state changes
4. **Why wasn't this prevented?** – examine validation gaps
5. **Why isn't this detectable earlier?** – identify monitoring opportunities

**Hypothesis ranking**: for each error, rank hypotheses by probability (most likely → possible → less likely). Fix in probability order; stop when the root cause is confirmed.

**Parallel investigation**: run multiple diagnostic streams simultaneously – don't wait for one hypothesis to be disproved before starting the next. Converge on the root cause from multiple angles.

**When the symptom is not reliably reproducible**, classify by failure pattern to guide investigation:
- **Timing-dependent** – race conditions, async ordering: add logging around concurrent paths, test with artificial delays
- **Environment-dependent** – config, OS, runtime differences: diff configs across environments, reproduce in each
- **State-dependent** – stale caches, uninitialized data, leaked state between tests: trace state mutations, check setup/teardown
- **Truly intermittent** – no pattern after classification: add telemetry, collect N occurrences before hypothesizing

## Phase 3: Build-Specific Techniques

For build, compile, dependency, and configuration failures specifically:

- **Dependency chain analysis**: trace error propagation through build dependencies; version conflicts are often the root cause of cascading failures
- **Clean build**: eliminate cached corruption before diagnosing – many issues disappear on a clean build, confirming cache corruption
- **Environment comparison**: diff the working vs failing environment systematically (env vars, tool versions, paths)
- **Minimal reproducible case**: strip down to the simplest failing configuration to isolate the issue

## Phase 4: Resolution

1. **Fix foundational issues first** – symptoms of the same root cause resolve together
2. **Apply fixes one at a time** – so you can attribute the resolution to a specific change
3. **Binary search when stuck** – isolate by systematically eliminating components; also apply the minimal-reproducible-case technique (Phase 3)

## Build Success Criteria

When the triage target is a broken build, done means – using the project's own build/test/run commands – a clean build, the full test suite, and a core-functionality smoke all pass with no warnings violating project standards.

## Output Format

### Issue Resolution Summary
Problem, root cause identified, and solution implemented.

### Root Cause Investigation
- **5 Whys chain**: step-by-step causation
- **Dependencies**: conflicts or mismatches found
- **Configuration**: environment/project settings issues

### Solution & Prevention
- **Fixes applied**: specific changes with rationale
- **Validation**: build/test results confirming resolution
- **Prevention**: monitoring or documentation improvements to prevent recurrence
