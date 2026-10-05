# Architecture – Review Mode

Full architecture health assessment, graded against the calibration.

## Workflow

1. **Discover structure** – the package or module graph; in a monorepo or workspace, every package and its declared dependencies.
2. **Compute the dependency graph and metrics** with the language's tooling: per-package Ca, Ce, I, A, D, and LOC, plus mean cyclomatic complexity and CCD / ACD / NCCD where the tooling measures them.
3. **Structural checks** – assert the calibration's principles (ADP, SDP, SAP) and zones over the graph, and flag God Modules on the calibration's composite. When the tooling cannot measure complexity, a God Module candidate is recorded at `confidence` 50 or below with the missing measurement as its `verification_needed`.
4. **Connascence** – for the highest-coupling boundaries (top 3–5 by Ce or most frequently crossed), classify the connascence at each and score it with the calibration's formula.
5. **Anti-pattern scan** – entity trap, distributed monolith, information leakage, speculative generality, premature decomposition, convenience coupling, shallow module, pass-through layer, hidden behaviour, temporal decomposition.
6. **Deep modules** – when the scope targets one module, class, or public API, the calibration's findings and questions for such a scope.

## Output

`review-output.md`'s Report Structure, all seven sections in its order.
