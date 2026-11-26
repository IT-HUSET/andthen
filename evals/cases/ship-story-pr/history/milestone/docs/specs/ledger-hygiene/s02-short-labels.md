# Short run labels

**Plan**: docs/specs/ledger-hygiene/plan.json
**Story-ID**: S02

## Feature Overview and Goal

**Intent**: The analyst pastes a run label into a 24-character column and never trims it by hand.

**Expected Outcomes**:
- [OC01] A run label of 24 characters or fewer comes out unchanged.
- [OC02] A longer run label comes out cut at the last word boundary within 24 characters, never mid-word.

## Required Context

- `docs/DECISIONS.md#still-current` – the label stays lowercase with collapsed whitespace.

## Acceptance Scenarios

- **S01 [OC01] A short label is untouched**
  - **Given** a label of 24 characters
  - **When** `normalize_label` runs
  - **Then** the result is the label as normalized before this story
  - **Proof**: `tests.test_text_tools#NormalizeLabelTests.test_keeps_a_short_label` – green

- **S02 [OC02] A long label is cut at a word boundary**
  - **Given** a label of 40 characters made of words
  - **When** `normalize_label` runs
  - **Then** the result is at most 24 characters and ends on a whole word
  - **Proof**: `tests.test_text_tools#NormalizeLabelTests.test_cuts_at_a_word_boundary` – green

## Structural Criteria

- **SC01** The limit is one named constant, not a literal at each use.

## Implementation Plan

### Implementation Tasks

- **TI01 Labels are limited to 24 characters**
  - `normalize_label(text)` in `src/reporter/text_tools.py` cuts at the last space within 24 characters.
  - **Verify**: `tests.test_text_tools#NormalizeLabelTests.test_cuts_at_a_word_boundary` – at most 24 characters, whole words
  - **SATISFIES**: S01, S02, SC01

## What We're NOT Doing

- No configurable limit; the PRD scopes it out.

## Implementation Observations

_No observations recorded yet._
