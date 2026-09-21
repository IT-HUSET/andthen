"""The deterministic half of a cell, run as a step of the cell's own workflow.

    python3 evals/step.py --case <case dir> --run <run dir>

A CLI over checks.evaluate and stage.stage_diff, never a second implementation of
either: the tail's `checks` step invokes this, so one DartClaw run carries the
subject, the checks, and the judge. A PASS and a FAIL both get the request, so
the judge weighs the workspace the checks weighed: a check is cheap enough to be
miscalibrated, and one vetoing the judge step turned a wording check nobody had
recalibrated into a skill regression with no verdict to contradict it. Exits
nonzero when this step cannot do its own job, or when a check could not run -
DartClaw stops a run at a bash step that exits nonzero, and an ERROR is a cell
the harness failed to evaluate, so a judge turn spent on it buys nothing.

The rubric still reaches nowhere the subject could read it: this step runs after
the subject's last one, and writes into request/, the one directory outside the
workspace the judge's provider is granted.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evals import cases, checks, stage  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 evals/step.py")
    parser.add_argument("--case", required=True, help="the case directory")
    parser.add_argument("--run", required=True, help="the cell's run directory")
    args = parser.parse_args(argv)
    case_dir, run = Path(args.case), Path(args.run)
    workspace = run / "workspace"

    check, error = cases.load_json(case_dir / "check.json")
    if error:
        sys.stderr.write(error + "\n")
        return 1
    changed, touched = stage.stage_diff(run, workspace)
    results = checks.evaluate(check, workspace, changed, case_dir)
    stage.write(run / "checks.json", json.dumps(results, indent=2) + "\n")
    # DartClaw keeps a bash step's stderr in the run record as `checks.stderr`,
    # which is where a PASS or a FAIL now shows, since the exit code no longer
    # carries it.
    outcome = checks.outcome(results)
    sys.stderr.write("checks: %s\n" % outcome)
    if outcome == "ERROR":
        return 1

    context = stage.run_context(run)
    settled, outputs = stage.step_outputs(context)
    artifacts, omitted = stage.changed_text(workspace, touched)
    stage.write(run / stage.REQUEST, json.dumps({
        "rubric": cases.load_json(case_dir / "rubric.json")[0],
        "prompt": cases.read_text(case_dir / "prompt.md"),
        "artifacts": artifacts,
        "omitted": omitted,
        "diff": cases.read_text(run / "diff.patch"),
        "outputs": outputs,
        "messages": dict((step, stage.assistant_messages(
            run, context.get("%s.sessionId" % step))) for step in settled),
    }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
