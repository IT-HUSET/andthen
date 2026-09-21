# Closure

The readiness contract an authoring skill runs before its artifact is handed to an unattended executor: every decision a person owns is settled or explicitly deferred, because an unattended run must not fork on an undecided choice. The calling skill names the altitude each settled decision is re-canonicalized into and how status is written; the three steps and the verdict grammar are here.

1. **Settle** – interview the user per blocking Note in one sitting the run waits on; settle it, or defer it explicitly. A deferral is written under `## Implementation Observations` in every FIS it holds, naming the decision and what would settle it, because `plan.json` carries only the blocked status. An ask that returned without an answer – a fire-and-forget question tool, a question posed earlier while authoring went on – is neither settled nor deferred: put it again here, synchronously.

   Sharpen before asking – investigate until the fork is precise, since an investigated fork often closes itself. What survives routes by altitude, after reading the `Decisions` document (see **Project Document Index**) and its Still Current notes, so a fork already settled there closes by citation instead of re-opening:

   - Requirements gap – the `andthen:clarify` skill.
   - Architecture fork – the `andthen:architecture` skill with `--mode trade-off`.
   - Empirical unknown – the `andthen:spike` skill.
   - `Scope trades:` Note from the self-review – the user, in the same sitting: accepted, it is a requirements decision routed like one; declined, nothing is written.

   Recommend, don't decide. Check each answer against earlier ones sharing a surface, since two sound answers can contradict.

   `AUTO_MODE` neither interviews nor invents – unsettled blocking Notes stay open and drive the verdict; scope-trade Notes are only reported.

2. **Re-canonicalize** – integrate each settled decision **once**, into the prose that owns it. No patch transcript, no decision-history section: the body is what the executor implements, and a second copy is what drifts from it. A decision that changes a scenario, a task, a `Proof` or `Verify` target, or a `SATISFIES` surface re-enters the caller's fresh-context self-review over that FIS alone – the independent gate ran on the pre-decision text, and READY would otherwise certify a version no reader saw.
3. **Size gate** – re-run the `OVERSIZE:` check on every FIS a settled decision touched, since closure only ever grew it. Compression is authoring's; here the check only measures.

Emit the verdict in both modes as one bare, unformatted line at line start of the reply, never a menu and never written into the artifact – `plan-schema.md` § FIS identity keeps status in `plan.json` alone. `Closure: READY` – zero open or deferred blocking decisions. `Closure: BLOCKED` – an open or deferred decision, an `OVERSIZE:` hold, a non-runnable `Verify`, or an unbound acceptance clause. The verdict is the artifact's own hold, never a wider reading: a scope item the source defers or a launch waiting on an external event holds nothing.
