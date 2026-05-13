# FIS Authoring Guidelines

Shared authoring guidelines for generating Feature Implementation Specifications (FIS). Referenced by `spec` (standalone) and `plan` (batch FIS generation).


## FIS Authoring Principles

FIS is an executable spec: intent over implementation, references over content, decisions not explanations.

> **FIS Mutability**: see [`data-contract.md`](${CLAUDE_PLUGIN_ROOT}/references/data-contract.md) – *FIS Mutability Contract*.


## Cross-Document References

Every reference from a FIS to another document (PRD, plan, research, ADRs, guidelines, glossary) is a **trust boundary**: the intent behind that reference lives with the author, not the executor. Punting the resolution ("see the plan") forces every downstream reader – exec-spec, review, remediate-findings, council reviewers – to re-discover what the author already knew. Precision at spec time eliminates that duplication.

### Two-tier model

- **Required Context** (load-bearing, inlined verbatim) – spans the executor *must* know to act on the FIS. Pulled from the source at spec time, inlined as a block in the FIS, pinned with `<!-- source: path#anchor -->` and `<!-- extracted: <commit-sha when source is in this repo; YYYY-MM-DD otherwise> -->` comments for audit. Prefer the commit SHA when available – it's a precise pointer; the date is the fallback for sources outside the repo or not yet committed. The inlined text is authoritative at execution time even if the source later drifts.
- **Deeper Context** (optional, anchored pointers) – supplementary material available if the inlined Required Context leaves a gap. Each bullet is `path/to/source.md#heading-slug – one-line description`. Readers resolve on demand. Anchors are validated at authoring time; broken anchors found post-spec are a doc-review finding, not an execution blocker.

### Authoring rules

1. **Prefer anchors over line numbers – for docs *and* code.** `prd.md#error-handling` and `src/auth.ts#validateToken` survive source edits; `prd.md:42-78` and `src/auth.ts:120-145` rot on the first line shift. For docs lacking stable headings, favor adding `<a id="..."></a>` markers in the source over fragile line references. For JSON sources like `plan.json`, anchor by story id (`stories[]` is keyed conceptually by `id`) rather than file offset. For code, use this fallback ladder:

   | Form | When to use | Example |
   |---|---|---|
   | `path#Symbol` | A named function/class/method/exported identifier exists. If multiple symbols share the name (overloads, merged declarations, `function format` + `class Format`), qualify as `Container.member` or fall back to the line-range row | `src/auth.ts#validateToken` |
   | `path#key.path` *(unquoted)* | Config/YAML/JSON nested key – dots walk into nested maps | `definitions/spec.yaml#steps.spec.skill` |
   | `path#"key.with.dots"` *(quoted)* | The key name itself literally contains dots – quotes prevent the dotted-walk interpretation | `config.yaml#"feature.flag.v2"` |
   | `path:LINE-LINE` | **Fallback only** – sub-region of a larger symbol where the span matters and no stable identifier exists | `src/parser/index.ts:120-145` |

   For multiple related symbols in one file, list one row per symbol; for a pattern spanning several symbols, anchor the row at the primary symbol and name the related symbols in the why column. Comma-joined fragments (`path#A,B`) break URL encoding and markdown rendering when the FIS is published to GitHub – don't use them.

   **Pair every reference with intent**: the why column states *what the executor should learn* from this pointer, not just a label ("Dialog pattern – copy focus-trap + escape-key handling", not "Pattern for dialog handling"). This applies wherever the ladder is used (Code Patterns table, task pattern references).

   **Scope**: this rule governs *new* FIS authoring. Reference rows pre-existing in a FIS are not retroactive findings; rows added or rewritten in the change set are in scope per normal review calibration.

   `path#X` is interpreted by file kind: markdown sources resolve to heading slugs, code/config sources to symbols or keys per the ladder. The convention is parseable text, not a navigable link in standard renderers.
2. **Resolve at authoring time, not execution time.** Before emitting the FIS, walk every cross-doc reference, extract the span, and decide required vs deeper. A bare "see the plan" without anchor or inlined content is not acceptable – the author saw the source, so the author names what matters.
3. **Inline budget.** Per block: typically 30-100 lines, hard cap 200 lines (only when a single load-bearing span legitimately needs more). Total across all blocks: ≤ 250 lines, so the FIS stays inside the 200-500 line sweet spot with room for Scenarios and Tasks. When the per-block cap is hit, narrow the extraction and move overflow to Deeper Context; when the total budget would be breached by additional blocks, downgrade lower-priority blocks. The 200-line per-block cap and 250-line total are not additive – a FIS with two blocks at the per-block hard cap (400 lines) breaches the total and must be cut down.
4. **Keep code pointers out of Required Context.** `src/foo.ts#parseFoo` pattern pointers belong inside task descriptions or in `Code Patterns & External References`. Required/Deeper Context is reserved for upstream *intent* documents (PRD, plan, ADRs, guidelines, glossary).
5. **Omit empty sections.** If a FIS has no load-bearing upstream spans to inline, omit the Required Context section entirely rather than leaving a stub. The same applies to Deeper Context – omit when there are no supplementary pointers worth surfacing. Standalone FIS with no PRD/plan upstream typically have neither section.

