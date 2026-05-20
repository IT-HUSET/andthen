# Skill-Authoring Guidelines

Generic guidelines for authoring Claude Code / Claude Agent skills (SKILL.md bundles). Supplements – does not restate – the general prompt-engineering rules in `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES.md`. Read those first; this doc covers what's specific to *skills* as a packaging and discovery format.

**Audience**: anyone authoring or reviewing a `SKILL.md` bundle, including AI agents editing skill content.

---

## What a Skill Is

A skill is an **organized folder** – a `SKILL.md` plus optional reference files and scripts – that an agent discovers by name and description, loads on demand, and uses to perform a specific task well. The mental model: *an onboarding guide for a new hire*. The skill captures procedural knowledge so the model behaves competently without holding that knowledge in the base context.

What discriminates a good skill from a bad one:

- **Concise**. Once loaded, every token competes with conversation history and other context.
- **Right degree of freedom**. Instruction specificity matches task fragility.
- **Progressively disclosed**. Information loads in stages; only the right level for the current task occupies context.
- **Reliably triggered**. The description discriminates clearly between "fire" and "don't fire".
- **Evaluation-driven**. Written to pass tested failure modes, not imagined ones.

---

## Progressive Disclosure: the Bundle Architecture

A skill loads in three levels. Treat this as a **file-layout discipline**, not just a prompting technique.

| Level | What loads | When | Budget |
|-------|------------|------|--------|
| 1. Metadata | `name` + `description` (frontmatter only) | Always, at session start | ~100 tokens per skill |
| 2. Body | `SKILL.md` body | When the skill is triggered | Target <500 lines / ~5k tokens |
| 3. Resources | Reference files, scripts | On demand, via explicit read / execute | Effectively unbounded |

`SKILL.md` serves as a *table of contents* that points to deeper material; it is not a manual.

### Bundle layout rules

- Keep references **one level deep** from `SKILL.md`. Do not chain `SKILL.md → A.md → B.md`; the model may use `head -100` to preview intermediates and miss downstream content.
- Name files descriptively (`form-validation-rules.md`, not `doc2.md`).
- Use forward slashes in paths, on every platform.

### Add a table of contents to long reference files

For any reference file over **~100 lines**, place a short table of contents at the top. The model often previews large files with partial reads; without a TOC, it sees only the first slice and can't tell what else is in the file. A TOC ensures it can see the full scope on the first read and jump to the relevant section.

```markdown
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
…

## Core methods
…
```

Keep the TOC compact – one line per section, no nested sub-bullets unless a section is genuinely deep. The TOC is a *map*, not an outline; the value is letting the model decide where to read next, not telling it everything the section will say.

### Three disclosure patterns

**Pattern 1 – High-level guide with references.** `SKILL.md` carries the quick start and points to reference files for advanced topics:

```markdown
## Quick start
[concise minimum content]

## Advanced features
**Form filling**: See [FORMS.md](FORMS.md)
**API reference**: See [REFERENCE.md](REFERENCE.md)
**Examples**: See [EXAMPLES.md](EXAMPLES.md)
```

**Pattern 2 – Domain-specific organization.** When content splits cleanly by domain, organize references by domain so the model loads only what the current task needs:

```
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md
    ├── sales.md
    ├── product.md
    └── marketing.md
```

`SKILL.md` lists each domain with a one-line summary and a link. A query about revenue loads `finance.md` only.

**Pattern 3 – Conditional details.** Show the basic content inline; link to advanced content for cases the user might or might not hit:

```markdown
## Editing documents
For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

---

## Frontmatter

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | yes | Identity and slash-command trigger. ≤64 chars, lowercase letters/digits/hyphens only. No reserved words ("anthropic", "claude"). |
| `description` | yes | The discovery trigger. 1–1024 chars. See *Description Engineering* below. |
| `when_to_use` | no | Extra trigger context, appended to `description` in the skill listing (combined cap ~1,536 chars in Claude Code). |
| `argument-hint` | no | Shown in autocomplete (e.g. `[issue-number]`). |
| `allowed-tools` | no | **Pre-approves** tool calls while the skill is active. Does not restrict – session permissions still apply for unlisted tools. |
| `disable-model-invocation` | no | `true` removes the skill from automatic discovery; only the user can invoke. Use for side-effectful workflows (deploy, send-message, commit) where you don't want the model deciding timing. |
| `user-invocable` | no | `false` hides the skill from the `/` menu but leaves it in the model's background knowledge. |
| `context: fork` | no | Runs the skill in an isolated subagent context. The skill body becomes the subagent's prompt – no access to outer conversation. Only useful when the skill contains an actionable task, not bare guidelines. |
| `model`, `effort` | no | Per-skill model and effort overrides; revert on return. |
| `paths` | no | Glob patterns gating auto-activation to matching files. |
| `hooks`, `shell` | no | Lifecycle hooks; default shell for embedded `!` blocks. |

### Naming conventions

Prefer **gerund form** (verb + `-ing`) – it clearly describes the activity:

- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

Acceptable alternatives: noun phrases (`pdf-processing`), action-oriented (`process-pdfs`).

Avoid: `helper`, `utils`, `tools`, `documents`, `data`, `files`, reserved words.

---

## Description Engineering: the Trigger Surface

The `description` is the **only signal** the model uses to decide whether to activate a skill from a list that may number in the hundreds. It is loaded into every system prompt; nothing else from the skill is visible until it fires. Treat description authoring as a discrete craft.

**Rules:**

1. **Always third person.** *"Processes Excel files and generates reports"*, not *"I help with Excel"* or *"You can use this to…"*. Mixed point-of-view degrades discovery.
2. **Encode *what* and *when*.** Capability alone is insufficient; include the trigger conditions.
   - Good: *"Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."*
   - Bad: *"Helps with documents."*
3. **Include user vocabulary.** Add the phrases users actually say – synonyms, casual terms, error messages.
4. **Add a negative constraint when scope is easily confused with a sibling skill.** *"Do not use when the user wants to execute an existing spec – use `exec-spec` for that."* Negative constraints prevent the most common mis-fire.
5. **Put the load-bearing trigger first.** Descriptions can be budget-trimmed in long skill listings; the first sentence must do the work.
6. **Do not write a manual.** The description is a trigger, not documentation.

**Common failure modes:** too vague (never selected); too broad (fires on unrelated tasks – tighten with a negative constraint, or set `disable-model-invocation: true`); terminology drift between description and body (the model triggers on a term the body never explains).

---

## Writing the Body

The body is read once, when the skill fires. Optimize for the model that will execute it, not the human who reads it on GitHub.

### Intent over procedure

State the **goal, the success criteria, and the failure modes**. Let the model fill in routine engineering decisions. Be specific about counter-intuitive behavior, cross-skill contracts, named failure modes, and gates. Be general about standard engineering practices. If a frontier model would naturally do something competently, don't instruct it.

### Why before what

A rule without a *why* is followed rigidly; a rule with a *why* is followed intelligently and generalizes to edge cases the author didn't enumerate. The tokens spent on rationale are not waste – they prevent the model from rationalizing past the rule when conditions shift.

### Degrees of freedom

Match instruction specificity to **task fragility**. The same skill can use different freedom levels in different sections.

| Level | When to use | Form |
|-------|-------------|------|
| **High freedom** | Multiple valid approaches; decisions depend on context | Text-based instructions, heuristics |
| **Medium freedom** | A preferred pattern exists; some variation acceptable | Pseudocode, parameterized templates, scripts with options |
| **Low freedom** | Fragile or error-prone operations; consistency critical | Specific scripts, few or no parameters, exact commands |

**Analogy.** Treat the model as a robot navigating a path:
- *Narrow bridge with cliffs on both sides* → only one safe way forward; specific guardrails and exact instructions (low freedom). Example: database migrations that must run in exact sequence.
- *Open field with no hazards* → many paths lead to success; general direction is enough (high freedom). Example: code reviews where context determines the best approach.

The wrong freedom level either over-constrains (model can't adapt when the situation deviates) or under-constrains (model freelances on a fragile step).

### Named principles over unnamed rules

Give load-bearing rules a name. *Stop-the-Line*, *Chesterton's Fence*, *Surgical Scope*, *Anti-Rationalization* – a named principle is a conceptual anchor the model can recall, apply, and explain. An unnamed rule is just another bullet competing for attention.

### Gates over steps

For workflow skills, name what must be **true to advance** at each phase, not just what to do. A gate ("PRD read once and held in working notes") is a falsifiable condition; a step ("read the PRD") is satisfiable by appearance.

### Structured output blocks

When the skill needs to surface uncertainty, blocked work, or out-of-scope observations, use **named blocks** with a consistent grammar:

```
CONFUSION: <what is ambiguous> – <which decision is needed>
BLOCKED: <external blocker> – <minimum info to unblock>
NOTICED BUT NOT TOUCHING: <pre-existing issue> – <suggested follow-up>
MISSING REQUIREMENT: <undefined behavior> – <which behavior to choose>
```

Named blocks let downstream skills and orchestrators parse responses deterministically, and discourage silent rationalization past uncertainty.

### Repetition is dilution

When a rule feels weak, the fix is *not* restating it three times. Restatements compete for attention and dilute every copy. Instead: name the specific failure mode being prevented, and explain the consequence.

---

## Workflows and Feedback Loops

### Use workflow checklists for complex multi-step tasks

For workflows with several sequential steps, provide a checklist the model can **copy into its response and tick off** as it progresses. This prevents skipped steps and creates a visible trace of progress.

```markdown
## Form-filling workflow

