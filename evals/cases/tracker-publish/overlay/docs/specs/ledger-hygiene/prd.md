# Product Requirements Document: Ledger Hygiene

> **Source**: tracker issue #1 – the ledger owner's month-close request, 2026-05-06
> **Context**: `docs/PRODUCT.md` § Value Propositions, "A report in one command"
> **Related Assets**: ADR-001 (module layering)


## Executive Summary

- **Problem**: A ledger the owner annotates by hand stops the run, and the run label is too long for the summary sheet the analyst pastes it into.
- **Vision**: An annotated ledger runs as it is, and every run label fits the sheet.
- **Target Users**: the ledger owner; the analyst.
- **Success Metrics**: runs stopped by an annotation – none; labels trimmed by hand – none.

### Capabilities at a Glance
- **FR1: Comment lines in the ledger** _(Must / P0)_ – a line starting with `#` is skipped, never read as a record.
- **FR2: Short run labels** _(Must / P0)_ – a run label is at most 24 characters, cut at a word boundary.

### Scope Highlights
- **In scope**: comment lines in the ledger reader; a length limit in label normalization.
- **Out of scope**: a comment after a record on the same line, a configurable limit, new command-line options.


## Problem Definition

### Problem Statement
The ledger owner writes notes into the ledger at month close, a correction or a month heading, and every such line stops the run with a parse error, so the owner deletes the notes before each run and loses them. The analyst pastes the run label into a summary sheet whose label column holds 24 characters; a label derived from a long ledger name overflows it and is trimmed by hand, often mid-word.

### Desired Outcome
The owner runs the export over the annotated ledger and gets the same report as over the ledger without notes; the analyst pastes every run label as it is.


## Functional Requirements

#### FR1: Comment lines in the ledger
**Description**: The ledger reader skips a line whose first character is `#`.

**Acceptance Criteria**:
- [ ] A ledger with comment lines yields the same records as the same ledger without them.
- [ ] A `#` anywhere but the first character of a line is part of the record as before.

#### FR2: Short run labels
**Description**: Label normalization limits a run label to 24 characters.

**Acceptance Criteria**:
- [ ] A label of 24 characters or fewer is unchanged.
- [ ] A longer label is cut at the last word boundary within 24 characters.
