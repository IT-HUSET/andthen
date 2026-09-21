import tempfile
import unittest
from pathlib import Path

from src.reporter.pipeline import build_label, build_seed, run


class PipelineTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "March Ledger.csv"
        self.source.write_text("1,north,40\n2,south,2\n", encoding="utf-8")
        self.out = self.root / "out"

    def test_seed_is_the_ledger_name(self):
        self.assertEqual("March Ledger", build_seed(self.out, self.source))
        self.assertEqual("March Ledger",
                         (self.out / "seed.txt").read_text(encoding="utf-8"))

    def test_label_normalizes_the_seed(self):
        build_seed(self.out, self.source)
        self.assertEqual("march ledger", build_label(self.out))
        self.assertEqual("march ledger",
                         (self.out / "label.txt").read_text(encoding="utf-8"))

    def test_run_writes_the_report_beside_the_run_files(self):
        report = run(self.source, self.out, "report.csv")
        self.assertEqual(["id,label,amount", "1,north,40", "2,south,2"],
                         report.read_text(encoding="utf-8").splitlines())
        self.assertTrue((self.out / "label.txt").exists())

    def test_run_records_the_exported_row_count(self):
        run(self.source, self.out, "report.csv")
        self.assertEqual("2", (self.out / "rows.txt").read_text(encoding="utf-8"))
