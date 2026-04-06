# Discovery Interview Techniques

Techniques for conducting effective requirements discovery interviews. Use these to dig deeper when surface-level answers leave gaps, when the user is unsure what they want, or when you need to explore the problem space more thoroughly.

> **Context**: This reference supports the discovery interview phase of requirements clarification. It complements question checklists (what to ask) with probing techniques (how to go deeper) and creative exploration (how to unstick).


## Interview Principles

Guide your interview stance — not rigid rules, but defaults to return to:

- **Listen first** — Let the user's answers guide the next question. Don't race through a checklist
- **Follow the energy** — When the user shows excitement or concern about something, dig deeper there
- **Challenge respectfully** — Question assumptions constructively: "What if that turned out not to be true?"
- **Embrace relevant tangents** — Unexpected directions often reveal hidden requirements. Follow briefly, then redirect
- **Build collaboratively** — Frame it as joint exploration ("Let's think through..."), not interrogation


## Probing Techniques

Use these when initial answers are too high-level, when you suspect unstated assumptions, or when you need to reach the real requirement beneath the surface request.

### The Five Whys
Dig from surface request to core motivation by repeatedly asking *why*.

```
User: "We need a dashboard."
→ Why? "So managers can see team progress."
→ Why is that important? "They're making staffing decisions blindly."
→ Why? "No visibility into who's blocked or idle."
→ Why does that matter now? "We doubled the team and the old standup model broke."
→ Core need: Visibility into team capacity and blockers at scale — not just "a dashboard."
```

**When to use**: When the stated requirement feels like a solution rather than a problem. The real requirement often lives 2-3 "whys" deeper.

### Scenario Testing
Test requirements against concrete situations to expose gaps and implicit assumptions.

- "What happens when a user does X but Y is also true?"
- "Walk me through what happens on day one vs. day 100"
- "What if the user has done this before vs. never?"
- "What does this look like with 5 users? 5,000?"

**When to use**: When requirements read well in the abstract but you suspect they'll break under real conditions.

### Extremes & Boundaries
Push requirements to their limits to find where they break or change character.

- "What if this problem got 10x worse — would the same solution work?"
- "What's the simplest version that still delivers value?"
- "What if you had zero budget for this?"
- "What if users could only interact with this for 30 seconds?"

**When to use**: When scope is fuzzy or when you need to find the essential core of a requirement.

### Trade-off Forcing
Force prioritization by creating artificial scarcity. Surfaces which requirements are truly essential vs. nice-to-have.

- "If you could only have 3 of these features, which three?"
- "Would you rather have A done well or both A and B done adequately?"
- "If we had to launch in one week, what would you keep?"
- "Which of these would you cut to ship a month earlier?"

**When to use**: When everything is "high priority" or when the user hasn't distinguished must-haves from nice-to-haves.

### Laddering
Move between abstraction levels — from features to benefits to underlying needs, or vice versa.

**Upward** (feature → benefit → need):
```
"You want export to CSV" → "So you can analyze data in Excel"
  → "So you can build custom reports" → "Because the built-in reports don't cover your use cases"
  → Need: Flexible, customizable reporting — CSV export is one possible solution
```

**Downward** (need → criteria → specifics):
```
"It needs to be fast" → "What does fast mean? Under 2 seconds? Instant?"
  → "Which operations specifically?" → "Is that first load or subsequent loads?"
```

**When to use**: Upward when a user requests a specific solution (to find the real need). Downward when a user states an abstract quality (to make it testable).


## Creative Exploration Techniques

Use these when the problem space is poorly understood, when the user is stuck, or when you want to surface requirements that nobody has thought of yet. Pick one technique, run it briefly, extract insights — don't try to use all of them.

### What If Scenarios
Pose provocative hypotheticals that remove constraints or change the frame. The goal isn't the hypothetical answer — it's the assumptions it reveals.

- "What if users could undo any action at any time — would that change the workflow?"
- "What if this had to work completely offline?"
- "What if the primary user was a complete beginner?"
- "What if you had to charge users per action — which actions would be worth paying for?"

**Extract**: Which assumptions changed? What does that reveal about the real requirements?

