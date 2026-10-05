import unittest

from tally.cli import count_words


class CountWordsTest(unittest.TestCase):
    def test_runs_of_whitespace_separate_words(self):
        self.assertEqual(3, count_words("one two  three\n"))

    def test_a_blank_line_counts_zero(self):
        self.assertEqual(0, count_words("\n"))


if __name__ == "__main__":
    unittest.main()
