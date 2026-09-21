"""Command line for the exporter."""

import argparse
import sys

from .pipeline import run


def build_parser():
    parser = argparse.ArgumentParser(
        prog="reporter", description="Export a ledger as a CSV report.")
    parser.add_argument("source", help="ledger file to read")
    parser.add_argument("--out", default="out", help="directory the report is written to")
    parser.add_argument("--name", default="report.csv", help="file name of the report")
    return parser


def main(argv=None):
    """Run the exporter, returning the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        report = run(args.source, args.out, args.name)
    except FileNotFoundError:
        sys.stderr.write("no such ledger: %s\n" % args.source)
        return 2
    sys.stdout.write("%s\n" % report)
    return 0

# WIP: user's unfinished change - do not lose
