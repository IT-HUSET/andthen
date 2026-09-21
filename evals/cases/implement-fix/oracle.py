#!/usr/bin/env python3
"""Reconciliation for the implement-fix report case, run with cwd = the workspace. The
pass must leave build_label reading seed.txt, both stories still done with the
`verified` record their completion wrote, and the input report annotated once
with a `## Remediation Status` section that states F1 RESOLVED and one
`**Remediated**:` line in its header - the annotation is what the next reader
trusts, so a fix without it, a status that contradicts the code, or a header that
still opens on the FAIL verdict alone is not a remediated report.

Case data, not harness. Python 3 standard library only, 3.9-compatible."""

import importlib
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/run-staging/plan.json")
REPORT = Path("plan-gap-review-claude-2026-09-05.md")
STATUS_HEADING = re.compile(r"^## Remediation Status[ \t]*$", re.M)
REMEDIATED = re.compile(r"^\*\*Remediated\*\*:", re.M)
NOT_RESOLVED = re.compile(r"\b(UNRESOLVED|PARTIALLY RESOLVED|DEFERRED|SURFACED)\b")


def check():
    rows, problems = story_state.stories(PLAN)
    if not rows:
        return problems
    # Remediation repairs code and annotates the report; it never re-completes a
    # story, so every row must still read `done` with the `verified` record its
    # own completion wrote.
    for row in rows:
        problems.extend(story_state.diverges(PLAN, row, verified=True, status="done"))
    text = REPORT.read_text(encoding="utf-8", errors="replace") if REPORT.is_file() else ""
    sections = STATUS_HEADING.split(text)
    if len(sections) != 2:
        problems.append("%s: %d '## Remediation Status' section(s), expected exactly 1"
                        % (REPORT, len(sections) - 1))
    else:
        stated = [ln for ln in sections[1].splitlines() if re.search(r"\bF1\b", ln)]
        if not stated or not any(re.search(r"\bRESOLVED\b", ln) and not NOT_RESOLVED.search(ln)
                                 for ln in stated):
            problems.append("%s: Remediation Status does not state F1 RESOLVED: %r"
                            % (REPORT, stated[:1]))
    # The report opens on its FAIL verdict, so the header is where a reader learns
    # the fixes came after it; a marker below the first section is not in the header.
    marked = len(REMEDIATED.findall(text.split("\n## ", 1)[0]))
    if marked != 1:
        problems.append("%s: %d '**Remediated**:' line(s) in the header, expected exactly 1"
                        % (REPORT, marked))
    sys.path.insert(0, str(Path(".").resolve()))
    pipeline = importlib.import_module("src.reporter.pipeline")
    with tempfile.TemporaryDirectory() as tmp:
        # A seed no run of this process wrote: a build_label that carries the
        # value in memory raises rather than reading the artifact beside it.
        (Path(tmp) / "seed.txt").write_text("North Region", encoding="utf-8")
        try:
            pipeline.build_label(tmp)
            label = (Path(tmp) / "label.txt").read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            label = "%s: %s" % (type(exc).__name__, exc)
        if label != "north region":
            problems.append("build_label wrote %r for the seed 'North Region' in seed.txt"
                            " - it does not read the prerequisite artifact" % label)
    return problems


def main():
    problems = check()
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
