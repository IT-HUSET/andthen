"""Stages a report run: the run seed, its label, then the report file."""

from pathlib import Path

from .export import export_csv, write_report
from .records import load_records
from .retry import retry
from .text_tools import normalize_label

SEED_FILE = "seed.txt"
LABEL_FILE = "label.txt"


def build_seed(root, source):
    """Write the run seed – the ledger's base name – under `root`."""
    seed = Path(source).stem
    path = Path(root) / SEED_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(seed, encoding="utf-8")
    return seed


def build_label(root):
    """Write the run label the seed under `root` implies."""
    seed = (Path(root) / SEED_FILE).read_text(encoding="utf-8")
    label = normalize_label(seed)
    (Path(root) / LABEL_FILE).write_text(label, encoding="utf-8")
    return label


def run(source, root, name):
    """Stage a run for `source` under `root` and write its report."""
    build_seed(root, source)
    build_label(root)
    lines = export_csv(load_records(source))
    return retry(lambda: write_report(root, name, lines))
