"""Reads ledger rows from a delimited input file."""

from pathlib import Path

from .export import DELIMITER

FIELDS = ("id", "label", "amount")


def parse_row(line):
    """Split one input line into a record, with `amount` as an integer."""
    cells = [cell.strip() for cell in line.split(DELIMITER)]
    if len(cells) != len(FIELDS):
        raise ValueError("expected %d fields, got %d" % (len(FIELDS), len(cells)))
    record = dict(zip(FIELDS, cells))
    record["amount"] = int(record["amount"])
    return record


def load_records(path):
    """Read every non-empty line of `path` as a record."""
    text = Path(path).read_text(encoding="utf-8")
    return [parse_row(line) for line in text.splitlines() if line.strip()]
