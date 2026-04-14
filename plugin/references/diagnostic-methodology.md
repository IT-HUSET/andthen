# Diagnostic Methodology

Shared debugging methodology for systematic root cause analysis. Used by `build-troubleshooter` (build failures, configuration errors) and `triage` (runtime failures, regressions, unclear bugs).


## Phase 1: Information Gathering

Gather evidence before forming hypotheses. Run diagnostic commands in parallel where possible:
- Project context: read CLAUDE.md and any troubleshooting guidelines
- Error capture: collect error messages, stack traces, build logs, test output
- Timeline: when did the issue begin? What changed?
- Scope: isolated incident or recurring pattern?


## Phase 2: Hypothesis-Driven Root Cause Analysis

Apply "5 Whys" reasoning to each identified error:

1. **Why did this error occur?** — identify the immediate trigger
2. **Why did that trigger exist?** — find the underlying condition
3. **Why did that condition develop?** — trace state changes
4. **Why wasn't this prevented?** — examine validation gaps
5. **Why isn't this detectable earlier?** — identify monitoring opportunities

**Hypothesis ranking**: for each error, rank hypotheses by probability (most likely → possible → less likely). Fix in probability order; stop when the root cause is confirmed.

**Parallel investigation**: run multiple diagnostic streams simultaneously — don't wait for one hypothesis to be disproved before starting the next. Converge on the root cause from multiple angles.


## Phase 3: Resolution

1. **Fix foundational issues first** — symptoms of the same root cause resolve together
2. **Test each fix incrementally** — verify the fix resolves the issue without introducing regressions
3. **Binary search when stuck** — isolate by systematically eliminating components
4. **Minimal reproducible case** — strip down to the simplest failing configuration when the issue is hard to locate


## Cross-Agent Communication (when escalating)

```
ISSUE: [specific error description]
CONTEXT: [command, environment, recent changes]
HYPOTHESIS: [most likely root cause]
REQUIRED_FIX: [specific action needed]
VALIDATION: [how to confirm fix succeeded]
```


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
