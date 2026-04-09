# Minimal Feature Implementation Specification Template

> For THIN stories only — used by `andthen:spec-plan` when the orchestrator writes FIS directly.
> Target: 30-60 lines. Same structure as the full FIS template but stripped to essentials.


# {Story Name}

## Feature Overview and Goal
{1-2 sentences from plan story scope}


## Success Criteria (Must Be TRUE)
{Acceptance criteria from plan, as checkboxes}

### Health Metrics (Must NOT Regress)
- [ ] Existing tests continue to pass
- [ ] No regressions introduced


## Scope & Boundaries
### In Scope
{From plan story scope}
### What We're NOT Doing
{Key exclusions from plan context}


## Architecture Decision
**We will**: {approach} -- {rationale from research brief}


## References & Constraints
### Documentation & References
{Relevant file:line references from research brief file map}
### Constraints & Gotchas
{Relevant constraints from research brief}


## Implementation Plan
### Execution Groups
#### G1: {Task Group} <- [depends: none]
- [ ] **TI01** {Outcome from acceptance criteria}
  - {Context from research brief}
  - **Verify**: {Behavioral assertion}

### Testing Strategy
- [G1] {Key test scenario from acceptance criteria}

### Validation
> Standard validation (TV01-TV04) handled by exec-spec.


## Final Validation Checklist
- [ ] All success criteria met
- [ ] All tasks completed and verified
- [ ] No regressions introduced
