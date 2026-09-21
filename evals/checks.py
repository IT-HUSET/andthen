"""The deterministic check evaluator.

One evaluator over one key set, no per-case knowledge. Every check reports an ID
of the form `<key>[<index>]`, a verdict, and one evidence line, because a failure
a maintainer cannot read costs a second live eval run to diagnose. ERROR and FAIL stay
apart: a command that ran and failed is about the subject, one that could not start
is about the machine, and conflating them blames the wrong thing.
"""

import fnmatch
import os
import subprocess
import sys

from evals.cases import read_text, REPO_ROOT

PASS, FAIL, ERROR = "pass", "fail", "error"

# Long enough for a repo's validators and test suite, short enough that a hung
# command does not hold a cell open for the dispatch timeout.
COMMAND_TIMEOUT = 600

# DartClaw provisions its own skills into the workspace and excludes them itself;
# .dartclaw is the worktree root it does not exclude. Neither is subject output.
SKIP_DIRS = {".git", ".dartclaw"}


def outcome(results):
    """ERROR beats FAIL beats PASS - an unusable machine is never a regression."""
    seen = set(r["status"] for r in results)
    return "ERROR" if ERROR in seen else ("FAIL" if FAIL in seen else "PASS")


def workspace_files(workspace):
    found = (p.relative_to(workspace) for p in workspace.rglob("*") if p.is_file())
    return sorted(r.as_posix() for r in found if not SKIP_DIRS.intersection(r.parts))


def matches(pattern, paths):
    """Paths matching one check pattern: an exact path when it holds no glob
    character, and a `**/` prefix matched at the root too - fnmatch wants a
    separator the root path lacks, so `**/x.md` would miss a subject that wrote
    x.md there, and a case cannot predict which one it gets."""
    candidates = (pattern, pattern[3:]) if pattern.startswith("**/") else (pattern,)
    return [p for p in paths if any(fnmatch.fnmatch(p, c) for c in candidates)]


def evaluate(check, workspace, changed, case_dir):
    """Run every key of one check.json against the workspace and its diff."""
    files = workspace_files(workspace)
    results = []
    for key, wanted in (("requiredArtifacts", True), ("forbiddenArtifacts", False)):
        for index, pattern in enumerate(check.get(key, [])):
            hit = matches(pattern, files)
            results.append(_result(key, index, bool(hit) is wanted,
                                   "%s matches %s" % (hit[0], pattern) if hit
                                   else "nothing in the workspace matches %s" % pattern))
    if "allowedPaths" in check:
        # One check over the diff, not one per pattern: the constraint is that no
        # changed path escapes the set, so the offending path is the evidence.
        allowed = check["allowedPaths"] or []
        stray = [p for p in changed if not any(matches(a, [p]) for a in allowed)]
        results.append(_result("allowedPaths", 0, not stray,
                               "changed path outside allowedPaths: %s" % stray[0] if stray
                               else "%d changed path(s) within allowedPaths" % len(changed)))
    results.extend(_text(check, workspace, files))
    for index, command in enumerate(check.get("commands", [])):
        results.append(_run("commands", index, command, workspace, True))
    if check.get("oracle"):
        # Resolved against the case directory and never copied into the workspace:
        # an oracle the subject can read is an oracle it can satisfy.
        results.append(_run("oracle", 0, [sys.executable, str(case_dir / check["oracle"])],
                            workspace, False))
    return results


def _text(check, workspace, files):
    """requiredText / forbiddenText, one check per (path pattern, substring). A
    pattern rather than a fixed path because a subject chooses where it writes:
    the spec case's FIS lands wherever the skill puts it. Case-insensitive: a
    non-goal written `Web API` at the start of a bullet is the requested
    `web API`."""
    results = []
    for key, wanted in (("requiredText", True), ("forbiddenText", False)):
        index = 0
        for pattern, needles in sorted((check.get(key) or {}).items()):
            hit = matches(pattern, files)
            for needle in needles:
                bad = [p for p in hit
                       if (needle.lower() in read_text(workspace / p).lower()) is not wanted]
                results.append(_result(
                    key, index, bool(hit) and not bad,
                    "no workspace file matches %s" % pattern if not hit
                    else "%s %r in %s" % ("missing" if wanted else "found", needle, bad[0])
                    if bad else "%r ok in %s" % (needle, pattern)))
                index += 1
    return results


def _run(key, index, command, cwd, shell):
    # Decoded leniently rather than with `text=True`: a fixture test or oracle
    # can print a non-UTF-8 byte, and a strict decode would raise out of the
    # evaluator and turn a subject FAIL into a harness ERROR.
    # ANDTHEN_ROOT lets a check run the tree's own scripts: the workspace has
    # no fixed path back to the tree (Claude cells stage no `candidate/`).
    env = dict(os.environ, ANDTHEN_ROOT=str(REPO_ROOT))
    try:
        done = subprocess.run(command, cwd=str(cwd), shell=shell, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=COMMAND_TIMEOUT)
    except subprocess.TimeoutExpired:
        return _result(key, index, None, "no exit within %ds" % COMMAND_TIMEOUT)
    except OSError as exc:
        return _result(key, index, None, "could not start: %s" % exc)
    out, err = (raw.decode("utf-8", "replace") for raw in (done.stdout, done.stderr))
    tail = " ".join(((err or out or "").strip().splitlines() or [""])[-2:])[:300]
    # Exit 127 is the shell's "command not found": a missing executable is the
    # machine's problem, and reporting it as FAIL would blame the subject.
    return _result(key, index, None if done.returncode == 127 else done.returncode == 0,
                   "exit %d%s: %s" % (done.returncode,
                                      ", executable not found" if done.returncode == 127 else "",
                                      tail))


def _result(key, index, ok, evidence):
    """ok is True, False, or None for a check that could not run at all."""
    return {"id": "%s[%d]" % (key, index),
            "status": ERROR if ok is None else (PASS if ok else FAIL),
            "evidence": evidence}
