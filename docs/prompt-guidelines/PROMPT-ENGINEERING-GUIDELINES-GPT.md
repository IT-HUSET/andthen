# GPT-Specific Prompt Engineering Guidelines

GPT-5.x+ specific behaviors, optimizations, and patterns.

**See Also**: [General Guidelines](PROMPT-ENGINEERING-GUIDELINES.md) - Model-agnostic core patterns

**Last Updated**: 2026-03-03

---

## GPT-5.x Model Family

| Model | ID | Status | Context | Max Output | Knowledge Cutoff | Input/Output (per 1M) |
|-------|-----|--------|---------|------------|-------------------|----------------------|
| GPT-5.4 | `gpt-5.4` | **Recommended default** | 1M* | 128K | Aug 2025 | $2.50/$15 |
| GPT-5.4 Pro | `gpt-5.4-pro` | Maximum capability | 1M* | 128K | Aug 2025 | TBD |
| GPT-5.3-Codex | `gpt-5.3-codex` | Dedicated agentic coding | 1M* | 128K | Dec 2025 | $3/$12 |
| GPT-5.2-Codex | `gpt-5.2-codex` | Previous-gen agentic coding | 400K | 128K | Sep 2025 | TBD |
| GPT-5.2 | `gpt-5.2` | General purpose | 256K | 128K | Sep 2025 | $3/$12 |
| GPT-5.1 | `gpt-5.1` | Legacy | 256K | 128K | Mar 2025 | $2/$8 |
| GPT-5 | `gpt-5` | Legacy | 128K | 128K | Oct 2024 | $2/$8 |

\* Extended context (>272K input tokens) requires the experimental `model_context_window` parameter and is billed at **2x input / 1.5x output** for the full session.

> **Retired models** (Feb 2026): o4-mini, GPT-4o, GPT-4.1, GPT-4.1 mini. Do not use for new development.

### GPT-5.4 vs GPT-5.3-Codex

GPT-5.4 is a **unified frontier model** that absorbed GPT-5.3-Codex coding capabilities. It marginally beats GPT-5.3-Codex on SWE-Bench Pro (57.7% vs 56.8%) at lower cost.

GPT-5.3-Codex retains a small edge on **Terminal-Bench 2.0** (77.3% vs 75.1%) — relevant for terminal-heavy/CLI-scripting workflows. For most tasks, **GPT-5.4 is the recommended default**.

### Core Capabilities

The GPT-5.x family represents substantial leaps in:
- Agentic task performance
- Coding capabilities
- Raw intelligence and reasoning
- Steerability and instruction following
- Computer use (GPT-5.4: 75% OSWorld-Verified)

See also: [Model & Effort Selection Guide](../../MODEL-EFFORT-SELECTION-GUIDE.md) for task-specific model/effort recommendations.

---

## Controlling Agentic Eagerness

GPT-5 operates on spectrum from highly autonomous to tightly controlled.

### Less Eager (Faster, More Controlled)

**Lower `reasoning_effort`**:
- Reduces exploration depth
- Improves efficiency and latency
- Many workflows work consistently at medium or low

**Define clear criteria**:
```xml
<context_gathering>
Goal: Get enough context fast. Parallelize discovery, stop as soon as you can act.

Method:
- Start broad, fan out to focused subqueries
- Launch varied queries in parallel; read top hits per query
- Deduplicate, cache; don't repeat queries
- Avoid over-searching

Early stop criteria:
- Can name exact content to change
- Top hits converge (~70%) on one area/path

Escalate once:
- If signals conflict or scope fuzzy, run one refined parallel batch, then proceed

Depth:
- Trace only symbols you'll modify or whose contracts you rely on

Loop:
- Batch search → minimal plan → complete task
- Search again only if validation fails
- Prefer acting over more searching
</context_gathering>
```

**Fixed tool call budgets** (maximally prescriptive):
```xml
<context_gathering>
- Search depth: very low
- Bias strongly towards correct answer as quickly as possible, even if might not be fully correct
- Usually, absolute maximum of 2 tool calls
- If need more time to investigate, update user with latest findings and open questions
</context_gathering>
```

**Escape hatches**: When limiting, provide flexibility:
```
"...even if it might not be fully correct"
```

### More Eager (Autonomous, Comprehensive)

**Increase `reasoning_effort`** and use persistence prompt:

```xml
<persistence>
- You are agent - keep going until user's query completely resolved before ending turn
- Only terminate when sure problem is solved
- Never stop when encountering uncertainty — research or deduce most reasonable approach and continue
- Do not ask human to confirm assumptions — decide most reasonable, proceed, document for user's reference after finishing
</persistence>
```

**Define stop conditions**:
- State clearly when agent should terminate
- Outline safe vs unsafe actions
- Define when acceptable to hand back to user

