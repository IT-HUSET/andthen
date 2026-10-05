"""Command-line entry point: one `file:line count` row per line."""

import sys


def count_words(line):
    return len(line.split())


def main(argv=None):
    names = sys.argv[1:] if argv is None else argv
    for name in names:
        with open(name, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                print("%s:%d %d" % (name, number, count_words(line)))
    return 0
