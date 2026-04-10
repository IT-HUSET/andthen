# Structured Output Protocols

Named communication formats for common situations during implementation. Use these when you encounter ambiguity, scope boundaries, or missing requirements — they surface uncertainty to the user rather than hiding it.


## CONFUSION

When requirements are ambiguous or contradict existing patterns, surface it with options:

```
CONFUSION:
[description of the ambiguity]

Options:
A) [first approach]
B) [second approach]
C) Ask [stakeholder/user]

-> Which approach?
```

**Why**: Prevents silent guessing. A wrong guess costs more than a 30-second pause.


## NOTICED BUT NOT TOUCHING

When you discover issues outside the current scope, surface them without acting:

```
NOTICED BUT NOT TOUCHING:
- [issue] (unrelated to this task)
- [issue] (out of scope)
-> Want me to create tasks for these?
```

The inverse — documenting intentional non-changes:

```
THINGS I DIDN'T TOUCH (intentionally):
- [file/issue]: [why it was left alone]
```

**Why**: Prevents scope creep while preserving information. Issues surfaced now can be addressed later; issues silently ignored are lost.


## MISSING REQUIREMENT

When behavior is undefined and a decision is needed before implementation can proceed:

```
MISSING REQUIREMENT:
[what is undefined — e.g., "duplicate title behavior not specified"]

Options:
A) [concrete option]
B) [concrete option]
C) [concrete option]

-> Which behavior?
```

**Why**: Makes implicit requirements explicit. Every undefined behavior the model invents is a silent assumption that may be wrong.
