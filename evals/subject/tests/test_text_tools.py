import unittest

from src.reporter.text_tools import normalize_label


class NormalizeLabelTests(unittest.TestCase):
    def test_collapses_whitespace_and_lowercases(self):
        self.assertEqual("north region", normalize_label("  North   Region "))

    def test_rejects_non_strings(self):
        with self.assertRaises(TypeError):
            normalize_label(7)

