#!/usr/bin/env python3
"""Bind resumed completion to repaired output, final state and a story commit.

Post-run checks observe the retained workspace, not the subject's tool calls.
The frozen final-validation command proves behavior; its invocation during the
subject run is reported separately through the completion rubric.
"""

import io
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import story_state  # noqa: E402

PLAN = Path("docs/specs/row-count/plan.json")
FIS = PLAN.parent / "s01-record-row-count.md"
SOURCE = Path("src/reporter/pipeline.py")
PROOF = Path("tools/check_blank_rows.py")
LEDGER = Path("examples/blank-ledger.csv")
OVERLAY = Path(__file__).resolve().parent / "overlay"
TRAILERS = (re.compile(r"^Story-ID: S01[ \t]*$", re.M),
            re.compile(r"^Plan: docs/specs/row-count/plan\.json[ \t]*$", re.M))


def git(*arguments):
    result = subprocess.run(("git",) + arguments, capture_output=True,
                            text=True, encoding="utf-8")
    return result.stdout if result.returncode == 0 else ""


def commit_proves_completion(sha):
    archive = subprocess.run(("git", "archive", sha, "--", "src", str(PLAN),
                              str(PROOF), str(LEDGER)), capture_output=True)
    if archive.returncode != 0:
        return False
    with tempfile.TemporaryDirectory(prefix="exec-plan-resume-") as directory:
        root = Path(directory).resolve()
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tree:
            for member in tree.getmembers():
                if member.isdir():
                    continue
                target = root / member.name
                try:
                    target.resolve().relative_to(root)
                except ValueError:
                    return False
                if not member.isfile():
                    return False
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tree.extractfile(member).read())
        row, problems = story_state.story(root / PLAN, "S01")
        if row is None or problems or story_state.diverges(
                PLAN, row, verified=True, status="done", completedTaskIds=["TI01"]):
            return False
        for path in (PROOF, LEDGER):
            if not (root / path).is_file() or (root / path).read_bytes() != (OVERLAY / path).read_bytes():
                return False
        proof = subprocess.run([sys.executable, str(PROOF)], cwd=str(root),
                               capture_output=True)
        return proof.returncode == 0


def main():
    row, problems = story_state.story(PLAN, "S01")
    if row is not None:
        problems.extend(story_state.diverges(
            PLAN, row, verified=True, status="done", completedTaskIds=["TI01"]))

    intact = True
    for path in (PROOF, LEDGER):
        if not path.is_file() or path.read_bytes() != (OVERLAY / path).read_bytes():
            problems.append("%s: final-validation input or command was changed" % path)
            intact = False
    if intact:
        proof = subprocess.run([sys.executable, str(PROOF)], capture_output=True,
                               text=True, encoding="utf-8")
        if proof.returncode != 0:
            problems.append(proof.stderr.strip() or proof.stdout.strip()
                            or "final validation failed")

    committed = False
    for sha in git("rev-list", "HEAD").split():
        message = git("show", "-s", "--format=%B", sha)
        if not all(pattern.search(message) for pattern in TRAILERS):
            continue
        changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines())
        if {str(SOURCE), str(PLAN)} <= changed and commit_proves_completion(sha):
            committed = True
            break
    if not committed:
        problems.append("no Story-ID/Plan commit contains both the repair and completed row")
    dirty = git("status", "--porcelain", "--", str(SOURCE), str(PLAN), str(FIS), "tests")
    if dirty.strip():
        problems.append("uncommitted completion: %s" % dirty.strip())

    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