Copy this checklist and check off items as you complete them:

- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`
This extracts form fields and their locations, saving to `fields.json`.

[…]
```

The pattern works equally well for **non-code workflows** (research synthesis, document review). The checklist's value is structural, not language-specific.

### Implement feedback loops on quality-critical steps

The pattern: **run validator → fix errors → repeat → only proceed when clean**. Drastically improves output quality on tasks where the first draft is unreliable.

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message
   - Fix the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild and test the output document
```

Feedback loops don't require code. The "validator" can be a `STYLE_GUIDE.md` checklist that the model reads and compares its draft against.

---

## Output Patterns

Three named patterns for shaping skill output. Pick the one whose strictness level matches what you need.

### Template pattern

Provide an output template. Choose strict or flexible:

**Strict** – use when downstream parsing or consistency matters:

```markdown
## Report structure

ALWAYS use this exact template:

# [Analysis Title]
## Executive summary
[One-paragraph overview]
## Key findings
- Finding 1 with supporting data
…
```

**Flexible** – use when adaptation is genuinely useful:

```markdown
## Report structure

Here is a sensible default format; adapt sections to the analysis type:

# [Analysis Title]
## Executive summary
[Overview]
…
```

### Examples pattern

When output quality depends on style or formatting nuance, provide **input/output pairs**. The model picks up style from examples more reliably than from descriptions.

```markdown
## Commit message format

**Example 1**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```
```

### Conditional workflow pattern

Guide the model through decision points by naming the branches:

```markdown
## Document modification workflow

1. Determine the modification type:
   - **Creating new content?** → Follow "Creation workflow" below
   - **Editing existing content?** → Follow "Editing workflow" below

## Creation workflow
- Use docx-js library, build from scratch, export to .docx

## Editing workflow
- Unpack the document, modify XML directly, validate after each change, repack
```

If branches become long, move each into its own reference file and have `SKILL.md` route to the right one.

---

## Scripts and Executable Content

Skills that bundle scripts have additional discipline. Script source code does **not** enter context when executed – only stdout does. A 200-line script costs ~0 tokens at runtime; a 200-line procedural explanation costs ~2k. Prefer scripts for anything deterministic.

### Solve, don't punt

Scripts should **handle error conditions explicitly**, not bubble unstructured failures to the model:

```python
def process_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, "w") as f:
            f.write("")
        return ""
    except PermissionError:
        print(f"Cannot access {path}, using default")
        return ""
```

Validation scripts should produce **verbose, specific** error messages: *"Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed"* – not just *"validation failed"*. Specific messages give the model enough information to fix issues without re-reading the source.

### No voodoo constants

Every magic number should justify itself. If you don't know the right value, the model won't either:

```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

Not `TIMEOUT = 47` with no explanation.

### Prefer utility scripts over generated code

When the same operation appears repeatedly, ship a script. Benefits:

- **More reliable** than freshly generated code (no syntax drift, no missing edge cases).
- **Saves tokens** – script body is never loaded into context.
- **Saves time** – no code-generation step.
- **Ensures consistency** across uses.

**Make execution intent explicit.** State whether the model should *execute* the script or *read* it as reference:

- *"Run `analyze_form.py` to extract fields"* → execute
- *"See `analyze_form.py` for the field-extraction algorithm"* → read

Most utility scripts should be executed, not read.

### Verifiable intermediate outputs (plan-validate-execute)

For batch operations, destructive changes, or high-stakes workflows, insert a **plan step that produces a structured intermediate artifact**, validate it, then execute:

```
analyze → create plan file (e.g. changes.json) → validate plan → execute → verify
```

Benefits: errors caught before changes are applied; machine-verifiable; the plan is reversible without touching originals; debugging is precise because the plan is concrete.

When to use: batch updates, destructive operations, complex validation rules, anything where rollback is painful.

### Visual analysis

When inputs can be rendered as images, have the model **see** them rather than reason about their structure abstractly. Particularly useful for forms, layouts, and any visual structure:

```markdown
## Form layout analysis

