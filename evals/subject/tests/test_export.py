import tempfile
import unittest
from pathlib import Path

from src.reporter.export import export_csv, write_report


class ExportCsvTests(unittest.TestCase):
    def test_writes_a_header(self):
        self.assertEqual("id,label,amount", export_csv([])[0])

    def test_exports_rows_in_order(self):
        rows = [{"id": "2", "label": "zeta", "amount": 5},
                {"id": "1", "label": "alpha", "amount": 3}]
        self.assertEqual(["id,label,amount", "2,zeta,5", "1,alpha,3"], export_csv(rows))


class WriteReportTests(unittest.TestCase):
    def test_writes_the_lines_under_the_root(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_report(root, "report.csv", ["id,label,amount"])
            self.assertEqual(Path(root) / "report.csv", path)
            self.assertEqual("id,label,amount\n", path.read_text(encoding="utf-8"))
