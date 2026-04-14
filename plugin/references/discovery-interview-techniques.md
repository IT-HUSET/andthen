# Discovery Interview Techniques

Use this when discovery answers are vague, contradictory, overly solution-driven, or too shallow to turn into a good spec or plan.

## Interview Principles

- **Listen, then probe**: follow the user's answer instead of racing through a checklist
- **Chase the tension**: dig where the user sounds uncertain, frustrated, or unusually opinionated
- **Challenge respectfully**: test assumptions without turning the conversation adversarial
- **Stay concrete**: examples and scenarios beat abstractions
- **Control scope drift**: explore tangents briefly, then bring the conversation back to the decision at hand

## Core Probing Techniques

### The Five Whys
Use when the user states a solution instead of the real problem.

Goal:
- move from requested feature to underlying need

Prompt shape:
- Why is this needed?
- Why does that matter?
- Why now?

Stop once the answer reaches a stable business or user need. Do not keep drilling after the problem is already clear.

### Scenario Testing
Use when a requirement sounds reasonable in the abstract but may break in practice.

Ask:
- What happens in a concrete example?
- What changes on day one versus day one hundred?
- What happens when two conditions are true at once?

This is the fastest way to surface edge cases, hidden actors, and missing workflow steps.

### Extremes and Boundaries
Use when scope is fuzzy or the user is asking for too much.

Ask:
- What is the smallest version that still delivers value?
- What breaks if scale grows 10x?
- What if the user has only 30 seconds?

This exposes what is essential versus ornamental.

### Trade-off Forcing
Use when everything is "important."

Ask:
- If we could only ship three things, which three?
- Would you prefer A done well or A and B done adequately?
- What would you cut to ship a month earlier?

Forced scarcity reveals true priorities faster than generic prioritization questions.

### Laddering
Use when the answer is either too specific or too vague.

- **Upward**: feature -> benefit -> need
- **Downward**: need -> criteria -> observable behavior

Examples:
- "Export CSV" -> "custom reporting" -> "reporting flexibility"
- "It should be fast" -> "under 2 seconds" -> "for first search results"

### Perspective Shift
Use when discovery is stuck in one happy-path viewpoint.

Ask from another role:
- skeptical user
- new team member
- admin/operator
- support engineer

Different roles surface different requirements and risks.

## Creative Escape Hatches

Use one of these briefly when the user is stuck:

- **Inversion**: what would make this fail badly?
- **Assumption reversal**: what if the assumption everyone is making is false?
- **What-if scenario**: what if the main constraint disappeared or flipped?

Do not run every creativity technique. Use one to unlock the conversation, then return to concrete requirements.

## Managing Difficult Moments

### When Ideas Are Vague
- ask for one concrete example
- ask how they handle it today
- ask what the wrong version would look like

### When Scope Keeps Growing
- anchor on MVP or first release
- ask what problem each new addition actually solves
- note future ideas explicitly, then refocus

### When Contradictions Appear
- surface the contradiction directly
- ask which requirement wins when they conflict
- test the conflict with a concrete scenario

### When the User Defers Everything
- offer 2-3 concrete options with trade-offs
- recommend a default and ask what feels wrong about it
- accept that some decisions genuinely do not matter to the user
