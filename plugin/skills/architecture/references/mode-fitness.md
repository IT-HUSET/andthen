# Architecture – Fitness Mode

Propose fitness functions for architectural governance and ADR enforcement.

**Supporting references**: `fitness-functions.md`, `package-principles.md`, `quanta.md`.

## Step 1 – Analyze Current Architecture

Identify which architectural properties are currently protected (existing tests, CI checks, lint rules) and which are unprotected.

## Step 2 – Map ADRs

If ADRs exist, check which ones have corresponding automated enforcement. An ADR without a fitness function is a governance gap.

## Step 3 – Propose Functions

Organize proposals by the 4-level governance stack:
- **Level 1** (every commit, <30s): fast deterministic checks
- **Level 2** (every PR, 1-5 min): structural analysis
- **Level 3** (nightly/weekly): integration and trend checks
- **Level 4** (continual, production): runtime monitoring

For each proposal provide: name, what it checks, threshold, implementation approach (language-specific tooling), which ADR it enforces (if any), and severity if violated.

## Step 4 – Prioritize

Rank proposals by: (1) blast radius if violated, (2) likelihood of accidental violation, (3) implementation effort. Recommend starting with 3 fitness functions and growing.

## Report Contents

Fitness-mode report must include:
1. Current governance coverage assessment
2. How to Read This Report (compact legend for ADR, governance levels, and any architecture shorthand used)
3. ADR gap analysis
4. Proposed fitness functions by governance level
5. Prioritized implementation roadmap
