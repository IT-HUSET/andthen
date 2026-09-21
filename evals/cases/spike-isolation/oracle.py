#!/usr/bin/env python3
"""Isolation reconciliation for the spike case, run with cwd = the workspace. The caller checkout must be on its original branch with no stash and its dirty edit still dirty; a spike branch must exist whose commits carry only spike-owned paths. That the sentinel files still hold their contents is check.json's to read.

Case data, not harness. Python 3 standard library only, 3.9-compatible."""

import subprocess
import sys


def git(*args):
    done = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    return done.stdout.strip() if done.returncode == 0 else None


SENTINELS = ("src/reporter/cli.py", "scratch.txt")


def check():
    problems = []
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or ""
    if branch.startswith("spike/"):
        problems.append("caller checkout was left on %s" % branch)
    if git("stash", "list"):
        problems.append("a stash was left behind: the caller tree was stashed")
    status = [line.strip() for line in (git("status", "--porcelain") or "").splitlines()]
    if "M %s" % SENTINELS[0] not in status:
        problems.append("%s is no longer dirty - it was staged, committed, or reverted"
                        % SENTINELS[0])
    branches = [b.strip() for b in (git("branch", "--list", "spike/*") or "").splitlines()]
    if not branches:
        return problems + ["no spike/* branch exists - the spike left no evidence"]
    for spike in branches:
        base = git("merge-base", "HEAD", spike)
        changed = (git("diff", "--name-only", base, spike) or "").split() if base else []
        for sentinel in SENTINELS:
            if sentinel in changed:
                problems.append("%s carries %s, a caller file" % (spike, sentinel))
    return problems


def main():
    problems = check()
    for problem in problems:
        sys.stderr.write(problem + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
