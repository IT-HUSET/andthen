"""Run-directory staging, Codex registration, dispatch, run-record readers.

A Claude cell runs in the operator's own environment: the parent environment
passes through whole, so the subject sees the settings, memory, agents, MCP
servers and installed candidate a real session sees, which is what the corpus is
there to measure. Nothing to stage, nothing to register.

Codex cannot follow. DartClaw pins Codex's CODEX_HOME to
<data_dir>/credentials/codex whatever the environment holds, so a Codex cell
registers a snapshot of the candidate there; a run that left the environment
alone would leave it unregistered, which is how Gate 0's first attempts failed.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from evals import cases
from evals.cases import REPO_ROOT, read_text

# Claude seeds nothing: with no credential in <data_dir>/credentials and
# `auth: auto`, a host-mode turn falls through to the CLI's own login, so the
# cell always runs as the account the operator watches instead of a stale,
# account-bound setup token. Codex still seeds: `auth: subscription` resolves
# per spawn against <data_dir>/credentials, and DartClaw's login_store_guard
# refuses a credentials dir that resolves onto the operator's real login path,
# so copying in is the only shape it accepts, and a run directory starts empty.
CREDENTIALS = {"codex": Path.home() / ".codex/auth.json"}

# All a Codex cell's dispatch inherits; a Claude cell inherits everything.
ENV_KEYS = ("PATH", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "SHELL", "TERM")

# One dispatch carries subject, checks and judge, so the turn ceiling and the
# cell's wall are not one number: a subject turn keeps its hour, and the wall
# adds the tail's own declared timeouts (1800 + 900) on top. A wall covering only
# the subject would kill a long cell mid-judge, leaving its completed work
# neither checked nor judged.
TURN_TIMEOUT = 3600
TIMEOUT = TURN_TIMEOUT + 1800 + 900

# <case>/<provider>/<stamp> under here is one cell's evidence. It is read to debug
# the latest runs and never as history - the numbers worth keeping are committed
# with the change they justified - so a tier keeps the newest KEEP cells of each
# case and provider. A directory not named as a stamp is somebody's deliberate keep.
EVIDENCE = REPO_ROOT / ".agent_temp" / "evals"
KEEP = 3
STAMP_TIME = "%Y%m%dT%H%M%S"
STAMP = re.compile(r"(\d{8}T\d{6})-[0-9a-f]{8}")

# The Codex marketplace source. plugin/ alone registers nothing: the CLI reads the
# manifests to find it, so both are staged beside it. andthen@andthen is enabled.
CANDIDATE_ASSETS = ("plugin", ".claude-plugin/marketplace.json",
                    ".agents/plugins/marketplace.json")

# The vendored application every overlay case starts from. Its deliberate flaws
# are documented beside it, never inside it, for the same reason `oracle.py` is
# never copied into a workspace.
SUBJECT = REPO_ROOT / "evals" / "subject"

# Where every skill that writes a review report puts it, per the review skill's
# Step 5 and the `--output-dir` the spec and clarify skills pass it. Ignored by
# the subject app, so stage_diff forces this subtree - and only this one - in.
REPORTS = ".agent_temp/reviews"

# What the checks step leaves for the judge step, in a directory of its own: the
# judge's provider is granted that directory and nothing else of the run, which
# costs the subject nothing because it is empty until the subject has finished.
REQUEST = "request/judge-request.json"

# The one edit staging makes to a case's own workflow text. A subject that judges
# its own step failed must still reach the checks - its self-report is not
# evidence - and `onFailure` is a per-step field no `stepDefaults` entry carries.
SELF_REPORT_TOLERANCE = "    onFailure: continue"

# One artifact over this is a subject's scratch rather than work to weigh, and
# the judge payload is a model's context: the largest real artifact the corpus
# has produced is a 58 KB review report, so 256 KiB leaves it four times over.
MAX_ARTIFACT_BYTES = 256 * 1024

# Committing as the run keeps a cell reproducible on a host with no git identity.
IDENTITY = ("-c", "user.name=andthen-evals", "-c", "user.email=evals@andthen.invalid",
            "-c", "commit.gpgsign=false")

CODEX_CONFIG = """[marketplaces.andthen]
source_type = "local"
source = "{candidate}"

[plugins."andthen@andthen"]
enabled = true

[projects."{workspace}"]
trust_level = "trusted"
"""

# Where the operator's Claude Code keeps the plugins it has installed, which is
# where the candidate runs from now that nothing redirects the config dir.
CLAUDE_PLUGINS = Path(os.environ.get("CLAUDE_CONFIG_DIR")
                      or Path.home() / ".claude") / "plugins"

# Both subjects run unprompted in a throwaway workspace. Claude's `dontAsk`
# denies any tool outside an allow-list, so the trust Codex gets from
# `approval: never` is spelled out here; DartClaw refuses bypass mode for a
# workflow step. `dontAsk` also denies a read outside the workspace, so the two
# directories a cell reaches outside it are named: the plugin bundle whose
# references a skill reads, and the judge step's request directory.
PROVIDER_BLOCK = {
    "claude": ("    auth: auto\n    inherit_user_settings: true\n"
               "    pool_size: 1\n    permissionMode: dontAsk\n"
               "    permissions:\n      allow: [Bash, Read, Glob, Grep, Write, Edit, "
               "NotebookEdit, Skill, Agent, TodoWrite, EnterWorktree, ExitWorktree]\n"
               "    settings:\n      additionalDirectories:\n        - %s\n"
               "        - {request}\n" % CLAUDE_PLUGINS),
    # Codex's workspace-write sandbox keeps .git read-only, and an executor
    # commits its story; the workspace is the run's own, so full access is the
    # Codex spelling of the Claude allow-list above.
    "codex": ("    auth: subscription\n    pool_size: 1\n"
              "    approval: never\n    sandbox: danger-full-access\n"),
}


def new_run_dir(case, provider):
    """`data/` is DartClaw's own state, per run so one cell's ledger, sessions and
    credentials are never another's; `home/` and `provider/` are the environment
    only a Codex cell dispatches under."""
    stamp = "%s-%s" % (time.strftime(STAMP_TIME), uuid.uuid4().hex[:8])
    path = EVIDENCE / case / provider / stamp
    path.mkdir(parents=True)
    for name in ("data",) + (("home", "provider") if provider == "codex" else ()):
        (path / name).mkdir()
    return path


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(repo, *args):
    """Decoded leniently rather than with `text=True`: a subject writes whatever
    bytes its probe produced, and a strict decode of a diff carrying one latin-1
    CSV raised out of staging and took the whole cell's verdict with it."""
    done = subprocess.run(["git", "-C", str(repo)] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = (raw.decode("utf-8", "replace") for raw in (done.stdout, done.stderr))
    if done.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), err.strip()))
    return out


def stage_workspace(run, case_dir):
    """The starting tree as one commit: the vendored subject app with the case's
    `overlay/` copied over it, an overlay file replacing the app's file of the
    same path - or the app unchanged, for a case that reviews or acts on it as it
    ships and has nothing to add - or, for a case whose prompt needs a project the
    app is not, the case's `fixture/` alone. *Contents* either way, because a
    workflow prompt names files workspace-relative: `feature-request.md`. An
    optional `dirty/` directory is copied over the committed workspace so a case
    can start with uncommitted work - a resumed story's earlier edits, a user's
    unrelated change - which is what the isolation journeys are about."""
    workspace = run / "workspace"
    fixture = case_dir / "fixture"
    if not fixture.is_dir():
        # Neither a run of the app's own suite nor a Finder window is part of
        # the project a subject reads.
        shutil.copytree(str(SUBJECT), str(workspace), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    staged = fixture if fixture.is_dir() else case_dir / "overlay"
    if staged.is_dir():
        shutil.copytree(str(staged), str(workspace), dirs_exist_ok=True)
    for name in ("prompt.md", "scripted-replies.json"):
        if (case_dir / name).is_file():
            shutil.copy2(str(case_dir / name), str(workspace / name))
    # One commit of the starting state, so the diff afterwards is the subject's,
    # and named for what it is to the subject that reads this history: a
    # project's own baseline, not a harness word.
    git(workspace, "init", "-q")
    git(workspace, "add", "-A")
    git(workspace, *(IDENTITY + ("commit", "-q", "-m", "baseline")))
    write(run / "fixture-head.txt", git(workspace, "rev-parse", "HEAD"))
    dirty = case_dir / "dirty"
    if dirty.is_dir():
        shutil.copytree(str(dirty), str(workspace), dirs_exist_ok=True)
        # Planted bytes are the starting state: stage_diff drops a planted path
        # the subject left as it found it, so the checks see only what the
        # subject did to it.
        write(run / "dirty-baseline.json", json.dumps(dict(
            (p.relative_to(dirty).as_posix(), _digest(p))
            for p in dirty.rglob("*") if p.is_file()), indent=2) + "\n")
    return workspace


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage_candidate(run):
    for rel in CANDIDATE_ASSETS:
        source, target = REPO_ROOT / rel, run / "candidate" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if source.is_dir() else shutil.copy2)(str(source), str(target))


def stage_workflows(run, case_dir):
    """The case's workflow and the harness tail as one definition, which is what
    makes a cell one DartClaw run. The tail is appended verbatim - the harness has
    no YAML parser and must not become one - and the only edit to the case's own
    text is SELF_REPORT_TOLERANCE on each of its steps; cases.validate has already
    refused a workflow this join would not extend cleanly. The request directory is
    created empty here, so the judge's provider can be granted it before any step
    runs and the subject finds nothing in it."""
    custom = run / "data" / "workflows" / "custom"
    custom.mkdir(parents=True, exist_ok=True)
    (run / REQUEST).parent.mkdir(parents=True, exist_ok=True)
    subject = "".join(
        line + "\n" + (SELF_REPORT_TOLERANCE + "\n" if cases.STEP_ITEM.match(line) else "")
        for line in read_text(case_dir / "subject-workflow.yaml").splitlines())
    write(custom / "subject-workflow.yaml", subject + read_text(cases.TAIL_WORKFLOW))


def register_codex(run):
    """Codex is handed the marketplace and the plugin materialized in its cache,
    the layout Gate 0 ran on, under the CODEX_HOME DartClaw pins. Written before
    the credential is seeded, so a missing one leaves no half-written registration
    behind. Claude needs no counterpart: the operator's own environment already
    registers the candidate."""
    home = run / "data" / "credentials" / "codex"
    source = run / "candidate" / "plugin"
    version = json.loads(read_text(source / ".claude-plugin" / "plugin.json"))["version"]
    cache = home / "plugins" / "cache" / "andthen" / "andthen" / version
    if not cache.is_dir():
        shutil.copytree(str(source), str(cache))
    write(home / "config.toml", CODEX_CONFIG.format(
        candidate=run / "candidate", workspace=run / "workspace"))


def seed_credentials(run, providers):
    for provider in providers:
        source = CREDENTIALS.get(provider)
        if source and source.is_file():
            target = run / "data" / "credentials" / provider / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(target))


def clear_credentials(run):
    """Whatever the outcome: a run directory is shared evidence, a token is not -
    and neither is the CODEX_HOME DartClaw pins beside it, some 65 MB of Codex's
    own state a cell that no check, judge, or report reads."""
    shutil.rmtree(str(run / "data" / "credentials"), ignore_errors=True)


def sweep(root=None, keep=KEEP, now=None):
    """Once, before a tier's first cell. A cell killed outright never reached its
    own teardown, so its token is still on disk; two walls after its stamp it
    cannot be a cell of a tier in flight elsewhere, and clearing it is safe. The
    cells past the newest `keep` go whole - a running cell is always among those."""
    now = time.time() if now is None else now
    for cells in (p for p in (root or EVIDENCE).glob("*/*") if p.is_dir()):
        stamped = sorted(p for p in cells.iterdir() if p.is_dir() and STAMP.fullmatch(p.name))
        for cell in stamped[:-keep]:
            shutil.rmtree(str(cell), ignore_errors=True)
        for cell in stamped[-keep:]:
            began = time.mktime(time.strptime(STAMP.fullmatch(cell.name).group(1), STAMP_TIME))
            if now - began > 2 * TIMEOUT:
                clear_credentials(cell)


def _claude_wrapper(run):
    """A Codex cell's judge step still runs on Claude, spawned by DartClaw under
    the empty HOME dispatch_env builds for Codex - so the `claude` CLI it finds
    reports `Not logged in`. This wrapper is that spawn's executable instead: it
    restores the operator's real HOME (and CLAUDE_CONFIG_DIR, if set) for the one
    exec, while Codex itself keeps running under the empty HOME."""
    real = shutil.which("claude") or "claude"
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    # `env` takes its options before any assignment, so the unset comes first.
    env_args = ("CLAUDE_CONFIG_DIR=%s" % config_dir) if config_dir else "-u CLAUDE_CONFIG_DIR"
    path = run / "claude"
    write(path, "#!/bin/sh\nexec env %s HOME=%s %s \"$@\"\n"
          % (env_args, os.environ.get("HOME", ""), real))
    path.chmod(0o755)
    return path


def write_config(path, run, workspace, subject, judge):
    """The Gate 0 run config with this run's paths substituted; `subject` and
    `judge` are {provider, model, effort} and the return is the subject's
    executable, which a failed dispatch has to name. One run carries both steps,
    so both roles are configured: `@workflow`, which every subject workflow pins,
    defaults to claude inside DartClaw rather than to agent.provider (a Codex cell
    otherwise crashes wiring an unconfigured claude provider), and `@reviewer`,
    which the tail's judge step pins. A judge on the other provider needs that
    provider declared too, or its step resolves to nothing."""
    provider, model, effort = subject["provider"], subject["model"], subject["effort"]
    executable = shutil.which(provider) or provider
    # DartClaw's own 30-minute turn ceiling, raised to TURN_TIMEOUT: exec-plan runs
    # every story and its gate in one turn (0.25.1 precedence: a step's own
    # turn_timeout, then stepDefaults, then this value; 0.24.3 read neither key
    # and capped every step at thirty minutes). Its stall watchdog only warns:
    # a subject waiting on a subagent emits nothing for minutes, and a cancel
    # there killed a spec run mid-review; TIMEOUT still bounds the cell.
    text = ("data_dir: %s\ncontainer:\n  enabled: false\n"
            "governance:\n  turn_limits:\n    turn_timeout: %d\n    stall_action: warn\n"
            "agent:\n  provider: %s\n  model: %s\n  effort: %s\n  execution: host\n"
            "providers:\n" % (run / "data", TURN_TIMEOUT, provider, model, effort))
    for name in dict.fromkeys((provider, judge["provider"])):
        wrapped = name == "claude" and provider == "codex"
        exe = _claude_wrapper(run) if wrapped else shutil.which(name) or name
        text += "  %s:\n    executable: %s\n" % (name, exe)
        if wrapped:
            # DartClaw's own auth gate reads the dartclaw-workflow process's HOME
            # (the empty one dispatch_env gives a Codex cell), not the executable
            # it is configured to spawn, so it refuses "claude" before the wrapper
            # ever runs; credentials_required: false skips that gate outright and
            # leaves the login to the wrapped binary (security.md ~line 518).
            text += "    credentials_required: false\n"
        text += PROVIDER_BLOCK[name].format(request=(run / REQUEST).parent)
    text += "workflow:\n  workspace_dir: %s\n  defaults:\n" % workspace
    for role, seat in (("workflow", subject), ("reviewer", judge)):
        text += ("    %s:\n      provider: %s\n      model: %s\n      effort: %s\n"
                 % (role, seat["provider"], seat["model"], seat["effort"]))
    write(path, text)
    return executable


def preflight(providers):
    """Everything that stops this cell, or '' - all at once, because fixing one
    name at a time costs a staging round trip per name."""
    missing = sorted(set(t for t in ("dartclaw-workflow",) + tuple(providers)
                         if not shutil.which(t)))
    absent = sorted(set(str(CREDENTIALS[p]) for p in providers
                        if p in CREDENTIALS and not CREDENTIALS[p].is_file()))
    return "; ".join(["%s: %s" % (label, ", ".join(names))
                      for label, names in (("unresolved on PATH", missing),
                                           ("missing subscription credential", absent))
                      if names])


def dispatch_env(run, provider):
    """The operator's own, except for Codex: DartClaw builds the CODEX_HOME it
    pins by mirroring the operator's ~/.codex plugin tables, so a Codex cell gets
    an empty HOME and the candidate it registered stands alone. The judge step's
    `claude` spawn still needs the operator's real environment, which is what
    _claude_wrapper restores for that one process."""
    if provider != "codex":
        return dict(os.environ)
    env = dict((key, os.environ[key]) for key in ENV_KEYS if key in os.environ)
    env["HOME"] = str(run / "home")
    env["CLAUDE_CONFIG_DIR"] = env["CODEX_HOME"] = str(run / "provider")
    return env


def dispatch(run, provider, config, name, workspace, variables):
    """The cell's one DartClaw run, retaining stdout, stderr, and exit code.
    --inline is load-bearing: without it DartClaw works in a worktree under
    workspace/.dartclaw/worktrees/<uuid> and the artifacts never reach the
    workspace the evaluator reads. The tail's steps read `variables` through
    --var; a bash step's environment is allowlisted down to PATH and its
    neighbours, so a path cannot reach the checks step any other way."""
    env = dispatch_env(run, provider)
    command = ["dartclaw-workflow", "--config", str(config), "run", name,
               "--inline", "--force", "--json", "--approvals", "auto"]
    for key, value in variables.items():
        command += ["--var", "%s=%s" % (key, value)]
    timed_out = False
    try:
        done = subprocess.run(command, cwd=str(workspace), env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIMEOUT)
        code, out, err = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out, code = True, 124
        out, err = [v.decode("utf-8", "replace") if isinstance(v, bytes) else (v or "")
                    for v in (exc.stdout, exc.stderr)]
        err += "timed out after %ds\n" % TIMEOUT
    write(run / "stdout.jsonl", out)
    write(run / "stderr.log", err)
    write(run / "exit.json", json.dumps(
        {"command": command, "exitCode": code, "timedOut": timed_out}, indent=2) + "\n")
    return {"exitCode": code, "timedOut": timed_out}


def stage_diff(run, workspace):
    """(changed paths, added-or-modified paths), with diff.patch retained. Staged,
    not working-tree: DartClaw excludes the skills it provisions through
    .git/info/exclude, so a bare `git diff` misses files a subject creates, and
    .dartclaw is excluded here because DartClaw does not exclude it. Against
    the fixture commit, not HEAD: an executor commits its story, and a diff
    from HEAD would show the judge an implementation-free change."""
    base = read_text(run / "fixture-head.txt").strip() or "HEAD"
    git(workspace, "add", "-A", "--", ".", ":!.dartclaw")
    # The project's own .gitignore is not the harness's: the subject app ignores
    # .agent_temp/, and REPORTS under it is where the review, spec and clarify
    # skills write the report the judge has to see. Only that subtree is forced
    # in - everything else a subject leaves under .agent_temp is its own working
    # scratch, and forcing all of it put a 27 MB probe CSV into one cell's diff.
    # The artifact checks walk the filesystem, so the scratch stays visible there.
    if any(p.is_file() for p in (workspace / REPORTS).rglob("*")):
        git(workspace, "add", "-f", "--", REPORTS)
    try:
        planted = json.loads(read_text(run / "dirty-baseline.json") or "{}")
    except ValueError:
        planted = {}
    untouched = set(rel for rel, digest in planted.items()
                    if (workspace / rel).is_file() and _digest(workspace / rel) == digest)
    changed = sorted(p for p in git(workspace, "diff", "--cached", base, "--name-only").split("\n")
                     if p and p not in untouched)
    touched = sorted(line.split("\t")[-1] for line
                     in git(workspace, "diff", "--cached", base, "--name-status").split("\n")
                     if line and line[0] in "AM" and line.split("\t")[-1] not in untouched)
    write(run / "diff.patch", git(workspace, "diff", "--cached", base))
    # The index was the harness's, not the subject's: an oracle that asks git
    # whether the caller's edit is still dirty must see the tree as it was left.
    git(workspace, "reset", "-q")
    return changed, touched


def changed_text(workspace, touched):
    """(path -> content for every text file the diff adds or modifies, [omission]).
    A file that does not decode as UTF-8, or is over MAX_ARTIFACT_BYTES, is left
    out and reported in the second list instead: the judge still sees the subject
    wrote it, no probe output balloons the payload, and the reason stays out of
    the artifacts - a note the harness wrote is not material a judge may quote to
    ground a PASS."""
    artifacts, omitted = {}, []
    for rel in touched:
        path = workspace / rel
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > MAX_ARTIFACT_BYTES:
            omitted.append({"path": rel, "bytes": size,
                            "reason": "over the %d-byte artifact cap" % MAX_ARTIFACT_BYTES})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            omitted.append({"path": rel, "bytes": size, "reason": "not UTF-8 text"})
        except OSError:
            continue
        else:
            if text:
                artifacts[rel] = text
    return artifacts, omitted


def _lines(path):
    for line in read_text(path).splitlines():
        if line.strip():
            try:
                yield json.loads(line)
            except ValueError:
                continue


def run_record(stdout_path):
    """(run id, [(step id, [declared output name])], [step id reached, in order]),
    read from the workflow's own event stream so no case's steps are named in the
    harness. The caller drops the tail's own two."""
    run_id, steps, seen = None, [], []
    for event in _lines(stdout_path):
        kind = event.get("type")
        if kind == "run_started":
            run = event.get("run") or {}
            run_id = run.get("id")
            steps = [(s.get("id"), sorted((s.get("outputs") or {}).keys()))
                     for s in (run.get("definitionJson") or {}).get("steps", [])]
        elif kind in ("task_status_changed", "workflow_step_completed") and event.get("stepId"):
            seen.append(event["stepId"])
    return run_id, steps, seen


def run_context(run, run_id=None):
    """Declared outputs and per-step metadata, which stdout.jsonl does not carry.
    By run id wherever the caller holds one, so a data dir that comes to hold a
    second record (a resume, a nested run) cannot have another run's outputs
    weighed as this one's; the checks step alone reads this mid-run, before any
    event has named the id, and falls back to the newest record that parses."""
    runs = run / "data" / "workflows" / "runs"
    for path in ([runs / run_id] if run_id else
                 sorted(runs.iterdir(), reverse=True) if runs.is_dir() else []):
        try:
            return (json.loads((path / "context.json").read_text(encoding="utf-8"))
                    or {}).get("data") or {}
        except (OSError, ValueError):
            continue
    return {}


def step_outputs(context):
    """([settled step id], {declared output name: what a step wrote}). DartClaw
    writes `<id>.status` for every step it settles, which is what names the ids;
    a declared output name is bare, so anything dotted is per-step bookkeeping and
    anything `_`-prefixed is DartClaw's own - neither is the subject's work, and
    the second half is material a judge may quote to ground a PASS."""
    settled = [key[:-len(".status")] for key in context if key.endswith(".status")]
    return settled, dict((key, value) for key, value in context.items()
                         if "." not in key and not key.startswith("_"))


def session_cost(run, session_id):
    """DartClaw's own accounting for one session, from data/kv.json: fresh input,
    output, cache read and write, its cache-weighted `effective_tokens`, and a
    list-price estimate. Short on both hosts until DartClaw counts the subagent
    sessions a step spawns (Claude) and every turn's cumulative usage (Codex):
    today the row is the step's main session, or its last turn."""
    if not session_id:
        return None
    try:
        kv = json.loads((run / "data" / "kv.json").read_text(encoding="utf-8"))
        raw = json.loads(kv["session_cost:%s" % session_id]["value"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return {"input": raw.get("input_tokens"), "output": raw.get("output_tokens"),
            "cacheRead": raw.get("cache_read_tokens"),
            "cacheWrite": raw.get("cache_write_tokens"),
            "effective": raw.get("effective_tokens"),
            "estimatedUsd": raw.get("estimated_cost_usd")}


def assistant_messages(run, session_id):
    """What the subject actually said in one step, for the judge to read."""
    if not session_id:
        return []
    path = run / "data" / "sessions" / str(session_id) / "messages.ndjson"
    return [m.get("content") for m in _lines(path) if m.get("role") == "assistant"]
