import unittest

from src.reporter.text_tools import normalize_label, truncate_label


class NormalizeLabelTests(unittest.TestCase):
    def test_collapses_whitespace_and_lowercases(self):
        self.assertEqual("north region", normalize_label("  North   Region "))

    def test_rejects_non_strings(self):
        with self.assertRaises(TypeError):
            normalize_label(7)


class TruncateLabelTests(unittest.TestCase):
    def test_keeps_a_label_that_fits(self):
        self.assertEqual("north", truncate_label("north", 5))

    def test_cuts_a_longer_label_to_the_limit_with_an_ellipsis(self):
        self.assertEqual("north...", truncate_label("north region", 8))

    def test_a_limit_equal_to_the_ellipsis_leaves_only_the_ellipsis(self):
        self.assertEqual("...", truncate_label("north", 3))

    def test_rejects_a_limit_below_the_ellipsis(self):
        with self.assertRaises(ValueError):
            truncate_label("north", 2)

    def test_rejects_non_strings(self):
        with self.assertRaises(TypeError):
            truncate_label(7, 5)