### Why the inlined text is authoritative

A FIS is a contract with the executor. If the author pulls text from `prd.md` or a story scope from `plan.json` at spec time, that's the intent the FIS is committing to – even if the upstream source later changes. Drift between the pinned span and the current source is a *review* signal (the FIS may need re-spec'ing), not an *execution* failure. Required Context is a point-in-time intent snapshot, not a live join.


## Scenarios and Proof-of-Work

Each scenario: one behavior, concrete Given/When/Then using actual codebase identifiers. Cover happy path first, then edge cases, then at least one error case. 3-7 scenarios is the sweet spot. If you can't write the **Then** clause, surface it as ambiguity.

### Scenario Authoring Principles

Dan North's "Introducing BDD" (2006) anchors scenarios as Given/When/Then examples; Liz Keogh's "Acceptance Criteria vs. Scenarios" (2011) separates abstract rules from concrete examples. Apply these principles:

- **Concrete over Abstract** – use actual data: "Given Fluffy is 3 weeks old" instead of "Given an animal under selling age".
- **Observable Boundary** – assert visible behavior: "Then checkout rejects the sale" instead of "Then `AgePolicy.validate()` returns false".
- **Declarative over Imperative** – state precondition, event, outcome: "When checkout runs" instead of "When the test constructs mocks and calls methods".

**Negative-path checklist** – after drafting scenarios, review for these three categories. Add one scenario per uncovered category (the riskiest gap), not one per parameter. The 3-7 target still applies.

- **Omitted optional inputs**: null/absent case producing a fragile default (empty string instead of null, zero instead of absent)?
- **No-match cases**: selectors, filters, or lookups where "nothing matches" falls through to an unintended default?
- **Rejection paths**: external integration points where unmatched/invalid input should be explicitly ignored or rejected?

**Proof-of-Work**: Every Success Criterion must have a proof path – at least one scenario (behavioral) or task Verify line (structural). The FIS locks down what proof is required; exec-spec produces and verifies it. Testing Strategy maps scenarios to task IDs so proof is produced incrementally, not deferred.

**Traceability**: Plan stories carry compact scope and source refs, while the FIS owns detailed Success Criteria and Scenarios. Read the story's Source refs for detailed PRD behavior. If a legacy plan includes **Key Scenarios** or acceptance criteria, treat them as seeds and map each retained seed to at least one FIS scenario – don't silently drop them.

## Execution Contract

Include the template's **Execution Contract** section near the bottom of the Implementation Plan. Extend it only if the feature truly needs feature-specific execution constraints; for lightweight specs, phrase the validation bullet around the checks that actually exist.


## Key Generation Guidelines

