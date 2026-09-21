# Architecture – Review Mode

Full architecture health assessment, graded against the calibration.

1. **Discover structure** – the package or module graph; in a monorepo or workspace, every package and its declared dependencies.
2. **Compute the dependency graph and metrics** with the language's tooling (SKILL Phase 1): per-package Ca, Ce, I, A, D, and CCD / ACD / NCCD where the tooling supports them.
3. **Structural checks** – assert the calibration's principles (ADP, SDP, SAP) and zones over the graph, and flag God Modules by efferent coupling or LOC outsized against siblings.
4. **Connascence** – for the highest-coupling boundaries (top 3–5 by Ce or most frequently crossed), classify the connascence at each and score it with the calibration's formula.
5. **Anti-pattern scan** – entity trap, distributed monolith, god module, leaky abstraction, speculative generality, premature decomposition, convenience coupling, shallow module, pass-through method or layer, temporal decomposition; each has a misfire boundary in the calibration's traps, checked before the finding is recorded.
6. **API obviousness** _(opt-in, Component / Code level)_ – Ousterhout's lens as the calibration scopes it, only when the scope targets in-process module or public-API design; step 5 already covers its package-level anti-patterns.

## Report Contents

`review-output.md`'s Report Structure, all seven sections in its order; Decomposition Recommendations appears only when findings drive one.
