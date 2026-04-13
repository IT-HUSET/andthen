---
description: >
  Deep quantitative architecture review: dependency metrics (Ca, Ce, I, A, D),
  connascence analysis, decomposition evaluation, and fitness function proposals.
  Synthesizes Ford & Richards, Farley, Martin's Package Principles, and Building
  Evolutionary Architectures. Use for package structure assessment, split/merge
  decisions, coupling analysis, or architectural governance.
user-invocable: true
argument-hint: "[scope/path] [--mode review|decompose|advise|fitness] [--to-issue] [--to-pr <number>]"
---

# Architecture Review

Deep structural analysis of package/module architecture using quantitative metrics, connascence taxonomy, and established frameworks.

## VARIABLES

ARGUMENTS: $ARGUMENTS

### Mode (auto-detected from arguments or explicit `--mode`)

| Mode | Triggers | References to load |
|------|----------|-------------------|
| **review** (default) | "review architecture", "assess health", "analyze structure", "modularity check" | `connascence.md`, `package-principles.md`, `anti-patterns.md`, `review-output.md` |
| **decompose** | "should I split", "merge these", "extract package", "decomposition", "too big" | `decomposition.md`, `connascence.md`, `package-principles.md`, `anti-patterns.md` |
| **advise** | architectural questions, "which pattern", "how should I structure", trade-off questions | Load references relevant to the specific question |
| **fitness** | "fitness functions", "governance", "architectural tests", "prevent drift" | `fitness-functions.md`, `package-principles.md`, `quanta.md` |

### Optional Output Flags
- `--to-issue` -> PUBLISH_ISSUE
- `--to-pr <number>` -> PUBLISH_PR

## INSTRUCTIONS

