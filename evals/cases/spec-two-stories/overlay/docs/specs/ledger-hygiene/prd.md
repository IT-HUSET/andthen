# Product Requirements Document: Ledger Hygiene

> **Source**: inline – two requests from the month-close retrospective, 2026-05-06
> **Context**: `docs/PRODUCT.md` § Value Propositions, "A report in one command"
> **Related Assets**: ADR-001 (module layering)


## Executive Summary

- **Problem**: A ledger the owner annotates by hand stops the run, and the run label is too long for the summary sheet the analyst pastes it into.
- **Vision**: An annotated ledger runs as-is, and every run label fits the sheet.
- **Target Users**: the ledger owner; the analyst.
- **Success Metrics**: runs stopped by an annotation – none; labels trimmed by hand – none.

### Capabilities at a Glance
- **FR1: Comment lines in a ledger** _(Must / P0)_ – a line starting with `#` is skipped, never read as a record.
- **FR2: Short run labels** _(Must / P0)_ – a run label is at most 24 characters, cut at a word boundary.

### Scope Highlights
- **In scope**: comment lines in the ledger reader; a length limit in label normalization.
- **Out of scope**: a comment after a record on the same line, a configurable limit, new command-line options.
- **MVP boundary**: each capability ships on its own; neither waits on the other.


## Problem Definition

### Problem Statement
The ledger owner writes notes into the ledger at month close – a correction, a month heading – and every such line stops the run with a parse error, so the owner deletes the notes before each run and loses them. The analyst pastes the run label into a summary sheet whose label column holds 24 characters; a label derived from a long ledger name overflows it and is trimmed by hand, often mid-word.

### Target Users
- **Ledger owner** – annotates the ledger and runs the export at month close.
- **Analyst** – copies the run label into the fixed-width summary sheet.

### Desired Outcome
The owner runs the export over the annotated ledger and gets the same report as over the ledger without notes; the analyst pastes every run label as it is.


## Success Metrics

| Metric | Baseline | Target | How observed |
|--------|----------|--------|--------------|
| Runs stopped by an annotation line | every annotated month | none | the month-close note |
| Run labels trimmed by hand | about one run in three | none | the summary sheet |


## Functional Requirements

### FR1: Comment lines in a ledger
A ledger line whose first non-blank character is `#` is a comment. Reading a ledger skips it as it skips a blank line: it is never split into fields, and a ledger holding only comments yields no records. Every other line reads exactly as today. Ledger reading lives in `src/reporter/records.py`.

**Acceptance criteria**
- A ledger with comment lines between records yields the same records as the ledger without them.
- A line with `#` after a record's cells is still a record, read as today.

### FR2: Short run labels
A normalized label is at most 24 characters. A longer one is cut at the last space at or before the 24th character, or at the 24th character when it has no space there, and never ends in a space. A label of 24 characters or fewer is unchanged. Label normalization lives in `src/reporter/text_tools.py`.

**Acceptance criteria**
- `normalize_label("North Region Quarterly Ledger")` is `"north region quarterly"`.
- A 30-character label with no space is cut to its first 24 characters.


## Scope

### In Scope
- FR1 in the ledger reader.
- FR2 in label normalization.

### Out of Scope
- A comment after a record's cells on the same line.
- A configurable label limit, or a command-line option for either capability.


## Constraints & Assumptions
- *Constraint:* standard library only (`docs/DECISIONS.md`).
- *Constraint:* the layering in `docs/ARCHITECTURE.md` holds – each leaf module keeps importing nothing else from the package.
- *Constraint:* every change carries executable verification.
