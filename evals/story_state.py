"""One plan-story reader for the case oracles that reconcile plan state.

Case data, not harness: it carries no case's expectations, only the shape every
`plan.json` story record has, so a case whose oracle only reconciles story state
needs no reader of its own. A case's `oracle.py` imports it by a path it computes
from `__file__`, because the evaluator runs an oracle by absolute path with the
workspace as the working directory.

Python 3 standard library only, 3.9-compatible.
"""

import json


def stories(path):
    """([story record], [problem]) - the plan's story rows, or why there are none."""
    if not path.is_file():
        return [], ["no %s in the workspace" % path]
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return [], ["%s: unreadable" % path]
    except ValueError as exc:
        return [], ["%s: not parseable JSON (%s)" % (path, exc)]
    rows = plan.get("stories") if isinstance(plan, dict) else None
    if not isinstance(rows, list) or not rows:
        return [], ["%s: no stories" % path]
    return [row for row in rows if isinstance(row, dict)], []


def story(path, identifier):
    """(one story record, [problem]) for a case that names the story it drove."""
    rows, problems = stories(path)
    if problems:
        return None, problems
    found = [row for row in rows if row.get("id") == identifier]
    return (found[0], []) if found else (None, ["%s: no story %s" % (path, identifier)])


def diverges(path, row, verified=False, **wanted):
    """Every way one story row diverges from the state a case expects. `wanted`
    names story fields by their own keys - status, completedTaskIds, fis - and
    `verified` asks for the at/summary record the run session writes when it
    marks the story done, from the proof lines that were executed, which is the
    only trace binding a status to a run rather than to a narrative."""
    problems = ["%s: story %s %s is %r, expected %r"
                % (path, row.get("id"), field, row.get(field), want)
                for field, want in sorted(wanted.items()) if row.get(field) != want]
    if not verified:
        return problems
    record = row.get("verified")
    if not isinstance(record, dict):
        return problems + ["%s: story %s has no verified record, expected one the "
                           "run session writes on done" % (path, row.get("id"))]
    return problems + ["%s: story %s verified.%s is %r, expected a non-empty string"
                       % (path, row.get("id"), field, record.get(field))
                       for field in ("at", "summary")
                       if not (isinstance(record.get(field), str)
                               and record[field].strip())]
