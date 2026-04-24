# Ousterhout — Module & Interface Design Lens

From John Ousterhout, _A Philosophy of Software Design_ (2nd ed.). Operates at C4 **Component / Code** level — within-process module, class, and API design. Complements (does not replace) the service-decomposition lens from Ford & Richards, Martin, and Farley.

Use this lens when reviewing or advising on:
- Module/class APIs, library or SDK design, internal package interfaces
- "Should this helper exist?" / "Does this layer earn its keep?" questions
- In-process code organization within a service, before a split is on the table

Not the right lens for: service boundaries, deployment topology, distributed consistency, team-aligned decomposition. Use the primary frameworks for those.

---

## Core Thesis

**Complexity** (Ousterhout): *anything about the structure of a system that makes it hard to understand or modify.* It is felt by the reader, not a property of the code in isolation.

**Three symptoms** to look for in a review:
1. **Change amplification** — a small change requires edits in many places
2. **Cognitive load** — too much must be held in working memory to change something safely
3. **Unknown unknowns** — the developer cannot tell what else is affected (the worst; the other two at least announce themselves)

**Two causes**, both reducible to structure:
1. **Dependencies** — code that cannot be understood or changed in isolation
2. **Obscurity** — important information not obvious from names, types, or docs

---

## Principles (ordered by review usefulness)

### Deep vs. shallow modules (Ch. 4)
A **deep** module exposes a small interface over a powerful implementation (Unix file I/O: a handful of syscalls over a huge amount of hidden logic). A **shallow** module has an interface nearly as complex as its implementation — it adds little abstraction and mostly adds a boundary to cross.

**Depth test**: if the interface is roughly as complex as the implementation, the module is shallow. Decomposing one shallow module into five helper functions with five new signatures typically replaces one shallow thing with five shallow things.

### Information leakage (Ch. 5)
A **design decision is leaked** when the same decision (file format, protocol detail, data layout, algorithm choice) appears in more than one module's interface. Changing that decision then forces coordinated changes in every interface reflecting it. Subtler — and more common — than "importing internal types": even clean-looking APIs can leak by shape.

**Leakage test**: for each non-trivial design decision, can you name exactly one module whose interface reflects it? More than one ⇒ leakage.

### Different layer, different abstraction — pass-through methods (Ch. 7)
Each layer in a stack should provide a different abstraction from the layer below. A **pass-through method** forwards to another method with the same (or near-identical) parameters, adding no abstraction. It is a signal the layer is not earning its existence.

### Pull complexity downward (Ch. 8)
When complexity must live somewhere, prefer the implementation over the interface. Callers must understand the interface; the implementation is hidden behind it.

**Trade-off framing**: "making the caller do this is simpler *for us*" is not a win if it multiplies cognitive load across N callers.

### General-purpose interfaces (Ch. 6)
Shape interfaces *slightly* more general than the immediate use case. An interface shaped precisely to one caller's current needs leaks that caller's logic into the module. This is not license for speculative generality — the target is "somewhat more general than one caller," not "all conceivable callers."

### Define errors out of existence (Ch. 10)
Often the best error handling is to redesign the abstraction so the error is no longer a case. `delete(path)` that throws on a missing file is one design; `delete(path)` meaning *"ensure this does not exist"* is another, and eliminates a whole class of handling code. Minimize the count of places that must deal with exceptions by choosing abstractions that reduce error cases.

**Judgment boundary**: only legitimate when the "absent" case is genuinely valid state, not evidence of a bug. Do not swallow faults.

### Temporal decomposition (Ch. 5, anti-pattern)
Splitting modules by the *order* operations happen ("read, then parse, then process") often distributes the same knowledge across modules. If reading and parsing both require knowledge of the file format, that knowledge belongs in one module.

### Design it twice (Ch. 11)
Sketch at least two fundamentally different interface designs before committing. The first plausible design is rarely the best one. For any new public API, the review expectation is evidence of a genuine alternative considered and rejected with reason.

### Strategic vs. tactical (Ch. 3)
Tactical programming optimizes for "working now"; strategic programming treats ongoing design quality as continuous investment (Ousterhout suggests ~10–15% of time). Compatible with Farley's complexity-management framing (`farley-framework.md`) — use Ousterhout's budget framing as the concrete tactic.

---

## Review heuristics (checklist form)

When auditing a module or public API:

1. **Depth test** — Is the interface significantly simpler than the implementation? If roughly equivalent: shallow ⇒ finding.
2. **Leakage test** — Is any design decision (format, layout, algorithm, protocol) visible in more than one interface? If yes ⇒ finding.
3. **Pass-through test** — Does any method do nothing but forward to another with the same arguments? If yes ⇒ layer not earning itself.
4. **Obviousness test** — Can a caller use this correctly without reading the implementation? If no ⇒ interface leaks.
5. **Temporal-decomposition test** — Was this boundary drawn by execution order, or by knowledge ownership? Sequence-based splits usually fail test 2.
6. **Error-existence test** — For each exception at the interface, could the abstraction be redefined so the case disappears (without hiding faults)?
7. **One-sentence test** — Can you describe the module in one sentence without using "and"? If not, abstraction is unclear.
8. **Designed-twice test** — Was at least one genuinely different alternative interface considered?

**Severity calibration**: defer to `architecture-calibration.md` (contrastive examples, false-positive traps) and `review-calibration.md` (universal anti-leniency rules). Apply the same blast-radius logic used for the existing examples there — HIGH requires measurable impact across multiple consumers; isolated single-module findings default to INFO. Do not invent thresholds specific to Ousterhout findings.

**Report artifact note**: most Ousterhout findings are qualitative (depth, obviousness, one-sentence) with no automated check. For the `Fitness Function` field required by `review-output.md`, **Manual review checkpoint** is acceptable — phrase it as the specific question to answer on re-review (e.g. "Can a caller use `X` correctly without reading its implementation?").

---

## Limits of this lens (apply honestly)

- **Does not address service decomposition**: quanta, bounded contexts, deployment topology, organizational coupling are out of scope.
- **Deep modules can become god objects**: the framework does not give a clear upper bound on depth; cross-check with CCP (`package-principles.md`) and the God Module entry in `anti-patterns.md`.
- **Deep stable-infrastructure packages are legitimate**: database drivers, logging frameworks, runtime bindings naturally have small interfaces over powerful implementations *and* sit in the Zone of Pain. Per `architecture-calibration.md` false-positive trap #1, do not flag these as Ousterhout-style findings unless the package contains business logic or changes frequently.
- **Not empirically grounded**: a practitioner's argument. Use it as a lens, not as a proof.
- **Tension with testability**: narrow interfaces (ISP / mockable) can pull toward shallower modules. Resolve case-by-case; prefer integration tests over mocks when a module is legitimately deep.
- **"Define errors out of existence" can mask bugs** if the absent case is not truly valid state. Require evidence the case is legitimate.

---

## Framework attribution

Cite in findings as *"Per Ousterhout (APoSD Ch. N) …"* to match the existing `Per SAP (Martin) …` / `Per Newman …` style used across findings and calibration examples. Anti-pattern catalog entries (`anti-patterns.md`) use the compact parenthetical form *"(Ousterhout, APoSD Ch. N)"* — both forms are accepted in their respective contexts. Chapter numbers refer to the 2nd edition.
