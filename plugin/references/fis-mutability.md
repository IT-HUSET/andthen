# FIS Mutability Contract

Who may change a FIS, when, and through which channel – the contract every skill that reads, executes, or amends a FIS shares.

Until execution begins (the story leaves `pending`), the owning `andthen:plan` skill and explicit mechanical review remediation may rewrite FIS prose.

During execution, everything above the FIS's two tail sections, `## Discovered Requirements` then `## Implementation Observations`, is read-only except through a design-change amendment. The agent appends to the tail sections with its own editor. A tail section the FIS lacks is created on first append, Discovered Requirements above an existing Implementation Observations.

Task progress lives in the story record of the FIS's plan, never in the FIS. An optional section that is absent or empty means standard handling.

## Discovered Requirements

Discovered Requirements is the one channel for a requirement found during execution. Append it before writing the test or code that depends on it, as one bullet carrying:

- **Title** and **Description**;
- **Rationale** – why the original spec missed it;
- **Interpretation** – unattended runs only: the conservative reading chosen and why;
- **Traced from** – the task ID;
- **Date**.

## Design-change amendment

A design-change amendment carries a real pivot from FIS Intent or scenario text. It requires an ADR, or an explicit ADR-creation action, plus re-attestation.

A scenario-only amendment changes title and Given/When/Then only. Its tags and its Proof path, selector, and state stay unchanged.

## Drift Notes

Drift Notes record deliberate code↔FIS divergence. A run that pivots, or that leaves a named upstream doc contradicted, appends a `#### DRIFT` subsection to `## Implementation Observations`, one line per item:

`- <class>: <what diverged> | Stale targets: <upstream docs> | –`

`<class>` is one of `code-defect | spec-stale | design-changed | ambiguous-intent`.

Review reads the section before flagging, so recorded drift routes to Note instead of being re-found as a fresh blocker every pass. Only `code-defect` still feeds a verdict.

Drift Notes cover the code↔FIS boundary only. FIS↔PRD and above stay human-owned, so a Drift Note recommends the upstream edit and never applies it.
