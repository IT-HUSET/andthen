# FIS Mutability Contract

Who may change a FIS, when, and through which channel – the contract every skill that reads, executes, or amends a FIS shares.

Until execution begins (the story leaves `spec-ready`), the owning `andthen:spec` / `andthen:plan` skill and explicit mechanical review remediation may rewrite FIS prose. During execution, everything above the FIS's two tail sections – `## Discovered Requirements`, then `## Implementation Observations`, each created on first append where the FIS carries no such heading, Discovered Requirements above an existing Implementation Observations – is read-only except through a design-change amendment; the agent appends to those two with its own editor. Task progress lives in the story record of the FIS's plan, never in the FIS. An optional section that is absent or empty means standard handling.

Discovered Requirements is the one channel for a requirement found during execution. Append it before writing the test or code that depends on it, as one bullet carrying **Title**, **Description**, **Rationale** (why the original spec missed it), **Interpretation** (`AUTO_MODE` only: the conservative reading chosen and why), **Traced from** (task ID), and **Date**.

Design-change amendment is for legitimate pivots from FIS Intent or scenario text, and requires an ADR or explicit ADR-creation action plus re-attestation. A scenario-only amendment changes title/Given/When/Then only; tags and Proof path/selector/state stay unchanged.

Drift Notes record deliberate code↔FIS divergence. A run that pivots, or that leaves a named upstream doc contradicted, appends a `#### DRIFT` subsection to `## Implementation Observations`: one line per item, `- <class>: <what diverged> | Stale targets: <upstream docs> | –`, with `<class>` from `code-defect | spec-stale | design-changed | ambiguous-intent`. Review reads the section before flagging, so recorded drift routes to Note instead of being re-found as a fresh blocker every pass; only `code-defect` still feeds a verdict. Scope is the code↔FIS boundary only – FIS↔PRD and above stay human-owned, so a Drift Note recommends the upstream edit and never applies it.
