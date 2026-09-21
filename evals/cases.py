"""Case discovery, case validation, and profile resolution.

A case is a directory of data files and this is the only module that knows what
those files must look like, which makes growing the corpus a data change.
Validation runs before anything is staged: an invalid case that reached dispatch
would spend a live model call to learn what a JSON parse already knew.

The harness is Python 3 standard library only and stays 3.9-compatible - the
autonomous proofs run under macOS's /usr/bin/python3, CI runs 3.12 and later.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
CASES_DIR = ROOT / "cases"
PROFILES = ROOT / "profiles.json"

# Appended to every case's subject workflow so a cell is one DartClaw run: the
# checks and the judge are the definition's last two steps, written once here
# rather than copied into every case.
TAIL_WORKFLOW = ROOT / "workflows" / "tail.yaml"
TAIL_STEPS = ("checks", "judge")

PROVIDERS = ("claude", "codex")
PROVIDER_CHOICES = PROVIDERS + ("both",)

# Tiers are named sets, not durations measured at run time, so a developer knows
# what a tier costs before paying for it. `smoke` is the per-change signal: every
# cell finishes under SMOKE_SECONDS on the subject model, so five-wide the tier
# is a few minutes of wall. One long cell sets the whole tier's wall, so the
# report names a smoke cell over the bar. The bar keeps the tier to a few minutes
# rather than budgeting a cell, so it sits above the slowest cell instead of on
# it. `full` is every case, the release check, and its longest cells run up to
# half an hour each. Codex runs the smoke tier only: the long cells are
# Claude-only, so `full` on Codex is `smoke`.
SMOKE = ("implement-fix", "implement-fix-intent", "implement-fix-request",
         "now-what-active-plan", "now-what-uninitialized", "review-quick",
         "spec-active-protected", "spike-isolation")
SMOKE_SECONDS = 300
TIERS = ("smoke", "full")


def tier(name, provider):
    """The case names one provider runs for a tier."""
    return discover() if name == "full" and provider == "claude" else list(SMOKE)

# The complete check key set. A key outside it is an ERROR rather than a silently
# ignored line, because a check nobody runs reads exactly like a check that passed.
CHECK_KEYS = ("requiredArtifacts", "forbiddenArtifacts", "allowedPaths",
              "commands", "requiredText", "forbiddenText", "oracle")

REQUIRED_FILES = ("prompt.md", "subject-workflow.yaml", "check.json", "rubric.json")

# A case starts from its own committed files. Naming another case or a prior run
# is how one cell would come to depend on another's output.
FORBIDDEN_REFS = ("evals/cases/", ".agent_temp/evals/")

# A case's `overlay/` and `dirty/` are staged into the tree the subject reads, so
# they are held to the silence SubjectAppTest keeps over the app itself: a subject
# that can read what it is being measured on can satisfy the measurement without
# doing the work. `defect` is not on this list, though the app's own is stricter -
# `code-defect` is the one Class a Fix-routed finding carries, so a planted review
# report cannot avoid it.
OVERLAY_WORDS = ("planted", "fixture", "eval", "dartclaw", "oracle", "judge", "rubric")

# One judge turn decides every criterion, so the ceiling is what that turn can
# weigh before its evidence budget thins.
MAX_CRITERIA = 6

# DartClaw dispatches by declared name, not by filename. A line match, not a YAML
# parse: the harness has no YAML library and must not become one - staging joins
# the case's text and the tail's, so the shape the join relies on is read the
# same way. TOP_LEVEL_KEY and STEP_ITEM anchor at column 0 and at the indent a
# step item sits on, which a folded prompt body and an inline schema cannot reach.
WORKFLOW_NAME = re.compile(r"^name:[ \t]*(\S.*?)[ \t]*$", re.M)
TOP_LEVEL_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):", re.M)
STEP_ITEM = re.compile(r"^([ \t]*)-[ \t]+id:[ \t]*(\S+)")
STEP_ON_FAILURE = re.compile(r"^[ \t]{4}onFailure:", re.M)


def discover():
    """Case names from the directory listing rather than a registry."""
    return sorted(p.name for p in CASES_DIR.iterdir()
                  if p.is_dir() and not p.name.startswith(".")) if CASES_DIR.is_dir() else []


def read_text(path):
    """Text, or '' when the file is unreadable or not text."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def named_words(text, words):
    """The listed words `text` actually uses, matched whole and case-insensitively
    with an optional plural: a substring rule refuses `retrieval` and `evaluate`
    for `eval`, which is ordinary prose, while `evals` is the leak it is for."""
    lowered = text.lower()
    return [word for word in words
            if re.search(r"\b%ss?\b" % re.escape(word), lowered)]


