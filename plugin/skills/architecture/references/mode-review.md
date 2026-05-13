# Architecture – Review Mode

Full architecture health assessment using quantitative metrics, connascence taxonomy, and established package principles.

**Supporting references** (load as needed): `connascence.md`, `package-principles.md`, `anti-patterns.md`, `ousterhout-modules.md` (for Component/Code-level module and API review), `review-output.md`.

## Step 1 – Discover Structure

Map the package/module structure. For monorepos or workspaces, identify all packages and their declared dependencies.

## Step 2 – Compute Dependency Graph & Metrics

Use language-appropriate tools to extract:
- **Dependency graph** (directed edges between packages/modules)
- **Per-package metrics**: Ca (afferent), Ce (efferent), I (instability), A (abstractness), D (distance from main sequence)
- **Graph-level metrics**: CCD, ACD, NCCD (if tooling supports)

Refer to `package-principles.md` for metric definitions and thresholds.

## Step 3 – Structural Checks

Check each principle systematically:
1. **ADP** – Are there cycles? (Always a finding if yes)
2. **SDP** – For each dependency edge A -> B: is I(A) >= I(B)? Flag violations
3. **SAP** – For packages with I < 0.3: is A > 0.3? Flag stable-but-concrete packages
4. **Zone analysis** – Flag packages with D > 0.3 and classify Zone of Pain vs Zone of Uselessness
5. **God modules** – Flag packages with Ce > 10 or unusually high LOC relative to siblings

## Step 4 – Connascence Analysis

For the highest-coupling boundaries (top 3-5 by Ce or most frequently crossing), classify the connascence type at each boundary. Refer to `connascence.md` for the taxonomy and severity scoring formula.

Flag any dynamic connascence (CoE, CoTm, CoV, CoI) crossing a package boundary – these are always HIGH or CRITICAL severity.

## Step 5 – Anti-Pattern Scan

Check for patterns in `anti-patterns.md`: entity trap, distributed monolith, god module, leaky abstractions, speculative generality, shallow module, pass-through method/layer, temporal decomposition.

## Step 6 – API Obviousness Check _(Component / Code level, opt-in)_

**Run only when** the scope explicitly targets in-process module or public API design (e.g. a single module, a library package, or an API review). **Skip** for full-project reviews, container-level scope, or service-decomposition scope – Ousterhout's lens does not apply there, and Step 5 already covers shallow-module, pass-through, and temporal-decomposition anti-patterns at the package level.

For each public API surface in scope:
- **Obviousness test** – Can a caller use this module correctly without reading its implementation? If no, the interface leaks. Per Ousterhout (APoSD Ch. 18). Tag findings at C4 **Component** or **Code** level. See `ousterhout-modules.md` for the remaining heuristics when they are useful as supplementary evidence.

## Report Contents

Review-mode report must include:
1. Executive Summary (3-5 sentences)
2. How to Read This Report (compact legend for metrics, graph metrics, C4 levels, principles, zones, and connascence terms used in the report)
3. Metrics Dashboard (per-package table)
4. Findings sorted by severity
5. Dependency graph description (condensed DAG)
6. Proposed fitness functions
