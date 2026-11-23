#!/usr/bin/env python3
"""Builds the branches the ship-story-pr subject starts on, as the case's first step.

    python3 history.py <run dir>

Case data, not harness. Staging commits one baseline, and this case needs three
branches and a remote: `main`, the remote's default branch, holding no copy of the
plan; `feat/ledger-hygiene`, the milestone branch, adding the plan bundle with both
stories pending; and `feat/ledger-hygiene-s01`, cut from it and checked out, adding
S01's story commit. The remote is a bare repository beside the workspace holding
`main` and the milestone branch, so the base rule's remote-branch rung can be read
with no network. Runs as a `type: bash` step before the subject's, because staging
has no hook for history and the case needs none beyond this.

The files of each commit are `history/<step>/`, copied over the tree. The subject
reads them through git, so they keep the silence an overlay keeps.

Two things it leaves in the run directory for the checks:
- `origin-refs.txt`, the remote's refs as built, which the oracle compares the
  remote against, because a push is the one write that leaves the workspace;
- `fixture-head.txt`, rewritten to the story branch's tip, which is the commit
  `stage.stage_diff` diffs from: the starting state is that tip, and diffing from
  the baseline would hand the judge S01's own commits as the subject's work.

Python 3 standard library only, 3.9-compatible.
"""

import shutil
import subprocess
import sys
from pathlib import Path

HISTORY = Path(__file__).resolve().parent / "history"
IDENTITY = ("-c", "user.name=andthen-evals", "-c", "user.email=evals@andthen.invalid",
            "-c", "commit.gpgsign=false")
MAIN, MILESTONE, STORY = "main", "feat/ledger-hygiene", "feat/ledger-hygiene-s01"
PLAN = "docs/specs/ledger-hygiene/plan.json"
# (branch, history step, commit message), in order; the story commit is shaped as
# a story run commits, a subject and two trailers.
COMMITS = (
    (MILESTONE, "milestone", "docs(ledger-hygiene): plan the month-close stories"),
    (STORY, "s01", "feat(S01): comment lines in the ledger\n\nStory-ID: S01\nPlan: %s" % PLAN),
)
REFS = "origin-refs.txt"
ORIGIN = "origin.git"


def git(cwd, *args):
    done = subprocess.run(["git"] + list(args), cwd=str(cwd),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if done.returncode != 0:
        raise SystemExit("git %s: %s" % (" ".join(args), done.stderr.decode("utf-8", "replace")))
    return done.stdout.decode("utf-8")


def remote_refs(origin):
    return git(origin, "for-each-ref", "--format=%(refname) %(objectname)")


def build(run):
    run = Path(run)
    workspace, origin = run / "workspace", run / ORIGIN
    git(workspace, "branch", "-M", MAIN)
    git(run, "init", "-q", "--bare", str(origin))
    git(origin, "symbolic-ref", "HEAD", "refs/heads/" + MAIN)
    git(workspace, "remote", "add", "origin", str(origin))
    for branch, step, message in COMMITS:
        git(workspace, "checkout", "-q", "-b", branch)
        source = HISTORY / step
        # By path, never `add -A`: the workflow runner provisions its own files
        # into the workspace before this step runs.
        paths = []
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            rel = path.relative_to(source)
            (workspace / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(str(path), str(workspace / rel))
            paths.append(rel.as_posix())
        git(workspace, "add", "--", *paths)
        git(workspace, *(IDENTITY + ("commit", "-q", "-m", message)))
        if branch == MILESTONE:
            git(workspace, "push", "-q", "-u", "origin", MAIN, MILESTONE)
    git(workspace, "remote", "set-head", "origin", MAIN)
    (run / REFS).write_text(remote_refs(origin), encoding="utf-8")
    (run / "fixture-head.txt").write_text(git(workspace, "rev-parse", "HEAD"), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: history.py <run dir>")
    build(sys.argv[1])