1. Convert PDF to images:
   `python scripts/pdf_to_images.py form.pdf`
2. Analyze each page image to identify field locations and types visually
```

### MCP tool references

Always use **fully qualified** MCP tool names – without the server prefix, the model may fail to locate the tool when multiple servers are connected:

```
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

Format: `ServerName:tool_name`.

### Package dependencies

Declare dependencies explicitly in `SKILL.md`; do not assume packages are installed:

- **Bad:** *"Use the pdf library to process the file."*
- **Good:** *"Install required package: `pip install pypdf`. Then…"*

Be aware of execution-environment constraints: some platforms allow package installation at runtime, others do not. State the assumption your skill makes.

---

## Execution Skills Run Headless; Discovery Skills Interact

**Execution skills** (skills whose deliverable is implementation, verification, or deterministic operations – the `exec-*`, `quick-implement`, `ops`, `simplify-code`, `refactor`, `remediate-findings` family, plus the artifact-producers like `prd`/`plan`/`spec`) **run to completion** without waiting for a user turn. For these skills, prefer:

- **Explicit assumptions** recorded in the artifact.
- **Conservative defaults** when input is ambiguous.
- **Documented open questions** at the end of the run.

Over:

- "STOP and WAIT for user input" patterns.
- Mid-run confirmation prompts.
- Asking the user to choose between options the skill could pick reasonably.

When such a skill *does* need to gate on user input, name the gate (`BLOCKED:` block) and the exact information that would unblock it.

**Discovery and design skills** (clarification, product/feature discovery, trade-off analysis, architectural advise, event-storming, strategic design, init) are **interactive by nature**: the user back-and-forth IS the deliverable, not an obstacle to it. These skills declare a named *Interactive-by-Contract* principle, gate the relevant steps explicitly, and use a question tool (`AskUserQuestion` when available, numbered markdown fallback otherwise) – the headless-execution rule above does not apply to them.

---

## Tool Allowlisting and Security

`allowed-tools` is a **pre-approval** mechanism, not a sandbox. It lowers friction for the user; it does not constrain what the skill can attempt.

Treat installed skills like installed software:

- Source matters. A skill can direct the model to invoke tools or execute code in ways that don't match its stated purpose.
- Be especially careful with skills that fetch external URLs at runtime; fetched content can contain prompt-injection payloads.
- Do not embed credentials, API keys, or environment-specific paths in shipped skill content.

When authoring, restrict `allowed-tools` to what the skill actually needs – this is for the user's benefit, not for security, but it makes review legible.

---

## Token Economy

Assume the model is already capable. Each line of context must earn its place. Quick test for any paragraph: *Does the model already know this? Does this paragraph justify its token cost?*

Compare:

**Concise (~50 tokens):**
````markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**Verbose (~150 tokens):**
```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but
pdfplumber is recommended because it's easy to use…
```

The verbose version assumes the model doesn't know what PDFs are and how libraries work. It wastes ~100 tokens on baseline knowledge the model has.

Token-saving moves:

- **Tables over prose** for dense reference material.
- **Decision trees over prose** for branching workflows.
- **Defer to references** for content only relevant on some paths.
- **Defer to scripts** for deterministic operations.
- **Cut content that restates model defaults.**

---

## Anti-Patterns

The body sections above already frame their own anti-patterns as named positive rules. The three below have no positive counterpart in the body and warrant their own callout.

- **Too many options.** Listing four libraries that can each solve the task and asking the model to pick. Choose a default, add an escape hatch (*"For scanned PDFs requiring OCR, use pdf2image with pytesseract instead"*).
- **Time-sensitive instructions.** *"If before August 2025, use the old API."* Replace with a current path and an "old patterns" reference block that quarantines deprecated guidance from the main flow.
- **Inconsistent terminology.** Mixing *endpoint* / *URL* / *route* / *path*, or *field* / *box* / *element*, in the same skill. Pick one term per concept and use it throughout – the model treats lexical drift as semantic drift.