- When `ARGUMENTS` is empty or ambiguous (no clear mode or scope), start with guided setup (see Phase 0). Do not assume a mode or run a full-project review by default.
- Read the Workflow Rules, Guardrails, and relevant project guidelines before starting.
- Analysis only. Do not modify code.
- Calibrate severity with `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and `references/architecture-review-calibration.md`.
- Read project learnings if they exist.
- Load only the reference files needed for the detected mode — do not load all references upfront.
- Adapt all tooling suggestions, metric computation, and fitness function implementations to the detected language.
- **Evidence over opinion**: compute metrics and analyze structure before forming conclusions. Never report "this module seems too large" — report specific metric values, file paths, and import chains.
- **Framework attribution**: every recommendation cites a named principle (e.g. "Per SAP (Martin)..." or "Ford/Richards disintegration driver #3...").
- **Actionable findings**: every finding includes a concrete remediation path and a fitness function to prevent recurrence.
- **Progressive improvement**: support the "frozen rules" pattern — snapshot current violation count, fail CI only on regressions.
- **Multi-scale awareness**: tag findings by C4 level (Context / Container / Component / Code).
- **Connascence-aware coupling**: classify coupling by connascence type, not just edge count. High Ca with all-CoN connections is manageable; low Ce with CoI connections is dangerous.

## GOTCHAS

- Running a full-project review when invoked with no arguments instead of asking the user what they want
- Reporting opinions without computed metrics
- Loading all 7+ reference files when the mode only needs a subset
- Treating infrastructure packages in Zone of Pain as problems (database drivers, runtime bindings may legitimately sit there)
- Missing dynamic connascence crossing package boundaries (always HIGH or CRITICAL)
- Recommending decomposition without scoring integration drivers alongside disintegration drivers
- Inflating severity for borderline metrics — report as INFO with context, not HIGH

## WORKFLOW

### Phase 0: Guided Setup _(when ARGUMENTS is empty or ambiguous)_

When invoked without clear mode and scope, guide the user interactively:

1. Present the available modes with one-line descriptions:
   - **review** — Full health assessment: dependency metrics, connascence analysis, anti-pattern scan, fitness function proposals
   - **decompose** — Evaluate a specific split/merge decision with Ford/Richards driver scoring
   - **advise** — Answer an architectural question grounded in established frameworks
   - **fitness** — Propose fitness functions for architectural governance and ADR enforcement

2. Ask what they want to accomplish and which part of the codebase to focus on. For **decompose**, also ask which boundary or package they're evaluating. For **advise**, ask for the specific question.

3. Confirm mode and scope before proceeding to Phase 1.

**Gate**: Mode and scope confirmed by user

### Phase 1: Context & Setup

1. Parse mode from `ARGUMENTS` (auto-detect or explicit `--mode`), or use the mode confirmed in Phase 0.
2. Read project rules, guidelines, and existing ADRs.
3. Detect the primary language from project files:

   | Indicator | Language | Tooling |
   |-----------|----------|---------|
   | `pubspec.yaml` | Dart | `lakos` (metrics + cycles), `dart pub deps --json`, `dart analyze` |
   | `package.json` | JavaScript/TypeScript | `dependency-cruiser` (rules + metrics), `madge` (cycles) |
   | `go.mod` | Go | `go mod graph`, custom cycle detection |
   | `pom.xml` / `build.gradle` | Java/Kotlin | ArchUnit (architecture tests), JDepend (metrics) |
   | `*.csproj` / `*.sln` | C#/.NET | NetArchTest, NDepend |
   | `pyproject.toml` / `setup.py` | Python | Deptry, pydeps, import-linter |
   | `Cargo.toml` | Rust | `cargo tree`, `cargo udeps` |

4. Load only the references needed for the detected mode (see Mode table above).

**Gate**: Mode, scope, language, and references are clear

### Phase 2: Analysis

Execute the analysis for the detected mode.

#### Review Mode

Full architecture health assessment.

**Step 1 — Discover Structure**
Map the package/module structure. For monorepos or workspaces, identify all packages and their declared dependencies.

**Step 2 — Compute Dependency Graph & Metrics**
Use language-appropriate tools to extract:
- **Dependency graph** (directed edges between packages/modules)
- **Per-package metrics**: Ca (afferent), Ce (efferent), I (instability), A (abstractness), D (distance from main sequence)
- **Graph-level metrics**: CCD, ACD, NCCD (if tooling supports)

Refer to `references/package-principles.md` for metric definitions and thresholds.

**Step 3 — Structural Checks**
Check each principle systematically:
1. **ADP** — Are there cycles? (Always a finding if yes)
2. **SDP** — For each dependency edge A -> B: is I(A) >= I(B)? Flag violations
3. **SAP** — For packages with I < 0.3: is A > 0.3? Flag stable-but-concrete packages
4. **Zone analysis** — Flag packages with D > 0.3 and classify Zone of Pain vs Zone of Uselessness
5. **God modules** — Flag packages with Ce > 10 or unusually high LOC relative to siblings

**Step 4 — Connascence Analysis**
For the highest-coupling boundaries (top 3-5 by Ce or most frequently crossing), classify the connascence type at each boundary. Refer to `references/connascence.md` for the taxonomy and severity scoring formula.

Flag any dynamic connascence (CoE, CoTm, CoV, CoI) crossing a package boundary — these are always HIGH or CRITICAL severity.

**Step 5 — Anti-Pattern Scan**
Check for patterns in `references/anti-patterns.md`: entity trap, distributed monolith, god module, leaky abstractions, speculative generality.

#### Decompose Mode

Evaluate a specific split or merge decision. Load `references/decomposition.md` for the full framework.

**Step 1 — Map the Boundary**
Identify what is being split or merged. Map all coupling points crossing the proposed boundary.

**Step 2 — Score Drivers**
Score all 6 disintegration drivers and 4 integration drivers from Ford/Richards. For each driver, provide evidence and a score: Strong / Moderate / Weak / N/A.

**Step 3 — Connascence at Boundary**
Classify the connascence type of each cross-boundary coupling point. Compute severity scores.

**Step 4 — Consumer Analysis** _(if applicable)_
If the split targets a library/SDK, define 3-5 consumer profiles and calculate forced dependency waste per profile.

**Step 5 — Evaluation Matrix**
Apply the 4-criteria check: (a) zero external deps, (b) independent consumer use case, (c) acyclic DAG post-split, (d) low breaking-change cost. All of a+b+c must pass to recommend splitting.

**Step 6 — Anti-Pattern Check**
Verify the split won't create an entity trap or distributed monolith. Check if the split is premature (domain not yet understood).

**Step 7 — Recommendation**
Produce one of: **Split** / **Merge** / **Keep** / **Defer** with confidence level (High/Medium/Low) and specific conditions for revisiting deferred decisions (decomposition triggers).

#### Advise Mode

Answer architectural questions grounded in established frameworks. For every recommendation:
1. Name the framework or principle driving it (e.g. "Per SDP (Martin)..." or "Ford/Richards' disintegration driver #3...")
2. Explain the trade-off (what you gain, what you lose)
3. Cite counter-arguments or when the principle should bend

Load reference files relevant to the specific question. If the question spans multiple concerns, load multiple references.

#### Fitness Mode

Propose fitness functions for architectural governance. Load `references/fitness-functions.md`.

**Step 1 — Analyze Current Architecture**
Identify which architectural properties are currently protected (existing tests, CI checks, lint rules) and which are unprotected.

**Step 2 — Map ADRs**
If ADRs exist, check which ones have corresponding automated enforcement. An ADR without a fitness function is a governance gap.

**Step 3 — Propose Functions**
Organize proposals by the 4-level governance stack:
- **Level 1** (every commit, <30s): fast deterministic checks
- **Level 2** (every PR, 1-5 min): structural analysis
- **Level 3** (nightly/weekly): integration and trend checks
- **Level 4** (continual, production): runtime monitoring

For each proposal provide: name, what it checks, threshold, implementation approach (language-specific tooling), which ADR it enforces (if any), and severity if violated.

**Step 4 — Prioritize**
Rank proposals by: (1) blast radius if violated, (2) likelihood of accidental violation, (3) implementation effort. Recommend starting with 3 fitness functions and growing.

**Gate**: Analysis complete with evidence-based findings

### Phase 3: Adversarial Challenge

Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Generic Findings-Challenger Template`) with:
- **Role**: `Adversarial Challenger reviewing architecture review findings`
- **Shared calibration**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`
- **Skill calibration**: `references/architecture-review-calibration.md`
- **Context block**: `The codebase under review is a {project description and scale}. Primary language: {language}. Review mode: {mode}. Scope: {scope}. Project stage: {from discovery}.`
- **Questions**:
  1. `Is this finding based on computed metrics and specific evidence, or opinion?`
  2. `Is the severity proportional — could this package legitimately sit in this zone given its architectural role (e.g. infrastructure, runtime bindings)?`
  3. `Does the finding account for the project's scale and maturity stage?`
  4. `Would acting on this recommendation actually improve architectural health, or is it theoretical improvement?`
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `{all findings}`

