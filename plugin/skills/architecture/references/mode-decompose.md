# Architecture – Decompose Mode

There is no correct granularity – the recommendation is the least worst combination of trade-offs, argued from evidence.

## Workflow

### Step 1 – Map the Boundary

Identify what is being split or merged. Map all coupling points crossing the proposed boundary.

### Step 2 – Score Drivers

Score Ford/Richards' six disintegration drivers and four integration drivers. Each gets **Strong / Moderate / Weak / N/A** with evidence, never an unsupported score.

Qualifiers that decide whether a driver counts:
- Service scope and function is **never sufficient alone** – it needs a second driver.
- Code volatility is scored from commit history per subdirectory, not from impressions.
- Scalability is scored from measured load; a subsystem needing ~10x the resources of its neighbours is the signal.
- Fault tolerance may be satisfied by container-level isolation without any logical split.
- Extensibility counts only with *actual* extension consumers, not hypothetical ones.
- Shared code scores as an integration driver only when it is genuinely reusable infrastructure rather than a missing service.

### Step 3 – Connascence at Boundary

Classify the connascence type of each cross-boundary coupling point and compute severity scores.

### Step 4 – Consumer Analysis _(libraries and SDKs)_

Define 3-5 concrete consumer profiles – real use cases with code – and trace each profile's dependency tree to compute **forced LOC waste** (imported but unused) and the true shared kernel across profiles. Report per profile as `Profile | Use case | LOC needed | LOC forced | Waste %`, graded on the calibration's consumer-waste thresholds – past the split threshold the median consumer carries more dead weight than useful code.

### Step 5 – Evaluation Matrix

Apply the 4-criteria check:

- (a) zero external deps – can the package stay pure language;
- (b) independent consumer use – would an external developer import it alone, with a concrete example;
- (c) acyclic dependency graph post-split;
- (d) low breaking-change cost – mechanical migration under ~5 files.

A **package or library extraction** needs all of a+b+c: a split that fails any of them recreates the coupling it claims to remove. A **service split** is gated by Step 2's driver scores plus (c): a cycle across a service boundary is a distributed monolith in disguise.

(d) is not gating. It is a strength signal that raises confidence, while a high breaking-change cost downgrades confidence or pushes toward **Defer**, never toward **Keep**.

### Step 6 – Recommendation

Produce one of **Split** / **Merge** / **Keep** / **Defer** with a confidence level (High/Medium/Low).

- **Split signals** – the module description needs "and"; subsets with different change frequencies; consumers using disjoint subsets; consumer waste or barrel size past the calibration's thresholds; instability says stable while the contents are volatile.
- **Merge signals** – two packages that always change together; packages in a cycle; one reachable only transitively through the other; very high Ca on a tiny package (over-extracted).

Once a split is decided, name the migration path: component-based decomposition where a modular structure already exists (verify quantum independence and SDP-correct direction in the new graph), tactical forking for a big ball of mud (each service starts as a full copy and deletes what it does not use), and Strangler Fig or Branch by Abstraction over big-bang extraction whenever the old path must keep serving traffic.

A **Defer** verdict is only complete with its decomposition triggers – the conditions that reopen it: a third consumer with different needs, an external contributor maintaining a subsystem, a barrel or a profile's consumer waste past the calibration's split threshold, a subsystem reused outside the original project, or a pre-1.0 review.

## Output

Decompose-mode report opens with an Executive Summary and How to Read This Report (compact legend for decomposition drivers, connascence terms, and any abbreviations used), then carries the Step 1–6 artifacts in order.