**Example**:
```
Shopping tools:
- Checkout/payment: Low uncertainty threshold (confirm with user)
- Search: High threshold (proceed autonomously)

Coding tools:
- Delete file: Low threshold (confirm)
- Grep search: High threshold (proceed)
```

---

## Tool Preambles

GPT-5 provides clear upfront plans and progress updates via "tool preamble" messages.

**Purpose**: For agentic trajectories monitored by users, intermittent updates improve UX.

**High-Quality Preamble Prompt**:
```xml
<tool_preambles>
- Begin by rephrasing user's goal in friendly, clear, concise manner before calling tools
- Immediately outline structured plan detailing each logical step
- As you execute file edits, narrate each step succinctly and sequentially, marking progress clearly
- Finish by summarizing completed work distinctly from upfront plan
</tool_preambles>
```

**Example Output**:
```
"I'm going to check live weather service for current conditions in San Francisco,
providing temperature in both Fahrenheit and Celsius."

[Tool call: get_weather(location="San Francisco, CA", unit="f")]
```

---

## Reasoning Effort Parameter

`reasoning_effort` controls how hard the model thinks and how willingly it calls tools.

### Values by Model

| Model | Values | Default |
|-------|--------|---------|
| GPT-5 | `minimal`, `low`, `medium`, `high` | `medium` |
| GPT-5.1+ | `none`, `low`, `medium`, `high` | `none` |
| GPT-5.2+ / GPT-5.4 | `none`, `low`, `medium`, `high`, `xhigh` | `none` |

> **Breaking Change**: Default changed from `medium` (GPT-5) to `none` (GPT-5.1+). Existing prompts relying on default medium reasoning may produce degraded results without explicit `reasoning_effort` parameter.

### When to Adjust
- **`none`/`low`**: Simple lookups, routing, classification
- **`medium`**: Standard tasks, clear instructions
- **`high`**: Complex multi-step reasoning, analysis
- **`xhigh`** (GPT-5.2+): Critical tasks requiring maximum depth — research, complex debugging, architectural decisions

### Peak Performance
Break separable tasks across multiple turns (one turn per task) rather than increasing reasoning effort for compound tasks.

---

## Developer Role

GPT-5.1+ supersedes the `system` role with `developer` in the Responses API.

**Cleanest approach**: Use the `instructions` parameter directly:
```json
{
  "model": "gpt-5.2",
  "instructions": "You are a helpful coding assistant...",
  "input": "Fix the bug in auth.py"
}
```

**Message-based approach** (when needed):
```json
{
  "input": [
    {"role": "developer", "content": "System-level instructions here"},
    {"role": "user", "content": "User message"}
  ]
}
```

> `system` role still works for backward compatibility but `developer` is preferred for new code.

---

## Responses API

**Strong recommendation**: Use Responses API for GPT-5.x agentic flows.

**Benefits**:
- Improved agentic flows
- Lower costs
- More efficient token usage
- Reasoning context persisted between tool calls
- Encrypted reasoning items — model can reference its own reasoning without exposing it to the caller

**Performance Gains**:
Example: Tau-Bench Retail score 73.9% → 78.2% by:
1. Switching to Responses API
2. Including `previous_response_id` to pass back previous reasoning

**Why**: Model refers to previous reasoning traces, conserves CoT tokens, eliminates need to reconstruct plan after each tool call.

**Context Compaction**: Use the `/responses/compact` endpoint to shrink context mid-session without losing the conversation thread. Useful for long-running agent sessions approaching context limits.

**For long sessions**: Prefer the Conversations API (below) over chaining `previous_response_id` — conversations have no TTL and provide durable state management.

---

## Conversations API

Durable conversation threads with no TTL — preferred over `previous_response_id` for long-running sessions.

**When to use**:
- Multi-turn agent sessions requiring persistent state
- Sessions spanning hours/days (no expiration)
- When context compaction is needed mid-session

**Key features**:
- `/responses/compact` endpoint for context shrinking without losing thread
- No TTL on conversations (vs `previous_response_id` which expires)
- Automatic state management

**Example**:
```json
{
  "model": "gpt-5.2",
  "conversation_id": "conv_abc123",
  "input": "Continue working on the auth module"
}
```

---

## Strict Mode on Tool Definitions

Always set `strict: true` on all function/tool definitions:

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "strict": true,
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"}
      },
      "required": ["location"],
      "additionalProperties": false
    }
  }
}
```

**Why**: Enables constrained decoding — model output guaranteed to match schema. Eliminates JSON parsing errors and schema violations.

---

## Scope Discipline (GPT-5.2+)

GPT-5.2 can over-generate — producing more output than requested. Use scope constraints:

```xml
<design_and_scope_constraints>
- Implement ONLY what is explicitly requested
- Do not add features, refactor surrounding code, or "improve" beyond scope
- When ambiguous, implement the minimal interpretation
- If scope is unclear, ask for clarification rather than guessing
</design_and_scope_constraints>
```

**When needed**: Code generation, document drafting, any task where output length/scope matters.

---

## Verbosity Control

GPT-5 `verbosity` API parameter influences final answer length (not thinking length).

### API Parameter
```json
{"verbosity": "low"}  // or "medium" (default), "high"
```

### Natural Language Override
While API parameter sets global default, GPT-5+ responds to natural-language overrides for specific contexts:

**Example** (from Cursor):
```
Set verbosity=low globally