Apply verdicts before writing the final report.

**Gate**: Findings challenged and filtered

### Phase 4: Report

Format findings per `references/review-output.md`.

**Review mode** report must include:
1. Executive Summary (3-5 sentences)
2. Metrics Dashboard (per-package table)
3. Findings sorted by severity
4. Dependency graph description (condensed DAG)
5. Proposed fitness functions

**Decompose mode** report must include:
1. Executive Summary
2. Boundary map with coupling points
3. Driver scores (disintegration + integration)
4. Connascence analysis at boundary
5. Consumer waste analysis (if applicable)
6. Recommendation with confidence level and decomposition triggers

**Advise mode**: Structured answer with framework attribution, trade-offs, and counter-arguments.

**Fitness mode** report must include:
1. Current governance coverage assessment
2. ADR gap analysis
3. Proposed fitness functions by governance level
4. Prioritized implementation roadmap

**Report output conventions**: Follow `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md` with:
- **Report suffix**: `architecture-review`
- **Scope placeholder**: `scope-or-package`
- **Spec-directory rule**: the scope corresponds to a feature with an associated spec directory from the Project Document Index
- **Target-directory rule**: the review scope is a specific package or directory, so the report belongs next to the primary review target

### Publish to GitHub
If PUBLISH_ISSUE is `true`:
1. Follow the optional GitHub publishing flow in `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
   Title template: `[Architecture Review] {scope}: {mode} Report`
2. Print the issue URL

If PUBLISH_PR is set:
1. Follow the optional GitHub publishing flow in `${CLAUDE_PLUGIN_ROOT}/references/report-output-conventions.md`
   Publish target: typed PR comment. If the posting command does not return a direct comment URL, resolve it via follow-up GitHub lookup before completing
2. Print the direct comment URL

## MULTI-STEP SESSIONS

This skill supports chaining multiple analyses in a single session. After completing any mode, offer follow-up actions and loop back to Phase 1 with the user's next choice. Carry forward context from prior steps — metrics computed in **review** mode should inform a subsequent **decompose** analysis without recomputation.

Typical chains:
- **review** -> **decompose** (a specific finding) -> **fitness** (governance for the resolution)
- **review** -> **advise** (dig into a specific concern) -> **fitness**
- **fitness** -> **review** (assess current state before proposing governance)

## FOLLOW-UP ACTIONS

After each analysis, present findings and offer:
1. **Continue with another mode** — e.g. after **review**, offer to decompose a flagged package or propose fitness functions. Carry forward the current session context.
2. **Deep-dive into a specific finding** — zoom into a single package or boundary for more detailed analysis
3. **Create fitness function implementations** from proposals
4. **Generate an ADR** for key architectural decisions (invoke the `andthen:trade-off` skill)
5. **Code-level review** for correctness, style, security (invoke the `andthen:review-code` skill)
6. **End session** — finalize the report and stop

When the user selects a follow-up that maps to another mode, loop back to Phase 1 with the new mode and narrowed scope. Do not re-read project rules or re-detect language — reuse context from the current session.
