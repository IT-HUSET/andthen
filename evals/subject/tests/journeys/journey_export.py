"""End-to-end journey: the command line over a ledger on disk."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from src.reporter.cli import main


class ExportJourneyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_a_ledger_becomes_a_report(self):
        source = self.root / "march.csv"
        source.write_text("1,north,40\n2,south,2\n", encoding="utf-8")
        out = self.root / "out"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main([str(source), "--out", str(out), "--name", "march-report.csv"])

        self.assertEqual(0, code)
        report = out / "march-report.csv"
        self.assertEqual(str(report), stdout.getvalue().strip())
        self.assertEqual("id,label,amount", report.read_text(encoding="utf-8").splitlines()[0])

    def test_a_missing_ledger_exits_two(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            code = main([str(self.root / "absent.csv"), "--out", str(self.root / "out")])

        self.assertEqual(2, code)
        self.assertIn("no such ledger", stderr.getvalue())
