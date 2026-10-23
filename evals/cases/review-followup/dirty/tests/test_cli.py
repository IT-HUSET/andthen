import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from src.reporter.cli import main


class MainTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.out = self.root / "out"

    def run_main(self, ledger_text):
        source = self.root / "ledger.csv"
        source.write_text(ledger_text, encoding="utf-8")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main([str(source), "--out", str(self.out)])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_a_good_ledger_exits_zero_and_prints_the_report_path(self):
        code, stdout, _ = self.run_main("1,north,40\n")
        self.assertEqual(0, code)
        self.assertEqual("%s\n" % (self.out / "report.csv"), stdout)

    def test_a_missing_ledger_exits_two(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main([str(self.root / "absent.csv"), "--out", str(self.out)])
        self.assertEqual(2, code)
        self.assertIn("no such ledger", stderr.getvalue())

    def test_a_malformed_amount_exits_two_with_a_message_and_no_traceback(self):
        code, stdout, stderr = self.run_main("1,north,fourty\n")
        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("bad ledger", stderr)
        self.assertNotIn("Traceback", stderr)
