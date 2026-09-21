import unittest

from src.reporter.retry import MAX_RETRIES, PAUSE_SECONDS, retry


class RetryTests(unittest.TestCase):
    def test_retries_a_transient_failure_until_it_succeeds(self):
        calls = []
        pauses = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionError("transient")
            return "ok"

        self.assertEqual("ok", retry(flaky, sleep=pauses.append))
        self.assertEqual(3, len(calls))
        self.assertEqual([PAUSE_SECONDS, PAUSE_SECONDS], pauses)

    def test_gives_up_after_the_maximum(self):
        calls = []

        def broken():
            calls.append(1)
            raise ConnectionError("always")

        with self.assertRaises(ConnectionError):
            retry(broken, sleep=lambda _: None)
        self.assertEqual(MAX_RETRIES + 1, len(calls))
