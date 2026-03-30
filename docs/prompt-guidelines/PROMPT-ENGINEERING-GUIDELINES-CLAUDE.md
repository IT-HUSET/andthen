# Claude-Specific Prompt Engineering Guidelines

Claude 4.5/4.6+ specific behaviors, optimizations, and patterns.

**See Also**: [General Guidelines](PROMPT-ENGINEERING-GUIDELINES.md) - Model-agnostic core patterns

**Last Updated**: 2026-03-03

---

## Format Preference

### XML vs Markdown
Claude is specifically tuned for XML tags - prefer XML over Markdown:

```xml
<system_context>Role and identity</system_context>
<instructions>What to do</instructions>
<examples>Canonical demonstrations</examples>
```

**Why**: Research shows up to 40% performance improvement. Claude's training emphasized XML structure.

**Override when**: Cross-model compatibility required, team strongly prefers Markdown.

---

## Claude 4.5/4.6 Behaviors

### Action vs Suggestion
Claude 4.5/4.6 follows instructions with **surgical precision** - be directive:

**For action** (Claude implements):
```
Change this function to improve performance
Implement the user registration feature
```

**For suggestions only**:
```
Can you suggest improvements?
What changes would you recommend?
```

### Default to Action Pattern
Add to system prompt for proactive behavior:

```xml
<default_to_action>
By default, implement changes rather than suggesting.
When intent unclear, infer most useful action and proceed.
Use tools to discover missing details instead of asking.
Try to infer whether a tool call (file edit, read) is intended and act accordingly.
</default_to_action>
```

### Conservative Action Pattern
For less proactive behavior:

```xml
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed.
When intent is ambiguous, default to information, research, and recommendations.
Only proceed with edits when explicitly requested.
</do_not_act_before_instructions>
```

---

## Breaking Changes in Claude 4.6

### Prefill Removal
Claude 4.6 no longer supports assistant message prefill — requests with prefilled assistant content return HTTP 400.

**Migration paths**:
- **Structured output**: Use `output_config.format` with `json_schema` type
- **Style/format control**: Use system instructions to guide output format
- **Tool forcing**: Use `tool_choice` parameter

### Parameter Restrictions
- `temperature` + `top_p` together now returns an error on Claude 4+ (pick one)
- Tool parameter JSON escaping behavior differs — test tool schemas after upgrading

### New Stop Reasons
Claude 4.5+ introduces two new stop reasons:
- `refusal` — model declined the request
- `model_context_window_exceeded` — input exceeded context limit

---

## Context Awareness

