# Amount filter

Two requests from the month-close retrospective, one for the report and one for the run label.

## FR1: Amount threshold

Records below a threshold should not reach the report. The report's amounts must still add up to the ledger's total, because the ledger owner reconciles the two before closing the month. Add a pure filter over parsed records and the command-line argument that supplies the threshold.

## FR2: Plain run labels

The analyst pastes the run label into a summary sheet that rejects punctuation. A normalized label keeps only letters, digits, and single spaces: every other character becomes a space before whitespace collapses, so `normalize_label("North-East (Q3)")` is `"north east q3"`. Label normalization lives in `src/reporter/text_tools.py`.

## Constraints

Each capability ships on its own; neither waits on the other. Keep the public surface of the existing modules and the standard-library-only rule. Every story must carry executable verification.