### Reversal / Inversion
Solve the opposite problem first, then invert back. Often easier to identify what would guarantee failure.

- "How could we make this experience as frustrating as possible?"
- "What would guarantee users abandon this after day one?"
- "What's the worst possible version of this feature?"

**Extract**: Invert each "worst" answer into a requirement. "Confusing navigation" → clear, predictable navigation is a requirement.

### How Might We (HMW)
Reframe problems as open-ended opportunity questions. Shifts from "we can't" to "what if we could."

Format: *"How might we [verb] for [user] so that [outcome]?"*

- "How might we make the waiting time feel productive?"
- "How might we help new users feel confident on their first task?"
- "How might we turn this constraint into a feature?"

**When to use**: When the user frames everything as obstacles or limitations. HMW reframing often uncovers requirements hiding behind complaints.

### Assumption Reversal
List assumptions about the problem, then systematically reverse each one. The reversals that feel most uncomfortable often point to hidden requirements.

```
Assumption: "Users will read the instructions"
  → Reversal: "No user will ever read instructions"
  → Requirement: The system must be self-explanatory without documentation

Assumption: "Data will be entered correctly"
  → Reversal: "Every input will contain errors"
  → Requirement: Robust validation with clear correction guidance
```

**When to use**: When requirements feel "obvious" — assumption reversal surfaces the things everyone takes for granted.

### SCAMPER for Feature Discovery
Systematic modification of an existing concept or workflow. Useful when augmenting an existing system.

- **Substitute**: What if we replaced [component] with something else?
- **Combine**: What if we merged [feature A] and [feature B]?
- **Adapt**: What works well in [analogous domain] that we could adapt?
- **Modify**: What if we amplified [aspect]? Minimized it?
- **Put to other use**: Who else could benefit from this? What else could this data/feature enable?
- **Eliminate**: What if we removed [component] entirely — would anyone notice?
- **Reverse**: What if the user/system roles were swapped? What if the order was reversed?

**When to use**: When adding features to an existing system or when the user says "it's like X but different."

### Role Perspective Shift
Explore the problem from a different stakeholder's viewpoint. Each perspective surfaces different requirements.

- "If you were the most skeptical user, what would make you leave?"
- "If you were onboarding a new team member, what would confuse them?"
- "If you were the admin responsible for this, what would worry you?"
- "If you were a competitor, how would you attack this product's weakness?"

**When to use**: When requirements are only capturing the happy-path perspective of the primary user.


## Managing Difficult Interview Moments

### When Ideas Are Vague
The user can't articulate what they want clearly.

**Techniques:**
- Ask for a **specific example**: "Can you walk me through one concrete scenario where this would be used?"
- Ask for **comparison**: "Is this more like X or more like Y?"
- Ask what they **don't** want: "What would the wrong version of this look like?"
- Ask about **existing workarounds**: "How do you handle this today, even if it's manual or messy?"

### When Scope Keeps Growing
Every answer introduces new features and capabilities.

**Techniques:**
- **MVP anchor**: "Is that essential for the first version, or is it future vision?"
- **Launch constraint**: "If we had to ship in 30 days, would this make the cut?"
- **Value test**: "What user problem does this specific addition solve?"
- **Defer explicitly**: Note it as a future consideration so the user feels heard, then refocus

### When Contradictions Appear
Earlier answers conflict with later ones.

**Techniques:**
- **Surface without judging**: "Earlier you mentioned X, and now Y — help me understand how these fit together"
- **Ask which wins**: "When X and Y conflict, which takes priority?"
- **Test with scenario**: "In situation Z, would you want X behavior or Y behavior?"
- Contradictions often mean the user is thinking about different contexts — help them articulate the distinction

### When the User Defers Everything
"Whatever you think is best" / "I don't know, you decide."

**Techniques:**
- **Offer concrete options**: "Here are two approaches — A does X, B does Y. Which feels more right?"
- **Use defaults**: "A common approach is X. Does that sound right, or does something feel off?"
- **Probe the hesitation**: "What's making this hard to decide? Is there uncertainty about [specific aspect]?"
- Some decisions genuinely don't matter to the user — accept that and note your recommendation with rationale