For code tools only:
"Write code for clarity first. Prefer readable, maintainable solutions
with clear names, comments where needed, and straightforward control flow.
Use high verbosity for writing code and code tools."
```

**Result**: Concise status updates + readable code diffs

### Output Verbosity Spec (GPT-5.2+)

For precise control over output length:

```xml
<output_verbosity_spec>
- Status updates: 1 sentence max
- Explanations: 2-3 bullet points max
- Code comments: Inline only, no block comments unless complex logic
- Summaries: 3 sentences max
- Error reports: Problem + fix, no preamble
</output_verbosity_spec>
```

---

## Long-Context Re-Grounding

For inputs exceeding ~10K tokens, add explicit re-grounding to prevent drift:

```xml
<long_context_handling>
- After reading large context blocks, summarize key points before acting
- Reference specific sections/line numbers when making changes
- Re-state the original task goal before generating output
- If context contains contradictions, flag them rather than silently choosing
</long_context_handling>
```

**When needed**: Large codebases, long documents, multi-file analysis.

---

## Hallucination and Ambiguity Handling

### Uncertainty Protocol
```xml
<uncertainty_and_ambiguity>
- When uncertain about facts, say so explicitly — never fabricate
- When multiple interpretations exist, state the most likely and proceed
- When referencing external APIs/docs, verify against provided context
- Distinguish between "I know" and "I infer" in reasoning
</uncertainty_and_ambiguity>
```

### High-Risk Self-Check
For critical outputs (production code, financial data, medical info):

```xml
<high_risk_self_check>
Before finalizing output:
1. Re-read the original request
2. Verify all claims against provided context
3. Flag any assumptions made
4. Confirm output matches requested format
</high_risk_self_check>
```

---

## Coding Best Practices

GPT-5 leads all frontier models in coding: bug fixes, large diffs, multi-file refactors, new features, full apps.

### Frontend Stack (Recommended)
- **Frameworks**: Next.js (TypeScript), React, HTML
- **Styling/UI**: Tailwind CSS, shadcn/ui, Radix Themes
- **Icons**: Material Symbols, Heroicons, Lucide
- **Animation**: Motion
- **Fonts**: San Serif, Inter, Geist, Mona Sans, IBM Plex Sans, Manrope

### Zero-to-One App Generation

Use self-reflection for quality:

```xml
<self_reflection>
- First, spend time thinking of rubric until confident
- Think deeply about every aspect of world-class one-shot web app
- Create rubric with 5-7 categories (critical, but don't show user - for your purposes only)
- Use rubric to internally think and iterate on best possible solution
- Remember: if not hitting top marks across all categories, start again
</self_reflection>
```

### Matching Codebase Design Standards

```xml
<code_editing_rules>
<guiding_principles>
- Clarity and Reuse: Every component modular and reusable. Avoid duplication.
- Consistency: Adhere to design system—color tokens, typography, spacing unified
- Simplicity: Small, focused components. Avoid unnecessary complexity
- Demo-Oriented: Structure allows quick prototyping
- Visual Quality: High visual quality bar (spacing, padding, hover states)
</guiding_principles>

<frontend_stack_defaults>
- Framework: Next.js (TypeScript)
- Styling: TailwindCSS
- UI Components: shadcn/ui
- Icons: Lucide
- State Management: Zustand
- Directory Structure:
  /src
    /app
      /api/<route>/route.ts
      /(pages)
    /components/
    /hooks/
    /lib/
    /stores/
    /types/
    /styles/
</frontend_stack_defaults>

<ui_ux_best_practices>
- Visual Hierarchy: Limit typography to 4–5 font sizes and weights
- Color Usage: Use 1 neutral base (e.g., zinc) and up to 2 accent colors
- Spacing and Layout: Always use multiples of 4 for padding and margins
- State Handling: Use skeleton placeholders or animate-pulse for loading
- Accessibility: Use semantic HTML and ARIA roles
</ui_ux_best_practices>
</code_editing_rules>
```

---

## Instruction Following

GPT-5 follows instructions with **surgical precision** - enables flexibility but requires careful prompt construction.

### Contradictory Instructions Are Damaging

Poorly-constructed prompts with contradictory/vague instructions harm GPT-5 more than other models.

**Why**: Model expends reasoning tokens searching for way to reconcile contradictions.

**Bad Example**:
```
❌ "Never schedule appointment without explicit patient consent recorded in chart"
❌ "For high-acuity cases, auto-assign earliest same-day slot without contacting patient"

These directly conflict!
```

**Fix**: Review prompts for internal consistency. Remove contradictions.

### Prompt Tuning Example (Cursor)

**Original** (too general for GPT-5):
```xml
<maximize_context_understanding>
Be THOROUGH when gathering information. Make sure you have FULL picture
before replying. Use additional tool calls or clarifying questions as needed.
</maximize_context_understanding>
```

**Problem**: Caused excessive tool usage on small tasks.

**Refined**:
```xml
<context_understanding>
If you've performed edit that may partially fulfill USER's query,
but you're not confident, gather more information or use more tools before ending turn.
Bias towards not asking user for help if you can find answer yourself.
</context_understanding>
```

**Result**: Better decisions about when to use tools vs internal knowledge.

---

## Steering Best Practices

GPT-5 is extraordinarily steerable - responds well to:
- Verbosity control (API param + natural language)
- Tone adjustments
- Tool calling behavior
- User-defined custom rules/instructions

### Structured Specs
Using structured XML specs like `<[instruction]_spec>` improves instruction adherence:

```xml
<tool_use_spec>...</tool_use_spec>
<context_understanding>...</context_understanding>
<output_format_spec>...</output_format_spec>
```

Allows clear referencing of previous categories elsewhere in prompt.

---

## Model Parameters Summary

| Parameter | Purpose | Values |
|-----------|---------|--------|
| `reasoning_effort` | How hard model thinks | `none` (default 5.1+), `low`, `medium`, `high`, `xhigh` (5.2+) |
| `verbosity` | Final answer length | `low`, `medium` (default), `high` |
| `previous_response_id` | Reuse reasoning context | Response ID from previous call |
| `conversation_id` | Durable conversation thread | Conversation ID for persistent sessions |
| `strict` | Constrained decoding on tools | `true` (recommended) / `false` |

---

## Migration Guide

When upgrading between GPT-5.x models, follow this 5-step process:

1. **Switch model ID**: Update `model` parameter (e.g., `gpt-5` → `gpt-5.2`)
2. **Pin reasoning effort**: Explicitly set `reasoning_effort` — don't rely on defaults (changed from `medium` to `none` in 5.1+)
3. **Run evals**: Compare output quality on your test suite before and after
4. **Use Prompt Optimizer**: OpenAI's built-in tool to adapt prompts for new model behavior
5. **Iterate**: Adjust prompts based on eval results; most prompts need only minor tuning

> **Common migration issue**: GPT-5 prompts that relied on default `medium` reasoning will appear "lazy" on GPT-5.1+ due to `none` default. Always pin `reasoning_effort` explicitly.

---

## Common Pitfalls

| Issue | Problem | Fix |
|-------|---------|-----|
| **Contradictory Instructions** | Internal conflicts in prompt | Review for consistency; remove contradictions |
| **Over-Restricting Autonomy** | Too many limitations on capable model | Start permissive, add constraints only when needed |
| **Ignoring Responses API** | Missing 5-10% performance gains | Use Responses API with `previous_response_id` |
| **Global Verbosity Everywhere** | Same verbosity for code, summaries, etc. | Set global default, override with natural language for specific contexts |
| **Scope Over-Generation** | GPT-5.2 produces more than requested | Use `<design_and_scope_constraints>` block |
| **Reasoning Effort Default Mismatch** | Prompts assume `medium` default, get `none` on 5.1+ | Always explicitly set `reasoning_effort` |

---

## Key Insights

> "GPT-5 responds well to direct and explicit instruction. Structured, scoped prompts yield most reliable results."

> "The model's creativity in approaching problems may exceed a human's ability to prescribe optimal thinking process."

> "Poorly-constructed prompts containing contradictory or vague instructions can be more damaging to GPT-5 than to other models."

---

## Further Reading

### Official Documentation
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [GPT-5.1 Prompting Guide](https://cookbook.openai.com/examples/gpt-5-1/gpt-5-1_prompting_guide)
- [GPT-5.2 Prompting Guide](https://cookbook.openai.com/examples/gpt-5-2/gpt-5-2_prompting_guide)
- [GPT-5.3-Codex Guide](https://cookbook.openai.com/examples/gpt-5-3-codex/prompting_guide)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Responses API Documentation](https://platform.openai.com/docs/api-reference/responses)
- [Conversations API Documentation](https://platform.openai.com/docs/api-reference/conversations)

### Production Examples
- [Cursor's GPT-5 Integration](https://cursor.com/blog/gpt-5) - Real-world prompt tuning

### General Patterns
- [Model-Agnostic Guidelines](PROMPT-ENGINEERING-GUIDELINES.md)
