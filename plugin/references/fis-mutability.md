# FIS Mutability Contract

Who may change a FIS, when, and through which channel – the contract every skill that reads, executes, or amends a FIS shares.

During execution, everything above the FIS's two tail sections – `## Discovered Requirements`, then `## Implementation Observations`, each created on first append where the FIS carries no such heading – is read-only. Task progress lives in the story record of the FIS's plan, never in the FIS. An optional section that is absent or empty means standard handling.

Until the final readiness gate, the owning `andthen:spec` / `andthen:plan` skill and explicit mechanical review remediation may rewrite FIS prose – preflight re-canonicalizes each settled decision into that prose. Once implementation begins, those two sections are the only ones an agent edits, appending to them with its editor; a design-change amendment reopens the prose above them under the rule below.

Discovered Requirements is the single sanctioned append-only channel for FIS-augmenting requirement discoveries during execution. Append the requirement before writing the test or code that depends on it, as one bullet carrying **Title**, **Description**, **Rationale** (why the original spec missed it), **Interpretation** (`AUTO_MODE` only: the conservative reading chosen and why), **Traced from** (task ID), and **Date**.

Design-change amendment is for legitimate pivots from FIS Intent or scenario text. It requires an ADR or explicit ADR-creation action, exact old/new text, and re-attestation. A scenario-only amendment changes title/Given/When/Then only; tags and Proof path/selector/state stay byte-identical.

Drift Notes record deliberate code↔FIS divergence, and are why no separate drift document exists – the FIS already travels with the work. A run that pivots, or that leaves a named upstream doc contradicted, appends a `#### DRIFT` subsection to `## Implementation Observations`: one line per item, `- <class>: <what diverged> | Stale targets: <upstream docs> | –`, with `<class>` from `code-defect | spec-stale | design-changed | ambiguous-intent`. Review reads the section before flagging, so recorded drift routes to Note instead of being re-found as a fresh blocker every pass; only `code-defect` still feeds a verdict. Scope is the code↔FIS boundary only – FIS↔PRD and above stay human-owned, so a Drift Note recommends the upstream edit and never applies it.
