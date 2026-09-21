import tempfile
import unittest
from pathlib import Path

from src.reporter.records import load_records, parse_row


class ParseRowTests(unittest.TestCase):
    def test_reads_the_amount_as_an_integer(self):
        self.assertEqual({"id": "1", "label": "north", "amount": 40},
                         parse_row("1, north, 40"))

    def test_rejects_a_row_with_the_wrong_field_count(self):
        with self.assertRaises(ValueError):
            parse_row("1, north")


class LoadRecordsTests(unittest.TestCase):
    def test_skips_blank_lines(self):
        with tempfile.TemporaryDirectory() as root:
            ledger = Path(root) / "ledger.csv"
            ledger.write_text("1,north,40\n\n2,south,2\n", encoding="utf-8")
            self.assertEqual(["north", "south"],
                             [record["label"] for record in load_records(ledger)])