**See [General Guidelines > Context Management](PROMPT-ENGINEERING-GUIDELINES.md#context-management) for full strategy.**

### Claude-Specific Behavior
Claude 4.5/4.6 tracks remaining context window ("token budget") throughout conversations.

**Natural wrapping**: Without guidance, Claude may wrap up work as it approaches context limit.

**Override for long tasks**:
```markdown
Your context will be compacted as needed, allowing indefinite work.
Never stop tasks early due to token concerns.
Save progress to memory before context refresh.
Complete tasks fully regardless of remaining context.
```

---

## State Management for Long Tasks

**See [General Guidelines > Context Management > State Management](PROMPT-ENGINEERING-GUIDELINES.md#state-management) for general approach.**

### Claude-Specific Strengths
Claude 4.5/4.6 excels at long-horizon reasoning with exceptional state tracking.

### Multi-Context Window Tasks

**First Window: Framework Setup**
```markdown
Use first context to establish foundation:
- Write tests in structured format (tests.json)
- Create setup scripts (init.sh for servers, tests, linters)
- Initialize state tracking files
```

**Future Windows: Iterate on Todo List**
```markdown
Subsequent windows focus on execution:
- Review progress from state files
- Continue from todo list
- Maintain test discipline
```

**Quality of Life Tools**
```bash
# init.sh example
#!/bin/bash
npm install && npm run lint && npm test
```

**Why**: Prevents repeated setup when continuing from fresh context.

**Test Discipline**
```markdown
Create tests before starting work, track in structured format.
Remind: "Unacceptable to remove/edit tests - could lead to missing functionality."
```

**Starting Fresh vs Compaction**
Claude 4.5/4.6 discovers state from filesystem excellently:
```markdown
When starting fresh context:
- Call pwd; only read/write files in this directory
- Review progress.txt, tests.json, git logs
- Manually run fundamental integration test before new features
```

**Encourage Full Context Usage**
```markdown
This is a very long task, so plan your work clearly.
Spend your entire output context working on the task.
Don't run out of context with significant uncommitted work.
Continue working systematically until you complete this task.
```

---

## Communication Style

Claude 4.5/4.6 has more concise, natural communication style:

**Characteristics**:
- **More direct**: Fact-based progress reports, not self-celebratory
- **More conversational**: Fluent, colloquial, less machine-like
- **Less verbose**: May skip detailed summaries for efficiency

**Balance verbosity** if you want updates:
```markdown
After completing a task with tool use, provide a quick summary of work done.
```

### Overtriggering Warning (Opus 4.5/4.6)
Opus models can overtrigger on emphatic instructions. Dial back aggressive language:

❌ **Over-emphatic**: `CRITICAL: You MUST ALWAYS use the search tool before responding. NEVER skip this step.`

✅ **Balanced**: `Search for relevant context before responding. Skip only when the answer is clearly within your training data.`

Strong models follow instructions well without aggressive emphasis — excessive `MUST`/`NEVER`/`CRITICAL` can cause rigid, suboptimal behavior.

---

## Extended Thinking

### Adaptive Thinking (Claude 4.6 — Recommended)

Opus 4.6 deprecates `budget_tokens` in favor of adaptive thinking:

```json
{
  "thinking": {"type": "adaptive"},
  "output_config": {"effort": "high"}
}
```

The model dynamically allocates thinking tokens based on task complexity. Combined with the `effort` parameter, this replaces manual budget management.

### Manual Extended Thinking (Sonnet 4.6)

Sonnet 4.6 supports both adaptive and manual extended thinking:

```json
{
  "thinking": {"type": "enabled", "budget_tokens": 10000}
}
```

### Effort Levels

| Effort | Use Case | Thinking Behavior | Model Support |
|--------|----------|-------------------|---------------|
| `low` | Simple lookups, classification, subagents | Minimal or no thinking | Opus 4.6, Sonnet 4.6, Opus 4.5 |
| `medium` | Standard tasks, code edits, most agentic coding | Moderate thinking | Opus 4.6, Sonnet 4.6, Opus 4.5 |
| `high` | Complex reasoning, debugging, architecture | Deep analysis (API default) | Opus 4.6, Sonnet 4.6, Opus 4.5 |
| `max` | Critical decisions, hardest problems | No constraints on thinking | **Opus 4.6 only** (error on other models) |

> **Note**: Haiku 4.5 does **not** support the effort parameter. Effort is a behavioral signal, not a hard token cap — even at `low`, the model will still think on genuinely hard problems.

### Recommended Configurations

**Coding workloads** (most tasks):
```json
{"thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}}
```

**Chat/conversational**:
```json
{"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}}
```

**Autonomous agents / computer use**:
```json
{"thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}}
```
Use adaptive thinking for agents — the model allocates more thinking for complex steps and less for simple ones, optimizing cost across long trajectories.

### When to Use Adaptive Thinking
- Autonomous agents with variable task complexity
- Computer use sessions (bimodal: some steps trivial, some complex)
- Workloads where manual budget tuning is impractical
- When you want the model to "think as much as needed"

### Prompting Extended Thinking
**Start with general instructions**:
```markdown
Think thoroughly and in great detail about this problem.
Consider multiple approaches, show complete reasoning.
```

**Why**: Claude's creativity may exceed a human's ability to prescribe optimal thinking process. Add specifics only if thinking output shows gaps.

### Multishot Pattern
Include examples using `<thinking>` or `<scratchpad>` tags — Claude generalizes the pattern.

---

## Structured Outputs (GA)

### Output Config Format
Force model output to match a JSON schema:

```json
{
  "output_config": {
    "format": {
      "type": "json_schema",
      "json_schema": {
        "name": "response",
        "schema": {
          "type": "object",
          "properties": {
            "answer": {"type": "string"},
            "confidence": {"type": "number"}
          },
          "required": ["answer", "confidence"]
        }
      }
    }
  }
}
```

### Strict Tool Definitions
Set `strict: true` on tool `input_schema` for guaranteed schema compliance:

```json
{
  "name": "get_weather",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string"}
    },
    "required": ["location"]
  },
  "strict": true
}
```

> **Deprecation**: `output_format` parameter is deprecated — use `output_config.format` instead.

---

## Effort Parameter (GA)

Control how much effort the model puts into its response:

```json
{
  "output_config": {
    "effort": "high"
  }
}
```

| Level | Use Case |
|-------|----------|
| `low` | Simple lookups, routing, classification |
| `medium` | Standard tasks, conversational responses |
| `high` | Complex reasoning, code generation, analysis |
| `max` | Research, critical decisions, deep debugging |

No beta header required. Works with all Claude 4.5+ models.

---

## Citations API (GA)

Extract cited passages from source documents:

```json
{
  "messages": [{"role": "user", "content": [
    {"type": "document", "source": {"type": "text", "data": "..."}},
    {"type": "text", "text": "What does the document say about X?"}
  ]}],
  "citations": {"enabled": true}
}
```

Response includes `cited_text` blocks referencing source documents. Cited text does not count toward output token usage.

---

## 1M Context Window (Beta)

Enable with beta header:
```
anthropic-beta: context-1m-2025-08-07
```

- Available on Sonnet 4.6 and Opus 4.6
- Standard pricing up to 200K tokens
- Long-context pricing above 200K (check current rates)
- Best for large codebases, long documents, extensive context

---

## Advanced Tool Use (Beta)

Enable with beta header:
```
anthropic-beta: advanced-tool-use-2025-11-20
```

### Features
- **Tool Search**: Model can search through large tool collections efficiently
- **Programmatic Tool Calling**: Dynamic tool invocation based on runtime conditions
- **Tool Use Examples**: Provide example tool calls to guide model behavior

Best for agents with large tool inventories (>20 tools) or dynamic tool sets.

---

## Memory Tool

Claude has Memory tool (public beta) for persistent cross-session state:

```markdown
Throughout execution:
- Store knowledge outside context window using Memory tool
- Consult memory across sessions
- Build knowledge bases over time
```

**Benefits**: Cross-session persistence, historical learning, not just retrieval (RAG).

---

## Model Selection

| Model | ID | SWE-bench Verified | Context | Max Output | Input/Output (per 1M) |
|-------|-----|-------------------|---------|------------|----------------------|
| **Haiku 4.5** | `claude-haiku-4-5-20251001` | 73.3% | 200K | 64K | $1/$5 |
| **Sonnet 4.6** | `claude-sonnet-4-6` | 79.6% | 200K (1M beta) | 64K | $3/$15 |
| **Opus 4.6** | `claude-opus-4-6` | 80.8% | 200K (1M beta) | 128K | $5/$25 |

| Model | Best For |
|-------|----------|
| **Haiku 4.5** | Simple tasks, subagents, high-volume parallel work. No effort param support. |
| **Sonnet 4.6** | Most daily coding — within 1.2% of Opus at 60% cost. Sweet spot for implementation, review, testing. |
| **Opus 4.6** | Planning, specs, ADRs, trade-off analysis, security audits, complex debugging. Only model supporting `max` effort. |

See also: [Model & Effort Selection Guide](../../MODEL-EFFORT-SELECTION-GUIDE.md) for detailed task-specific recommendations.

---

## Performance Optimization

### Examples Are Critical
Claude 4.5+ pays **close attention** to example details:
- Curate diverse, canonical examples (not exhaustive edge cases)
- Examples show pattern, not every variation
- 2-3 well-chosen examples > 10 generic ones

### Context & Motivation
Explain WHY behaviors matter:

❌ Less effective: `NEVER use ellipses`

✅ More effective: `Your response will be read by text-to-speech. Never use ellipses since TTS engines can't pronounce them properly.`

Claude generalizes from explanations.

### Incremental Progress
Claude 4.5/4.6 focuses on "making steady advances on a few things at a time rather than attempting everything at once."

**Prompt for this**:
```markdown
Focus on incremental progress:
- Complete a few components thoroughly before moving on
- Don't attempt everything simultaneously
- Make steady, measurable advances
```

---

## Common Pitfalls

| Issue | Problem | Fix |
|-------|---------|-----|
| **Assumed Proactivity** | Expecting action from "suggest changes" | Be explicit: "Change this" vs "Can you suggest?" |
| **Not Leveraging Context Awareness** | Stopping tasks early, poor context transitions | Tell Claude about compaction, use Memory tool |
| **Missing State Management** | Losing progress across contexts | JSON for structure, text for notes, git for checkpoints |
| **Over-Prescriptive Thinking** | Restricting reasoning with rigid steps | Start high-level goals, add specifics only if needed |

---

## Key Insights

> "Claude 4.5/4.6 models excel at long-horizon reasoning with exceptional state tracking, making steady advances on a few things at a time."

> "Context engineering is the art and science of curating what will go into the limited context window."

> "Claude is smart enough to generalize from explanations."

---

## Further Reading

### Official Documentation
- [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Extended Thinking Tips](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips)
- [Structured Outputs](https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs)
- [Adaptive Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#adaptive)
- [Citations](https://docs.anthropic.com/en/docs/build-with-claude/citations)
- [Claude 4.6 Migration Guide](https://docs.anthropic.com/en/docs/resources/claude-4-6-migration)
- [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Building Effective Agents](https://docs.anthropic.com/en/docs/agents-and-tools/building-effective-agents)

### General Patterns
- [Model-Agnostic Guidelines](PROMPT-ENGINEERING-GUIDELINES.md)
