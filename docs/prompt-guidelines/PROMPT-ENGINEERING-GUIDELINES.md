# Prompt Engineering Guidelines for Autonomous AI Agents

Model-agnostic patterns for building reliable autonomous agents and slash commands.

**Model-Specific**: [Claude](PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md) | [GPT](PROMPT-ENGINEERING-GUIDELINES-GPT.md)

**Last Updated**: 2026-03-03

---

## Quick Start

**New to prompt engineering?** Start here:

1. **Use templates**: XML for Claude, Markdown for cross-model
2. **Structure work**: Break into phases with clear gates
3. **Add examples**: 2-3 canonical cases showing expected patterns
4. **Validate independently**: Different agent verifies implementation
5. **Manage context**: Load just-in-time, delegate to sub-agents

**For detailed patterns**, continue reading.

---

## Purpose & Success Criteria

**Target**: Developers building AI agent systems with autonomous task execution

**Achieves**:
- Faster agent development through reusable patterns
- Higher task completion rates via structured workflows
- Fewer prompt iterations using proven templates
- Better code quality through independent validation

**Measure success**:
- Task completion rate (target: >85%)
- Prompt iterations to working solution (target: <3)
- Validation effectiveness (target: >90% issues caught)

**When to use**: Read General guidelines first, add model-specific (Claude/GPT) for optimization.

---

## Core Principles

### 1. Intent > Context > Prompts
What you're ultimately engineering is **intent** — goals, constraints, and success criteria that tell the AI *what must be true*, not *what code to write*. Context provides the information environment. Prompts are just the mechanism.
- Encode outcomes and goals, not implementation steps
- Progressive disclosure (just-in-time loading)
- Tool-mediated exploration
- Working set maintenance only
- Delegate deep work to sub-agents

