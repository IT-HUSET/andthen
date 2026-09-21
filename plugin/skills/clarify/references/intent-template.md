# Intent Document Template

The `andthen:clarify` skill's `intent.md` shape. Every section heading is contract – preserve verbatim. Feature scope writes `prd.md` from `prd-template.md` unless `--brief` is set.

One shape in two roles: what anyone can drop at `<specs-root>/<feature-name>/intent.md` without running the skill, and what `--brief` writes there. Step 1 detects it as a baseline and Step 3 folds it into the PRD (or amends it under `--brief`). The `Source` line and the `Decisions Log` are the skill's: a hand author may omit them, and the skill writes them so the next run folds settled answers instead of re-asking.

```markdown
# Intent: [Name]

> **Source**: [stable source identity, as the PRD carries it]

## Problem
[What is wrong or missing, and for whom]

## Proposed Outcome
[What counts as solved – observable, not a design]

## Affected Systems
- [Component, surface, team, or process expected to change]

## Constraints
- [Deadline, platform, compatibility, or policy limit]

## Open Questions
_Answer in place: replace the bullet with the decision, or leave it and it is asked again._
- [Question]? Recommended: [option] – [one-line why]. Alternatives: [option]; [option].

## Decisions Log
| Decision | Rationale | Date |
|----------|-----------|------|
| [What the interview settled] | [Why] | [YYYY-MM-DD] |
```