---

## Iterating: Evaluation-Driven Authoring

### Build evaluations first

Write the evaluation **before** writing extensive documentation. This grounds the skill in real failures rather than imagined ones.

1. Run the model on representative tasks *without* the skill. Note specific failures.
2. Build **at least three** evaluation scenarios covering those failures.
3. Establish a baseline (how often does the model succeed unaided).
4. Write the **minimum** skill content needed to pass the evaluations.
5. Iterate: run evals, compare to baseline, refine.

A useful evaluation structure:

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads the PDF using a suitable library or tool",
    "Extracts text from all pages without skipping any",
    "Saves the result to output.txt in a clear, readable format"
  ]
}
```

### The two-instance method (author / executor)

Use one model instance to **author** the skill (the *author*) and a *fresh* instance with the skill loaded to **execute** representative tasks (the *executor*). The author understands intent; the executor reveals gaps through actual behavior. Observe the executor and bring specific observations back to the author:

- **Unexpected exploration order** → the skill's structure isn't intuitive.
- **Missed references** → links need to be more explicit or prominent.
- **Overreliance on one section** → that content should be in `SKILL.md` body.
- **Files never accessed** → either unnecessary or poorly signaled.
- **Trigger doesn't fire when it should** → description needs more user vocabulary.

### Test across model tiers

Run skills against Haiku, Sonnet, and Opus where available. Different questions per tier:

- **Haiku** – does the skill provide *enough* guidance?
- **Sonnet** – is the skill clear and efficient?
- **Opus** – does the skill avoid *over*-explaining?

What works for Opus often needs more detail for Haiku; what's right for Haiku may be over-specified noise for Opus. The mismatch tells you where the skill is leaning on raw model capability rather than its own structure.

### Gather real-usage feedback

If the skill is used by others (or other agents), share it and observe usage. Ask: does the skill activate when expected? Are instructions clear? What's missing? Real usage reveals blind spots that authoring-time review never surfaces.

---

## Checklist for an Effective Skill

Before publishing, verify:

**Core quality**
- [ ] Description is specific, third-person, and includes both *what* and *when*
- [ ] Name uses gerund form (or other consistent convention) and avoids vague words
- [ ] `SKILL.md` body is under 500 lines
- [ ] References are one level deep
- [ ] Long reference files (>100 lines) have a table of contents
- [ ] Consistent terminology throughout
- [ ] No time-sensitive information (or quarantined in an "old patterns" block)
- [ ] Workflows have clear steps and gates
- [ ] Progressive disclosure used appropriately

**Code and scripts** (if applicable)
- [ ] Scripts handle errors explicitly, don't punt to the model
- [ ] All constants are justified (no voodoo numbers)
- [ ] Required packages listed and verified available in the runtime
- [ ] All paths use forward slashes
- [ ] Validation steps included for critical operations
- [ ] Feedback loops on quality-critical tasks
- [ ] Execute-vs-read intent stated for each script
- [ ] MCP tools referenced with fully qualified `Server:tool` names

**Testing**
- [ ] At least three evaluation scenarios exist
- [ ] Tested with each model tier you plan to use
- [ ] Tested with realistic usage scenarios, not just synthetic prompts
- [ ] Real-usage feedback incorporated (where applicable)

---

## Layering: Where This Doc Fits

| Topic | Where it lives |
|-------|----------------|
| Generic prompting craft (altitude, examples, structure) | `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES.md` |
| Claude-specific prompting (XML, thinking blocks, etc.) | `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES-CLAUDE.md` |
| GPT-specific prompting | `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES-GPT.md` |
| Skill packaging, discovery, frontmatter, bundle architecture, output patterns | *this document* |
| Non-negotiable engineering rules | `docs/guidelines/CRITICAL-RULES-AND-GUARDRAILS.md` |

When skill craft and general prompt craft both apply, skill craft wins for skill files.

---

## References

- Anthropic: Agent Skills best practices – https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Anthropic: Agent Skills overview – https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code skills documentation – https://code.claude.com/docs/en/skills
- Anthropic engineering blog: *Equipping agents for the real world with Agent Skills* – https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic public skills repository – https://github.com/anthropics/skills
