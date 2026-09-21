import unittest

from src.export import export


class ExportTests(unittest.TestCase):
    def test_roundtrip(self):
        self.assertEqual([1], export([1]))
