"""Retries a callable whose failure is transient."""

import time

PAUSE_SECONDS = 1.0
MAX_RETRIES = 5


def retry(fn, sleep=time.sleep):
    """Call `fn`, retrying after a fixed pause until the maximum is reached."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            return fn()
        except OSError:
            if attempt == MAX_RETRIES:
                raise
            sleep(PAUSE_SECONDS)