### 2. Right Altitude
Balance specificity and flexibility:
- **Too Low**: "If X then Y, if Z then W..." (brittle, doesn't generalize)
- **Too High**: "Be helpful" (vague, inconsistent results)
- **Right**: "Analyze systematically, implement pragmatically, validate thoroughly" (guiding heuristics)

**Decision heuristics**:
- Simple, well-defined task → Direct specific instructions
- Complex, multi-step task → High-level phases with sub-steps
- Open-ended exploration → Guiding principles + examples

### 3. Be Explicit and Direct
Modern frontier LLMs (Claude 4.6+, GPT-5.2+) need clear instructions:
- State exactly what you want, not hints
- Explain WHY behavior matters (models generalize from context)
- Use examples (models pay close attention to details)
- Specify completeness: "as many features as needed" vs "minimal implementation"

### 4. Independent Verification
Implementation ≠ Validation:
- Use separate agents for verification
- Multi-layer: functional, quality, security, architecture
- Run validators in parallel when possible

### 5. Simplest Thing That Works
```
Well-crafted prompt + retrieval
  ↓ If insufficient
Structured workflow (phases + gates)
  ↓ If insufficient
Agentic autonomy (ReAct loop)
  ↓ If insufficient
May not be LLM-suitable yet
```

---

## Instruction Structure

### Templates

**XML** (preferred for Claude):
```xml
<system_context>
Role, identity, operational context
</system_context>

<instructions>
## Phase 1: Analysis
- Understand requirements
- Analyze patterns

## Phase 2: Execution
- Implementation guidelines
- Delegation strategy

## Phase 3: Validation
- Success criteria
- Verification methods
</instructions>

<tools>
When to use each tool
</tools>

<examples>
2-3 canonical demonstrations
</examples>

<constraints>
Hard boundaries, anti-patterns
</constraints>
```

**Markdown** (cross-model):
```markdown
# System Context
Role, identity, operational context

## Instructions
### Phase 1: Analysis
- Understand requirements

### Phase 2: Execution
- Implementation guidelines

### Phase 3: Validation
- Success criteria

## Tools
When to use each tool

## Examples
2-3 canonical cases

## Constraints
Hard boundaries, anti-patterns
```

### Format Selection
- **XML**: Claude (40% better performance), hierarchical data
- **Markdown**: Cross-model, team prefers readability
- **Avoid JSON**: Underperforms for prompts
- **Stay consistent**: One format per conversation

### Adding Context & Motivation
Explain WHY, not just WHAT:

❌ Less effective: `NEVER use ellipses`

✅ More effective: `Your response will be read by text-to-speech. Never use ellipses since TTS engines can't pronounce them properly.`

Models generalize better from explanations.

---

## Custom Slash Command Structure
When generating custom slash commands (custom prompts) for use by AI coding agents, follow this structure:

### Template

```markdown
---
description: Action-oriented summary (<100 chars)
argument-hint: [arg1] [arg2]
---

# Command Name

## Variables
INPUT: $ARGUMENTS

## Instructions (optional)
- Command-specific context only (reference project guidelines)

## Workflow

### Phase 1: [Name]
1. Steps with clear actions
2. Delegate to specialist agents

**Gate**: Proceed condition

### Phase 2: Validation
- Quality checks (parallel when possible)

**Gate**: All pass
```

### Section Guidelines

**Frontmatter** (required): Model, tools, description for help
**Variables** (required): Even if just `INPUT: $ARGUMENTS`
**Instructions** (optional): Add only if command needs domain-specific context
**Workflow** (required): Phases with gates for complex tasks, numbered steps
**Report** (optional): Only for specific output formats (reports, summaries)

### Anti-Patterns
| ❌ Avoid | ✅ Do |
|---------|-------|
| Duplicate project rules | Reference, add command-specific only |
| Missing Variables | Always include |
| Prose-heavy workflow | Numbered steps, concise |
| Report for file edits | Only for specific outputs |

---

## Task Decomposition

### ReAct Pattern (Recommended)
```
Loop until complete:
  THOUGHT: Analyze situation, plan next action
  ACTION: Execute tool call or implementation
  OBSERVATION: Evaluate results, update understanding
```

### Planning: Hybrid Approach

**Initial Decomposition**:
1. Break into high-level phases
2. Identify dependencies
3. Mark parallel vs sequential
4. Use task tracking

**Just-In-Time Planning**:
- Plan details when reaching each phase
- Adapt based on outcomes
- Re-plan when blocked

### Chain of Thought (CoT)
For complex reasoning:
1. Understand problem
2. Identify relevant information
3. Break into sub-problems
4. Solve systematically
5. Combine solutions

### Reasoning Models vs Standard
Reasoning models (o-series, Claude with extended thinking) have built-in chain-of-thought — **do not** add explicit "think step by step" prompting, as it wastes tokens and can degrade output.

- **Reasoning models**: Direct task instructions only. Model handles its own thinking process.
- **Standard models**: Still benefit from explicit CoT prompting ("think step by step", "break this down").

When unsure, test both approaches with your specific model and task.

---

## Context Management

Unified strategy with complementary techniques:

### Progressive Disclosure
Load information just-in-time:
1. Start with structure/outline
2. Navigate to relevant areas
3. Load specifics as needed
4. Maintain active working set only

### State Management
**When to use each**:
- **Structured (JSON/YAML)**: Test status, counts, schema data
- **Unstructured (text)**: Session summary, next steps, warnings
- **Git commits**: Checkpoints for restoration

**Example structured state**:
```json
{
  "tests": {"total": 200, "passing": 175, "failing": 25},
  "current_phase": "validation",
  "blockers": []
}
```

**Example progress notes**:
```
Session 3: Fixed auth validation
Next: investigate user_mgmt failures (test #2)
Warning: Never remove tests - causes missing functionality
```

### Compaction (Approaching Limit)
1. Summarize old context preserving critical info
2. Keep recent N messages full
3. Clear old tool results
4. Reinitiate with summary + recent

### Prompt Caching
Both major providers support automatic prompt caching with ~90% cost savings on cached tokens.

**Pattern**: Place static content first, dynamic content last:
1. System prompt (cached)
2. Tool definitions (cached)
3. Reference documents (cached)
4. Dynamic conversation history (not cached)

This ordering maximizes cache hit rates. No code changes needed — caching is automatic when content prefix matches between requests.

### Sub-Agent Architecture
**Main Agent** (orchestrator): High-level planning, coordination, lightweight state

**Sub-Agents** (specialists): Deep technical work, focused exploration, return condensed summaries

**Benefits**: Clean contexts, deep exploration without bloat, parallel execution, specialized expertise

**When to delegate**: Documentation lookup, code review, architecture analysis, deep codebase exploration, visual validation

---

## Tool Design

### Good Tool Characteristics
1. **Self-contained**: Minimal dependencies, robust to errors
2. **Clear purpose**: Obvious when to use, no ambiguity
3. **Minimal overlap**: No redundant functionality
4. **Token-efficient**: Return only relevant info, not full dumps
5. **Excellent docs**: Clear purpose, parameters, returns, examples

### Template
```markdown
Tool: [name]

Purpose: [1-2 sentences]
Use when: [specific scenario]
Don't use for: [anti-pattern]

Parameters:
- param1 (required): [description]
- param2 (optional, default X): [description]

Returns:
Success: [what it returns]
Error: [clear message, not exception]

Examples:
[2-3 canonical use cases]
```

### Error Handling
**DON'T**: Raise exceptions in tool code
**DO**: Return error message via tool result

Models understand and retry correctly when given clear error messages.

### Structured Outputs
Both major providers now support constrained decoding for guaranteed schema compliance:
- **`strict: true`** on tool/function definitions — model output guaranteed to match schema
- **`json_schema`** output format — force entire response into a JSON schema

This eliminates JSON parsing errors and schema violations in production. See model-specific docs for implementation details:
- [Claude: Structured Outputs](PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md#structured-outputs-ga)
- [GPT: Strict Mode](PROMPT-ENGINEERING-GUIDELINES-GPT.md#strict-mode-on-tool-definitions)

---

## Validation Strategy

### Multi-Layer Validation
1. **Functional**: Works? Tests pass?
2. **Quality**: Clean code? Linting passes?
3. **Architecture**: Fits patterns? No debt?
4. **Security**: No vulnerabilities? Safe inputs?
5. **UI/UX**: Matches design? Accessible? [if applicable]
6. **Documentation**: Updated? Complete?

### When to Use
```
Code change → Tests + Linting + Review
Architecture change → Architect review
UI change → Visual validation + Designer review
Security-sensitive → Security audit
All of above → All validators in parallel
```

### Self-Verification Pattern
Ask models to verify before completion:
```markdown
Before finishing:
1. Verify solution with test cases
2. Check expected results achieved
3. Run through edge cases
4. Fix issues found
```

Example: "Write factorial function. Before finishing, verify with n=0, n=1, n=5, n=10 and fix issues."

### Independent Verification Pattern
```markdown
Implementation

Validation (parallel):
- Code quality
- Architecture
- Security
```

### Success Criteria Template
```markdown
## Success Criteria (ALL must pass)

Functional:
- [ ] Requirement X implemented
- [ ] Edge case Y handled
- [ ] Integration Z working

Quality:
- [ ] Tests pass
- [ ] Code analysis clean (0 errors/warnings)
- [ ] Performance meets requirements

Documentation:
- [ ] Code documented
- [ ] Docs updated
- [ ] Changes logged

Cleanup:
- [ ] Temp files removed
- [ ] Debug code removed
- [ ] TODOs addressed
```

---

## Error Handling

### Recovery Framework
```
DETECT → Monitor failures early
CLASSIFY → Temporary vs permanent, recoverable vs not
RESPOND →
  Temporary → Retry with backoff
  Permanent → Fix root cause
  Unrecoverable → Escalate to user
VALIDATE → Verify recovery worked
```

### Common Edge Cases

**Context Management**:
- Progressive disclosure fails to find context → Escalate to user for guidance
- State restoration fails → Fall back to fresh exploration
- Sub-agent exceeds capacity → Return partial results, continue in new session

**Tool Execution**:
- Tool call loops → Detect after 3 identical calls, try different approach
- Timeout/unavailability → Retry with exponential backoff (3 attempts), escalate
- Parallel conflicts → Serialize conflicting operations

**Validation**:
- All validators fail → Root cause analysis, fix, re-validate
- Validators disagree → Manual review required, escalate to user
- False positives → Refine validation criteria, re-run

---

## Anti-Patterns

### Prompt Design
| ❌ Avoid | ✅ Do |
|---------|-------|
| Bloated edge case listing | Curated canonical examples |
| If-then chains (too specific) | Guiding heuristics (right altitude) |
| Vague assumptions | Explicit expectations |
| Inconsistent formatting | Single format throughout |
| No examples | 2-3 concrete demonstrations |

### Context Management
| ❌ Avoid | ✅ Do |
|---------|-------|
| Load everything upfront | Just-in-time loading |
| Static retrieval only | Progressive disclosure |
| No compaction strategy | Summarize when needed |
| Context pollution | Working set only |

### Tool Design
| ❌ Avoid | ✅ Do |
|---------|-------|
| One tool does everything | Focused single-purpose |
| Overlapping functionality | Clear boundaries |
| Vague documentation | Excellent docs + examples |
| Raise exceptions | Return errors via interface |

### Validation
| ❌ Avoid | ✅ Do |
|---------|-------|
| Single check only | Multi-layer verification |
| Same agent validates | Independent validators |
| Ambiguous pass/fail | Explicit criteria |
| Skip when "looks good" | Always validate |

---

## Testing Your Prompts

### Eval Dataset (Minimum 30 Cases)
- **Success cases (40%)**: Should work perfectly
- **Edge cases (40%)**: Tricky scenarios
- **Failure cases (20%)**: Should handle gracefully

### Iteration Process
1. Test with diverse scenarios
2. Collect failure examples
3. Analyze root causes
4. Update prompt to address
5. Re-test affected scenarios
6. Check for regressions
7. Repeat until robust

### Quality Metrics
- Task completion rate (target: >85%)
- Parameter accuracy (% correct tool calls)
- Error recovery (% recovered from failures)
- Validation effectiveness (% issues caught)

---

## Quick Reference

**Decision Trees**:

```
What to use?
  Simple task → Single prompt + retrieval
  Predefined sequence → Workflow (phases + gates)
  Open-ended, multi-step → Agent (ReAct loop)
  Complex feature → Process (Requirements → Design → Implementation)

Which validation?
  (See "Validation Strategy > When to Use" above)

Error recovery?
  Tool error → Analyze, correct inputs, retry
  Validation failure → Fix issues, re-validate
  Stuck/blocked → Request user input
  Unrecoverable → Document, explain, escalate
```

**Essential Patterns**:
1. Intent > Context > Prompts: Encode goals, not implementation steps
2. Be Explicit: Clear instructions + WHY
3. Right Altitude: Guide without constraining
4. Validate Independently: Different agents verify
5. Disclose Progressively: Just-in-time retrieval
6. Design Tools Clearly: Token-efficient returns
7. Iterate Empirically: Test extensively

---

## Further Reading

### Model-Specific Guidelines
- [Claude-Specific](PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md) - Claude 4.6+ behaviors, XML preference, extended thinking
- [GPT-Specific](PROMPT-ENGINEERING-GUIDELINES-GPT.md) - GPT-5.2+ behaviors, agentic eagerness, reasoning effort

### Official Documentation

**Anthropic**:
- [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Building Effective Agents](https://docs.anthropic.com/en/docs/agents-and-tools/building-effective-agents)
- [Claude 4.6 Migration Guide](https://docs.anthropic.com/en/docs/resources/claude-4-6-migration)

**OpenAI**:
- [GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [GPT-5.1 Prompting Guide](https://cookbook.openai.com/examples/gpt-5-1/gpt-5-1_prompting_guide)
- [GPT-5.2 Prompting Guide](https://cookbook.openai.com/examples/gpt-5-2/gpt-5-2_prompting_guide)

### Research Papers
- "ReAct: Synergizing Reasoning and Acting in Language Models" (2023)
- "Graph of Thoughts: Solving Elaborate Problems with Large Language Models" (2024)
- OWASP: "LLM Prompt Injection Prevention" (2025)
