"""Renders records as CSV lines and writes a report file."""

from pathlib import Path

DELIMITER = ","
COLUMNS = ("id", "label", "amount")


def export_csv(rows):
    """Return a header line followed by one line per row."""
    lines = [DELIMITER.join(COLUMNS)]
    for row in rows:
        lines.append(DELIMITER.join(str(row[column]) for column in COLUMNS))
    return lines


def write_report(root, name, lines):
    """Write `lines` as the report `name` under `root` and return its path."""
    destination = Path(root) / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination
