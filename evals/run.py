"""python3 -m evals.run <case|smoke|full>... --provider claude|codex|both [--jobs N] [--profile name]

One cell is validate, stage, preflight, one dispatch, classify, write, and the
runner carries no per-case knowledge - everything specific to a case lives in its
directory, which makes growing the corpus a data change. The checks and the
judge are the last two steps of that same run, appended from workflows/tail.yaml,
so the runner reads their results out of the run it already dispatched rather than
assembling and dispatching a second one. Both weigh every cell: a PASS is the
checks and the judge's criteria together, so neither layer can veto the other and
a failing check is read beside a verdict rather than in place of one. The
outcomes are not grades of each other: FAIL is about the subject, ERROR about the
case, the machine, or the judge and never a regression, PASS one run's evidence.
Every cell writes result.json and summary.md, preflight refusals included, so a
maintainer reads the cause instead of paying to see it.

A tier is a named set (cases.SMOKE, or every case), and --jobs runs its cells N
at a time: each cell is its own DartClaw run over its own run directory and
workspace, so no cell can see another's work and the only limit is what the
provider subscriptions will serve at once. Wall time is what makes a suite get
run at all - one cell at a time makes the full tier hours.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from evals import cases, checks, stage

def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m evals.run")
    parser.add_argument("case", nargs="+", help="case directory names or tiers (%s)"
                        % ", ".join(cases.TIERS))
    parser.add_argument("--provider", required=True)
    parser.add_argument("--jobs", type=int, default=1, help="cells run at a time")
    parser.add_argument("--profile", default="default")
    args = parser.parse_args(argv)
    chosen = args.provider

    discovered = cases.discover()
    unknown = [w for w in args.case if w not in cases.TIERS and w not in discovered]
    if unknown:
        return _refuse("unknown case %r; tiers: %s; discovered under %s: %s"
                       % (unknown[0], ", ".join(cases.TIERS), cases.CASES_DIR.name,
                          ", ".join(discovered) or "none"))
    if chosen not in cases.PROVIDER_CHOICES:
        return _refuse("unknown provider %r; valid: %s"
                       % (chosen, ", ".join(cases.PROVIDER_CHOICES)))
    if args.jobs < 1:
        return _refuse("--jobs must be at least 1")
    try:
        profile = cases.load_profile(args.profile)
    except (KeyError, ValueError) as exc:
        # str(KeyError) is the repr of its argument; the message is args[0].
        return _refuse(exc.args[0] if exc.args else str(exc))

    providers = list(cases.PROVIDERS) if chosen == "both" else [chosen]
    selected = []
    for provider in providers:
        for wanted in args.case:
            for name in (cases.tier(wanted, provider) if wanted in cases.TIERS else [wanted]):
                if (name, provider) not in selected:
                    selected.append((name, provider))
    # Independent: one cell's ERROR must not cost the others their results, and
    # the pool never reorders the report, so a row is found where it was asked for.
    started = time.time()
    stage.sweep()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        rows = list(pool.map(lambda cell: run_cell(cell[0], cell[1], args.profile, profile),
                             selected))
    return _report(rows, time.time() - started)


def run_cell(case, provider, profile_name, profile):
    """One case on one provider. Returns (result, run directory or None)."""
    started = time.time()
    cell = _new_cell(case, provider, profile_name, profile)
    staged = {}
    try:
        _execute(cell, staged, cases.CASES_DIR / case, provider)
    except Exception as exc:  # noqa: BLE001
        # A staging or dispatch failure belongs to the machine, not the subject.
        # Reporting it keeps the staged evidence; propagating would lose it.
        cell["error"] = "%s: %s" % (type(exc).__name__, exc)
    finally:
        # Ctrl-C skips the except clause, and a seeded token must not outlive the
        # cell. A kill skips this too; the next tier's stage.sweep clears that one.
        if staged.get("run"):
            stage.clear_credentials(staged["run"])
    if cell["error"]:
        cell["outcome"] = "ERROR"
    cell["durationSeconds"] = round(time.time() - started, 3)
    run = staged.get("run")
    if run is not None:
        cell["tokens"] = dict((role, stage.session_cost(run, cell[role]["sessionId"]))
                              for role in ("subject", "judge"))
        # One level under request/: the bare token names none of the files a
        # maintainer opens to see what the judge was asked.
        top = list(run.iterdir())
        cell["evidence"] = sorted(
            ["request/%s" % c.name for p in top if p.name == "request" and p.is_dir()
             for c in p.iterdir()]
            + [p.name for p in top if p.name != "request"] + ["result.json", "summary.md"])
        stage.write(run / "result.json", json.dumps(cell, indent=2) + "\n")
        stage.write(run / "summary.md", _summary(cell))
    return cell, run


def _new_cell(case, provider, profile_name, profile):
    subject = (profile.get("subject") or {}).get(provider) or {}
    judge = profile.get("judge") or {}
    return {"case": case, "provider": provider, "profile": profile_name,
            "subject": {"provider": provider, "model": subject.get("model"),
                        "effort": subject.get("effort"), "sessionId": None, "runId": None},
            "judge": {"provider": judge.get("provider"), "model": judge.get("model"),
                      "effort": judge.get("effort"), "sessionId": None},
            "candidate": _candidate(), "outcome": "ERROR", "error": None,
            "checks": [], "criteria": [], "evidence": [], "durationSeconds": 0.0,
            "tokens": {"subject": None, "judge": None}}


def _execute(cell, staged, case_dir, provider):
    invalid = cases.validate(case_dir)
    if invalid:
        cell["error"] = "invalid case: " + "; ".join(invalid)
        return
    if not cell["subject"]["model"] or not cell["judge"]["model"]:
        cell["error"] = ("profile %r resolves no model for subject %s or the judge"
                         % (cell["profile"], provider))
        return
    if shutil.which("git") is None:
        cell["error"] = "unresolved on PATH: git, and staging needs it"
        return

    run = staged["run"] = stage.new_run_dir(cell["case"], provider)
    used = [provider] + [p for p in [cell["judge"]["provider"]] if p and p != provider]
    if "codex" in used:
        # Claude reads the candidate the operator already has installed; Codex
        # reads a snapshot, because DartClaw pins where it looks.
        stage.stage_candidate(run)
        stage.register_codex(run)
    workspace = stage.stage_workspace(run, case_dir)
    stage.seed_credentials(run, used)
    stage.stage_workflows(run, case_dir)
    config = run / "dartclaw.yaml"
    executable = stage.write_config(config, run, workspace, cell["subject"], cell["judge"])

    cell["error"] = stage.preflight(used)
    if cell["error"]:
        return

    dispatched = stage.dispatch(
        run, provider, config, cases.workflow_name(case_dir / "subject-workflow.yaml"),
        workspace, {"repo_root": cases.REPO_ROOT, "case_dir": case_dir, "run_dir": run})
    run_id, steps, seen = stage.run_record(run / "stdout.jsonl")
    context = stage.run_context(run, run_id)
    subject_steps = [(s, names) for s, names in steps if s not in cases.TAIL_STEPS]
    last_step = ([s for s in seen if s not in cases.TAIL_STEPS] or [None])[-1]
    cell["subject"]["sessionId"] = _session(context, subject_steps)
    cell["subject"]["runId"] = run_id
    # A subject that judges its own step failed has still run to the end and
    # written what it declared; its self-report is not evidence, so the checks
    # and the judge weigh it - which is why staging tolerates it rather than
    # letting the run stop there. Only a dispatch that produced no subject step,
    # or left the last one's declared outputs unwritten, is a harness ERROR.
    missing = [name for step, names in subject_steps if step == last_step
               for name in names if context.get(name) is None]
    if dispatched["timedOut"] or last_step is None or missing:
        cell["error"] = _dispatch_error(dispatched, last_step, executable, missing)
        return

    worktrees = workspace / ".dartclaw" / "worktrees"
    stray = sorted(p.relative_to(workspace).as_posix() for p in worktrees.rglob("*")
                   if p.is_file()) if worktrees.is_dir() else []
    if stray:
        # --inline did not land the artifacts in workspace/, a harness condition:
        # evaluating anyway reports every artifact check as a subject that
        # produced nothing.
        cell["error"] = "subject artifacts stayed in a DartClaw worktree: %s" % stray[0]
        return

    loaded, error = cases.load_json(run / "checks.json")
    if error:
        # The checks are a step of the run, so their absence is the step's:
        # stderr.log carries what the workflow said about it. cell["checks"]
        # stays [] (its _new_cell default) rather than None, so _summary and
        # any report code iterating it need no guard.
        cell["error"] = "the checks step recorded no results (%s); see stderr.log" % error
        return
    cell["checks"] = loaded
    cell["outcome"] = checks.outcome(cell["checks"])
    # A check that could not run names itself here; one that ran and failed
    # leaves error null, so FAIL keeps pointing at the subject.
    cell["error"] = "; ".join("check %s could not run: %s" % (c["id"], c["evidence"])
                              for c in cell["checks"]
                              if c["status"] == checks.ERROR) or None
    if cell["outcome"] == "ERROR":
        # A check that could not run leaves a workspace nothing can be concluded
        # about; a check that failed leaves one the judge still has to weigh.
        return
    _decide(cell, run, context, dispatched)


def _decide(cell, run, context, dispatched):
    """The judge step, weighed against what the checks step handed it. The judge
    is a step of the subject's own run, so isolation is its own session rather
    than its own dispatch: an id that comes back as the subject's says the
    boundary failed, and a verdict from a judge that continued the subject's
    session is not independent. Missing ids alone prove nothing either way."""
    cell["judge"]["sessionId"] = session = context.get("judge.sessionId")
    if session and session == cell["subject"]["sessionId"]:
        cell["outcome"], cell["error"] = "ERROR", (
            "the judge step reused the subject session %r" % session)
        return
    request, error = cases.load_json(run / stage.REQUEST)
    if error:
        cell["outcome"], cell["error"] = "ERROR", (
            "the checks step wrote no judge request (%s); see stderr.log" % error)
        return
    # A judge step that never settled answered nothing, and nothing is not a bad
    # answer: DartClaw writes `judge.status` for a step it settles, so its absence
    # is the step erroring, pausing, or dying with the dispatch. A settled agent
    # step's real value is "accepted" (a live context.json, 2026-09-15).
    status = context.get("judge.status")
    if status != "accepted":
        cell["outcome"], cell["error"] = "ERROR", (
            "the judge step %s, dispatch exit %d; see stderr.log"
            % ("recorded no status" if status is None else "settled %r" % status,
               dispatched["exitCode"]))
        return
    stage.write(run / "judge-result.json",
                json.dumps(context.get("judge_result"), indent=2, default=str) + "\n")
    identifiers = [c["id"] for c in request["rubric"]["criteria"]]
    # Raw text and the JSON-escaped form the judge actually read: a quote of a
    # line holding quotes or backslashes comes back in either shape. `omitted` is
    # cut from both - a note the harness wrote about a file it left out is not
    # the subject's work, and a PASS grounded in it would prove nothing.
    material = _material(request) + "\n" + _squash(
        json.dumps(dict(request, omitted=[]), indent=2))
    decisions = _decisions(context.get("judge_result"), identifiers, material)
    if decisions is None:
        cell["outcome"], cell["error"] = "ERROR", (
            "the judge returned an output that is unparseable, does not name each of %s "
            "exactly once, or passes a criterion without a reason and evidence quoted "
            "from the retained subject material; see judge-result.json"
            % ", ".join(identifiers))
        return
    cell["criteria"] = decisions
    # The harness derives the verdict and the judge decides criteria: no score
    # and no weighting, so nobody can tune a run into passing. The checks are the
    # other half of the conjunction - they ran before the judge did, and one that
    # failed still fails the cell whatever the criteria say.
    cell["outcome"] = "PASS" if (all(d["pass"] for d in decisions)
                                 and checks.outcome(cell["checks"]) == "PASS") else "FAIL"


def _decisions(output, identifiers, material):
    """The judge's decisions, or None when this attempt was not usable. A PASS
    needs a reason and an evidence line found in the retained material: the
    quote proves the judge read the artifact, not that the criterion holds -
    calibration stays with the rubric - but an empty or invented quote is a
    verdict nobody can check. A FAIL may cite an absence."""
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except ValueError:
            return None
    decisions = output.get("decisions") if isinstance(output, dict) else None
    if not isinstance(decisions, list) or not all(isinstance(d, dict) for d in decisions):
        return None
    if sorted(str(d.get("id")) for d in decisions) != sorted(identifiers):
        return None
    for d in decisions:
        if not (isinstance(d.get("pass"), bool) and isinstance(d.get("evidence"), str)
                and isinstance(d.get("reason"), str) and d["reason"].strip()):
            return None
        if d["pass"] and not _grounded(d["evidence"], material):
            return None
    return decisions


def _grounded(evidence, material):
    """Every fragment of the quote is in the retained material. A judge that
    joins two verbatim lines with an ellipsis has still read both; an empty
    quote, or one with an invented fragment, proves nothing. Backslashes are
    stripped from both sides first: a step output that embeds JSON of its own
    gets escaped once for that JSON and again when the request is serialised,
    so the same text can sit in the material at any escaping depth while the
    judge always quotes it unescaped - comparing with backslashes removed
    makes the match independent of how deep the escaping went."""
    material = material.replace("\\", "")
    fragments = [f for f in re.split(r"\.{3}|\u2026", evidence) if f.strip()]
    return bool(fragments) and all(_squash(f).replace("\\", "") in material for f in fragments)


def _squash(text):
    r"""Whitespace folded and markdown emphasis dropped on both sides: a judge
    quoting `**Final snapshot:** \`HEAD 7035bdf\`` writes it plain, and the
    quote still proves it read the line."""
    return " ".join(str(text).replace("*", "").replace("`", "").split())


def _material(request):
    """Everything the judge was handed as quoted data, whitespace-folded so a
    quote that wraps differently from the artifact still resolves. Step outputs
    go in raw as well as serialised: a report holding a dash or a quote reads
    `\u2014` and `\"` in the JSON, and the judge quotes the text it saw."""
    parts = [request["prompt"], request["diff"], json.dumps(request["outputs"])]
    parts += [v for v in request["outputs"].values() if isinstance(v, str)]
    parts += list(request["artifacts"].values())
    parts += [m for msgs in request["messages"].values() for m in msgs if isinstance(m, str)]
    return _squash("\n".join(p for p in parts if p))


def _session(context, steps):
    """The last subject step that recorded one, so the subject's id and the
    judge's stay distinct."""
    recorded = [context.get("%s.sessionId" % step) for step, _ in steps]
    return ([s for s in recorded if s] or [None])[-1]


def _dispatch_error(dispatched, step, executable, missing=()):
    cause = ("did not finish within %ds" % stage.TIMEOUT if dispatched["timedOut"]
             else "wrote no declared output %s" % ", ".join(missing) if missing
             else "completed no subject step" if step is None else "failed")
    return ("dartclaw %s at step %s, exit %d, executable %s; see stderr.log"
            % (cause, step or "none", dispatched["exitCode"], executable))


def _candidate():
    """What was tested: the working tree's commit and dirtiness, and the copy the
    subject actually loads. A Claude cell dispatches in the operator's own
    environment, so it runs the installed plugin rather than this tree - a cell
    whose result named only the tree reported a candidate the run never used."""
    def out(*args):
        return subprocess.run(["git", "-C", str(cases.REPO_ROOT)] + list(args), text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        head = out("rev-parse", "HEAD")
    except OSError:
        head = None
    candidate = ({"head": None, "dirty": None} if head is None or head.returncode else
                 {"head": head.stdout.strip(),
                  "dirty": bool(out("status", "--porcelain").stdout.strip())})
    installed = _installed_plugin()
    candidate.update({"installedHead": installed.get("gitCommitSha"),
                      "installPath": installed.get("installPath"),
                      "installMatches": _install_matches(installed.get("installPath"))})
    return candidate


def _installed_plugin():
    """The `andthen@andthen` record Claude Code wrote at install time, or {} when
    there is no readable manifest. Its first entry: a second is the same plugin
    installed at another scope, and which one a session loads is Claude Code's
    decision, not something this file says."""
    manifest = cases.load_json(stage.CLAUDE_PLUGINS / "installed_plugins.json")[0]
    plugins = manifest.get("plugins") if isinstance(manifest, dict) else None
    entry = plugins.get("andthen@andthen") if isinstance(plugins, dict) else None
    return entry[0] if entry and isinstance(entry[0], dict) else {}


_INSTALL_IGNORE = {".DS_Store", ".in_use", ".git"}


def _install_matches(install_path):
    """Whether the installed plugin directory is byte-identical to the working
    tree's plugin/, or None when there is nothing to compare. The manifest's
    `gitCommitSha` is Claude Code's own bookkeeping, not an object in this repo,
    so staleness is decided by content instead."""
    if not install_path:
        return None
    installed, source = Path(install_path), cases.REPO_ROOT / "plugin"
    if not installed.is_dir() or not source.is_dir():
        return None
    def snapshot(root):
        return {p.relative_to(root): p.read_bytes() for p in root.rglob("*")
                if p.is_file() and not _INSTALL_IGNORE & set(p.relative_to(root).parts)}
    return snapshot(installed) == snapshot(source)


def _install_note(cell):
    """Whether this cell's installed plugin is what the report should trust, or
    None. Claude only: a Codex cell registers a snapshot of the working tree,
    so there is no install for it to drift from."""
    if cell["provider"] != "claude":
        return None
    matches = (cell.get("candidate") or {}).get("installMatches")
    if matches is None:
        return "installed plugin unknown"
    return None if matches else (
        "installed plugin differs from the working tree's plugin/ - "
        "a Claude cell measures the install")


def _reason(cell):
    """The one line that says why a row is not a PASS: its cause, or the first
    check or criterion that did not pass. Trimmed, because the table is scanned -
    summary.md carries every check and every decision in full."""
    parts = ([cell["error"]] if cell.get("error") else
             ["%s %s: %s" % (c["id"], c["status"], c["evidence"])
              for c in cell.get("checks") or [] if c["status"] != checks.PASS]
             + ["%s fail: %s" % (d["id"], d["reason"])
                for d in cell.get("criteria") or [] if not d["pass"]])
    return " ".join(parts[0].split())[:120] if parts else "-"


def _summary(cell):
    def role(name, provider):
        return "%s %s / %s, session %s" % (provider, cell[name]["model"],
                                           cell[name]["effort"],
                                           cell[name]["sessionId"] or "none")
    candidate = cell["candidate"]
    lines = ["# %s / %s - %s" % (cell["case"], cell["provider"], cell["outcome"]), "",
             "- profile: %s" % cell["profile"],
             "- subject: %s" % role("subject", cell["provider"]),
             "- judge: %s" % role("judge", cell["judge"]["provider"]),
             "- candidate: %s%s" % (candidate["head"] or "unknown",
                                    " (dirty)" if candidate["dirty"] else "")]
    if cell["provider"] == "claude":
        # Only a Claude cell has an install to report: it dispatches in the
        # operator's environment and loads what he installed, while a Codex cell
        # registers a snapshot of the tree the candidate sha already names.
        lines.append("- installed plugin: %s%s"
                     % (candidate.get("installedHead") or "unknown",
                        " at %s" % candidate["installPath"]
                        if candidate.get("installPath") else ""))
    lines += ["- duration: %ss" % cell["durationSeconds"],
              "- tokens: subject %s; judge %s" % tuple(
                  _tokens(cell["tokens"][r]) for r in ("subject", "judge"))]
    # Every check, passing ones included: "this check failed and every criterion
    # passed" is a miscalibrated case, and the failures alone do not show it.
    for heading, body in (
            ("Cause", [cell["error"]] if cell["error"] else []),
            ("Checks", ["- %s %s: %s" % (c["id"], c["status"], c["evidence"])
                        for c in cell["checks"]]),
            ("Criteria", ["- %s %s: %s - %s" % (d["id"], "pass" if d["pass"] else "fail",
                                                d.get("reason", ""), d["evidence"])
                          for d in cell["criteria"]]),
            ("Retained evidence", ["- %s" % p for p in sorted(cell["evidence"])])):
        if body:
            lines += ["", "## %s" % heading, ""] + body
    return "\n".join(lines) + "\n"


def _tokens(cost):
    """One session's accounting on a line, or `none` when DartClaw recorded nothing."""
    if not cost:
        return "none"
    usd = cost.get("estimatedUsd")
    return ("in %s / out %s / cache read %s / cache write %s / effective %s%s"
            % (cost.get("input"), cost.get("output"), cost.get("cacheRead"),
               cost.get("cacheWrite"), cost.get("effective"),
               " / est $%.2f" % usd if isinstance(usd, (int, float)) else ""))


def _report(rows, wall):
    # The reason where the token column was: a row that says only FAIL costs a
    # maintainer an open, while the token accounting is read one cell at a time
    # and is in that cell's summary.md and result.json.
    print("case | provider | outcome | seconds | run | reason")
    notes = []
    for cell, run in rows:
        seconds = cell.get("durationSeconds") or 0
        print("%s | %s | %s | %d | %s | %s"
              % (cell["case"], cell["provider"], cell["outcome"], round(seconds),
                 run.relative_to(cases.REPO_ROOT).as_posix() if run else "-", _reason(cell)))
        # A cell refused before staging has no run directory to read, so its
        # cause is printed under the table rather than lost; so is a smoke cell
        # over the tier bar, because one such cell is the whole tier's wall, and
        # a Claude cell that ran a plugin this tree has moved on from.
        causes = [cell["error"]] if run is None and cell["error"] else []
        if cell["case"] in cases.SMOKE and seconds > cases.SMOKE_SECONDS:
            causes.append("%ds over the %ds smoke bar" % (round(seconds), cases.SMOKE_SECONDS))
        causes += [note for note in [_install_note(cell)] if note]
        notes += ["  %s/%s: %s" % (cell["case"], cell["provider"], c) for c in causes]
    for note in notes:
        print(note)
    print("%d cell(s) in %ds wall" % (len(rows), wall))
    return 0 if rows and all(cell["outcome"] == "PASS" for cell, _ in rows) else 1


def _refuse(message):
    """Before setup, so an unknown name never costs a staged run directory."""
    sys.stderr.write(message + "\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