1. **Outcomes, not code changes**: Each task describes what must be TRUE when done, not what code to write. The executing agent determines the implementation.
2. **Task brevity**: Each task description is 1-3 lines. State the outcome, reference the pattern (`file#symbol` – see Cross-Document References rule #1 for the symbol-anchor ladder), include the Verify line. If a task description exceeds 3 lines, it is either too large (split it) or too detailed (describe the outcome, not the steps).
3. Each task: atomic, self-contained, with `file#symbol` references to patterns to follow. Order tasks so later tasks can build on earlier ones without hidden dependencies (see Task Ordering below)
4. Reference patterns, don't reproduce them
5. Each task must include a **`Verify:`** line – a concrete, observable check proving the outcome. **Verify lines must assert the described behavior, not just build success.** At least one assertion per task should fail if the outcome is not achieved. Trace verification back to the feature's Success Criteria where applicable.

   **Prescriptive details must be in Verify lines.** When the FIS prescribes specific outputs (column names, format strings, error messages, file locations), the Verify line MUST check the prescribed detail verbatim – not just that "output exists." A proof check that doesn't name the prescribed detail lets the implementation satisfy the task in spirit while missing the exact contract.

   - Weak: `Verify: traces list shows token breakdown` (doesn't name the columns)
   - Strong: `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`

   Rule of thumb: if you prescribed a specific format, column name, file path, or string in the FIS – put it in the Verify line verbatim.
6. Most good FIS files land in the 200-500 line range. Once a draft starts pushing past roughly ~700 lines or more than ~18 tasks, that is a strong signal that this is no longer one execution-sized spec. Save the FIS regardless, but warn the user and recommend a path: for standalone feature requests, switch to the `/andthen:prd → /andthen:plan → /andthen:exec-plan` chain so the work goes through proper PRD-backed planning; for `story {story_id} of plan.json` inputs, the story was too broad – revisit the source plan and decompose it before regenerating specs.
7. Replace `<path-to-this-file>` in the self-executing callout with the actual FIS output path
8. Make **What We're NOT Doing** explicit: 3-5 specific exclusions or deferrals with reasons. Use it to preserve scope boundaries across sessions, not as filler.
9. Include the **Execution Contract** section from the template. Keep it consistent unless the feature truly needs extra execution-specific constraints.


## Task Ordering

After defining individual tasks (TI01, TI02...), order them so the implementation can proceed sequentially without hidden orchestration metadata. The task list itself should make the dependency path obvious.

Put foundational tasks first, then widening tasks, then polish/integration tasks. Keep related tasks adjacent when they share context, but don't introduce separate grouping syntax unless the document genuinely needs it for reader clarity.

When a later task must consume something from an earlier task (an API, a type, a component), state this explicitly in the later task's description. Don't rely on the executing agent discovering it from context. Example: if TI01 creates `effectiveConcurrency()`, TI03 should say "Dispatch loop MUST use `effectiveConcurrency()` from TI01 for concurrency cap."


## Plan-Spec Alignment Check (when FIS originated from a plan story)

Before finalizing, cross-check the plan story brief, its Source refs, and any applicable Binding Constraints against the FIS:
- Verify the FIS Success Criteria and Scenarios deliver the story scope and every applicable Binding Constraint.
- If the FIS cannot fully satisfy the story scope (due to exclusions, architectural constraints, or "What We're NOT Doing" items), you MUST either:
  (a) Expand the FIS scope to address the story, or
  (b) Add a scope note to the FIS explaining the narrowing (e.g., "replace-mode harnesses only; see Constraints") and flag it for the `andthen:plan` cross-cutting review.
- Do not finalize a FIS that silently narrows a plan story or Binding Constraint.


## Reverse Coverage Check (phantom-scope guard) – applies to all FIS

Forward coverage (above) catches plan criteria the FIS misses. Reverse coverage catches the opposite: FIS work no upstream asked for.

> Distinct from Self-Check's **Scope-consistency** (internal: In Scope → coverage within the FIS). Reverse Coverage is external: Success Criterion → upstream source.

For each FIS Success Criterion, name the plan story scope, Source ref, Binding Constraint, PRD outcome, or (standalone) feature-request element it serves. Any unnamed criterion is **phantom scope**.

**Resolution depends on mode:**

- **Batch sub-agent mode** (from the `andthen:plan` skill) – sub-agents check Success Criteria against plan-level sources **plus the `bindingConstraints[]` array in `plan.json`** when non-empty (each entry's `verbatim` text and `anchor` are the binding source). A criterion that traces to either is sourced; only criteria with no plan-level *and* no Binding Constraints source are candidates for phantom-scope reporting. For each candidate, either (a) remove the criterion, or (b) return a `PHANTOM_SCOPE` entry in your completion summary so the orchestrator can escalate – at the cross-cutting review the orchestrator filters once more against the full `prd.md` to catch any constraint missed by the inline extraction. Do not rationalize by adding scope notes. **Do not edit `plan.json` or `prd.md` from a sub-agent** – phantom-scope resolution flows through the orchestrator only.
- **Standalone mode**: (a) remove, or (b) raise with the user and – on approval – add a scope note documenting the proposed addition for plan/PRD amendment.
- **Standalone with no plan or PRD at all**: accept the criterion only if it traces to a user- or business-observable outcome in the feature request. "Uses X library", "refactors Y" are phantom scope absent a user-facing reason.

Do not finalize a FIS with Success Criteria the upstream contract doesn't justify.


## Self-Check

Quick sanity check before saving:
- [ ] **Template structure**: follows Key Generation Guidelines – ADR states decision, no over-specification or code snippets >5 lines
- [ ] **Size check**: see Key Generation Guidelines #6 – if oversized, emit the `OVERSIZE:` signal
- [ ] **Scope-consistency**: every "In Scope" item exercised by a scenario or Verify line; see Reverse Coverage Check + In-Scope rules
- [ ] **Coverage**: every Success Criterion has a proof path; see Scenarios and Proof-of-Work (negative-path checklist)

### Confidence Check
Rate your FIS 1-10 for single-pass implementation success:
- **9-10**: All context present, clear decisions, validation automated
- **7-8**: Good detail, minor clarifications might be needed
- **<7**: Missing context, unclear architecture, needs revision

**If score <7**: Revise or ask for user clarification.

**If score <7 AND FIS exceeds size thresholds**: see Key Generation Guidelines #6.
