# Architecture – Decompose Mode

Evaluate a specific split or merge decision using Ford/Richards driver scoring and connascence analysis.

**Supporting references**: `decomposition.md`, `connascence.md`, `package-principles.md`, `anti-patterns.md`, `ddd.md` (load when the boundary in question is a bounded context, or when the integration relationship between two existing contexts needs a context-mapping pattern choice).

## Step 1 – Map the Boundary

Identify what is being split or merged. Map all coupling points crossing the proposed boundary.

## Step 2 – Score Drivers

Score all 6 disintegration drivers and 4 integration drivers from Ford/Richards. For each driver, provide evidence and a score: Strong / Moderate / Weak / N/A.

## Step 3 – Connascence at Boundary

Classify the connascence type of each cross-boundary coupling point. Compute severity scores.

## Step 4 – Consumer Analysis _(if applicable)_

If the split targets a library/SDK, define 3-5 consumer profiles and calculate forced dependency waste per profile.

## Step 5 – Evaluation Matrix

Apply the 4-criteria check: (a) zero external deps, (b) independent consumer use case, (c) acyclic DAG post-split, (d) low breaking-change cost. All of a+b+c must pass to recommend a split – a split that fails any of these (carries external deps, has no independent consumer, or reintroduces a cycle) recreates the coupling it claims to remove, so it is a distributed monolith in disguise rather than a clean boundary. (d) low breaking-change cost is not gating: it is a strength signal that raises confidence, while a high breaking-change cost downgrades confidence or pushes toward **Defer**, never toward **Keep**.

## Step 6 – Anti-Pattern Check

Verify the split won't create an entity trap or distributed monolith. Check if the split is premature (domain not yet understood).

## Step 7 – Recommendation

Produce one of: **Split** / **Merge** / **Keep** / **Defer** with confidence level (High/Medium/Low) and specific conditions for revisiting deferred decisions (decomposition triggers).

## Report Contents

Decompose-mode report must include:
1. Executive Summary
2. How to Read This Report (compact legend for decomposition drivers, connascence terms, and any abbreviations used)
3. Boundary map with coupling points
4. Driver scores (disintegration + integration)
5. Connascence analysis at boundary
6. Consumer waste analysis (if applicable)
7. Recommendation with confidence level and decomposition triggers
