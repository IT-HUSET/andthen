"""Check a report against the representative ledger with empty lines."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.reporter.pipeline import run

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    report = run(Path("examples/blank-ledger.csv"), root, "report.csv")
    count = (root / "rows.txt").read_text(encoding="utf-8").strip()
    if count != "2":
        sys.stderr.write("expected 2 exported records, got %s\n" % count)
        sys.exit(1)
    rows = report.read_text(encoding="utf-8").splitlines()
    if rows != ["id,label,amount", "1,north,40", "2,south,2"]:
        sys.stderr.write("the report no longer holds the two ledger records\n")
        sys.exit(1)
print("OK: 2 exported records; blank lines excluded")