def load_json(path):
    """(value, error) - the error names the file."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError:
        return None, "%s: unreadable" % path.name
    except ValueError as exc:
        return None, "%s: not parseable JSON (%s)" % (path.name, exc)


def workflow_name(path):
    found = WORKFLOW_NAME.search(read_text(path))
    return found.group(1) if found else None


def load_profile(name):
    """The named profile, or raise naming the ones that do resolve."""
    data, error = load_json(PROFILES)
    if error:
        raise ValueError(error)
    known = sorted(data) if isinstance(data, dict) else []
    if name not in known:
        raise KeyError("unknown profile %r; %s holds: %s"
                       % (name, PROFILES.name, ", ".join(known) or "nothing"))
    return data[name]


def validate(case_dir):
    """Every reason this case cannot run, one line each; empty means valid. Every
    reason rather than the first: one defect per round trip is a slow way to
    author a case."""
    if not case_dir.is_dir():
        return ["%s: not a directory" % case_dir.name]
    errors = ["%s: missing" % n for n in REQUIRED_FILES if not (case_dir / n).is_file()]
    overlay = case_dir / "overlay"
    if overlay.is_dir() and (case_dir / "fixture").is_dir():
        errors.append("overlay/ and fixture/: a case carries at most one - overlay/ is "
                      "applied over the vendored subject app, while fixture/ is a whole "
                      "workspace and is only for a case whose prompt needs a project "
                      "the app is not")
    for staged in (overlay, case_dir / "dirty"):
        errors.extend(_staged_errors(staged))
    errors.extend(_check_errors(case_dir))
    errors.extend(_rubric_errors(case_dir))

    errors.extend(_workflow_errors(case_dir / "subject-workflow.yaml"))
    for path in sorted(case_dir.rglob("*")):
        text = read_text(path) if path.is_file() else ""
        errors.extend("%s: names %s, so the case does not start from its own "
                      "committed files" % (path.relative_to(case_dir).as_posix(), ref)
                      for ref in FORBIDDEN_REFS if ref in text)
    return errors


def _workflow_errors(path):
    """What staging needs of a subject workflow before appending the tail to it.
    The join is text, so a file ending in another top-level key, or indenting its
    steps differently, would become a definition nobody authored - and a key the
    join would write twice is a YAML parse error DartClaw only reports at
    dispatch, once the cell has already paid for staging."""
    if not path.is_file():
        return []
    text = read_text(path)
    keys = TOP_LEVEL_KEY.findall(text)
    items = [m for m in (STEP_ITEM.match(line) for line in text.splitlines()) if m]
    errors = ["subject-workflow.yaml: no top-level name: line, and DartClaw dispatches "
              "by declared name"] if workflow_name(path) is None else []
    if keys[-1:] != ["steps"]:
        errors.append("subject-workflow.yaml: last top-level key is %r, and the tail is "
                      "appended to the steps list it extends" % (keys[-1] if keys else None))
    if not items or any(m.group(1) != "  " for m in items):
        errors.append("subject-workflow.yaml: every step item must be `  - id: <id>` at "
                      "the two-space indent the appended tail uses")
    if "variables" in keys:
        errors.append("subject-workflow.yaml: a top-level variables: block, which the "
                      "appended tail declares too, so the join carries the key twice")
    if STEP_ON_FAILURE.search(text):
        errors.append("subject-workflow.yaml: a step-level onFailure: field, which staging "
                      "inserts on every step, so the join carries the field twice")
    return errors + ["subject-workflow.yaml: step id %r belongs to the appended tail"
                     % m.group(2) for m in items if m.group(2) in TAIL_STEPS]


def _staged_errors(directory):
    """Every listed word a staged file names, for `overlay/` or `dirty/` alike -
    both are copied into the workspace, so both are read by the subject."""
    return ["%s/%s: names %r, and a file the subject reads must not tell it what is "
            "being tested" % (directory.name, path.relative_to(directory).as_posix(), word)
            for path in (sorted(directory.rglob("*")) if directory.is_dir() else [])
            if path.is_file()
            for word in named_words(read_text(path), OVERLAY_WORDS)]


def _strings(value, empty_ok=False):
    return (isinstance(value, list) and (empty_ok or value)
            and all(isinstance(v, str) and v.strip() for v in value))


def _check_errors(case_dir):
    """Value shapes as well as key names: `commands: [7]` passed the name check
    and raised during evaluation, and `requiredText: []` contributed no check
    at all, which reads exactly like a check that passed."""
    path = case_dir / "check.json"
    if not path.is_file():
        return []
    check, error = load_json(path)
    if error or not isinstance(check, dict):
        return [error or "check.json: not a JSON object"]
    errors = ["check.json: unknown key %r, not a check key" % k
              for k in check if k not in CHECK_KEYS]
    for key in ("requiredArtifacts", "forbiddenArtifacts", "commands", "allowedPaths"):
        # allowedPaths may be empty: present-and-empty rejects every change.
        if key in check and not _strings(check[key], empty_ok=key == "allowedPaths"):
            errors.append("check.json: %s must be a list of non-empty strings" % key)
    for key in ("requiredText", "forbiddenText"):
        value = check.get(key)
        if key in check and not (isinstance(value, dict) and value and all(
                isinstance(k, str) and k.strip() and _strings(v) for k, v in value.items())):
            errors.append("check.json: %s must map path patterns to non-empty lists "
                          "of non-empty strings" % key)
    oracle = check.get("oracle")
    if oracle is not None:
        target = (case_dir / oracle) if isinstance(oracle, str) else None
        inside = target is not None and target.is_file() and not target.is_symlink() and \
            case_dir.resolve() in target.resolve().parents
        if not inside:
            errors.append("check.json: oracle %r is not a regular file inside the case"
                          % oracle)
    return errors


def _rubric_errors(case_dir):
    path = case_dir / "rubric.json"
    if not path.is_file():
        return []
    rubric, error = load_json(path)
    if error:
        return [error]
    criteria = rubric.get("criteria") if isinstance(rubric, dict) else None
    if not isinstance(criteria, list) or not criteria:
        return ["rubric.json: criteria must be a non-empty list"]
    if len(criteria) > MAX_CRITERIA:
        return ["rubric.json: %d criteria exceeds the %d the judge accepts"
                % (len(criteria), MAX_CRITERIA)]
    if not all(isinstance(c, dict) and isinstance(c.get("id"), str) and c["id"].strip()
               and isinstance(c.get("intent"), str) and c["intent"].strip()
               for c in criteria):
        return ["rubric.json: every criterion needs a non-blank string id and intent"]
    identifiers = [c["id"] for c in criteria]
    if len(set(identifiers)) != len(identifiers):
        # A duplicate id would let one decision answer for two criteria.
        return ["rubric.json: duplicate criterion id %s"
                % next(i for i in identifiers if identifiers.count(i) > 1)]
    return []
