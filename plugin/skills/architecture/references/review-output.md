# Architecture Review Output Format & Severity

The finding and report contract for `review`; `decompose` and `fitness` use its Finding Structure under their own Report Contents.

## Finding Structure

Findings use the Structured Finding Contract in `review-calibration.md`, each headed `### ARCH-{NNN}: {Title}`, read for architecture: `severity` also takes `INFO` (a metric marginally outside its range); `location` names the package or module and its C4 level (Context | Container | Component | Code); `evidence` is quantified – package names, metric values, file paths, import chains ("Ce=12", never "high coupling") – with detection labelled separately from interpretation; `suggested_fix` cites the principle driving it ("Per SAP (Martin) …", never "add interfaces"). Three fields are added:

- `dimension`: modularity | coupling | cohesion | testability | deployability | security | governance
- `connascence` (when applicable): {type} – Strength: {N}, Degree: {N}, Locality: {N} -> Severity: {score}
- `fitness_function`: the automated check that prevents recurrence, with its governance level – 1 every commit, 2 every PR, 3 nightly, 4 continual in production. A qualitative finding with no automatable check takes a **manual review checkpoint** instead, phrased as the exact question to answer on re-review.

`Class:` and `Routing:` do not apply – these modes analyse and never remediate. Severity follows the calibration's contrastive pairs; the fitness function enforcing a finding breaks the build for CRITICAL, fails the pipeline for HIGH, warns for MEDIUM, and logs LOW and INFO.

## Report Structure

1. **Executive Summary** – overall health in one sentence, counts by severity, the most critical issue, the most impactful recommendation.
2. **How to Read This Report** – a compact legend for an informed non-specialist, expanding only the shorthand this report actually uses: package and graph metrics, C4 levels, package principles, zone labels, connascence forms; every abbreviation is defined here or on first use.
3. **Metrics Dashboard** – per-package table `Package | Ca | Ce | I | A | D | Zone | Notes`, plus CCD / ACD / NCCD when the tooling produced them.
4. **Findings** – the structure above, sorted by severity (CRITICAL first), then by dimension.
5. **Dependency Graph** – the condensed DAG (SCCs collapsed) in text: edge direction, which packages are leaves (I ≈ 1), which are foundations (I ≈ 0), and any cycles, each also a finding.
6. **Decomposition Recommendations** – only when findings drive one; each names the findings behind it.
7. **Proposed Fitness Functions** – the primary actionable output. Per function: name, what it checks, threshold, governance level, language-specific implementation, and the findings it addresses. On an existing codebase carrying many violations, propose a **frozen-rules** baseline – snapshot the count, fail only on new violations, ratchet down, then switch to zero tolerance – rather than a zero-tolerance rule nobody can adopt.
