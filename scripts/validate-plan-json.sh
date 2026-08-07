#!/usr/bin/env bash
#
# validate-plan-json.sh – schema invariant validator for plan.json
#
# Checks a plan.json file against this machine-checkable subset of the
# invariants in plugin/references/plan-schema.md:
#   - canonical JSON formatting: 2-space indentation, trailing newline, no
#     byte-level formatting drift
#   - schemaVersion === "1"
#   - stories[].id is uppercase S + exactly two digits, present, and unique
#   - stories[].status in {pending, spec-ready, in-progress, done, skipped, blocked}
#   - every dependsOn[] element matches some stories[].id
#   - stories[].fis values unique and canonical; resolved targets are contained,
#     regular non-symlink siblings with matching Plan/Story provenance
#   - legacy metadata blocks are tolerated but ignored
#   - top-level and object keys are within the schema-named set and appear in
#     schema order (extra unknown keys fail loudly rather than silently propagating)
#
# Note: metadata.immutableDigest enforcement was retired in 0.20.0. A missing
# digest is valid; a present legacy 0.19.x digest is reported but never fails.
#
# Out of scope (intentionally not checked here): per-field type validation,
# enum membership for risk, presence of optional-but-recommended fields, and
# other semantic checks (e.g. wave references in stories matching overview.phases[].waves).
# Those are owned by the producer skill, not this drift-regression harness.
#
# Usage: scripts/validate-plan-json.sh <path-to-plan.json>
# Exit:  0 = all invariants hold; 1 = at least one violation; 2 = bad usage / unreadable input.
#
set -o pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <path-to-plan.json>" >&2
  exit 2
fi

PLAN_PATH="$1"

if [[ ! -r "$PLAN_PATH" ]]; then
  echo "error: cannot read $PLAN_PATH" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required but not found on PATH" >&2
  exit 2
fi

python3 - "$PLAN_PATH" <<'PY'
import json
import os
import re
import subprocess
import sys

TOP_LEVEL_KEYS = [
    "schemaVersion", "prd", "references", "overview",
    "sharedDecisions", "bindingConstraints", "stories",
    "riskSummary", "executionNotes",
]
LEGACY_TOP_LEVEL_KEYS = {"metadata"}
OVERVIEW_KEYS = ["summary", "phases"]
PHASE_KEYS = ["id", "name", "waves"]
SHARED_DECISION_KEYS = ["title", "description", "stories"]
BINDING_CONSTRAINT_KEYS = ["featureId", "anchor", "verbatim"]
STORY_KEYS = [
    "id", "name", "phase", "wave", "dependsOn", "parallel", "risk",
    "status", "fis", "owner", "scope", "sourceRefs", "provenance", "assetRefs", "notes",
]
RISK_SUMMARY_KEYS = ["story", "risk", "mitigation"]
STATUS_ENUM = {"pending", "spec-ready", "in-progress", "done", "skipped", "blocked"}

def check_key_order(obj, expected, label, ignored=()):
    if not isinstance(obj, dict):
        return
    keys = [k for k in obj.keys() if k not in ignored]
    known_positions = [expected.index(k) for k in keys if k in expected]
    if known_positions != sorted(known_positions):
        errors.append(f"{label}: keys are not in schema order (expected relative order: {expected})")

def check_unknown_keys(obj, expected, label, ignored=()):
    if not isinstance(obj, dict):
        return
    known = set(expected) | set(ignored)
    extra = [k for k in obj.keys() if k not in known]
    if extra:
        errors.append(f"{label}: unknown keys {sorted(extra)} (allowed: {sorted(known)})")

def canonical_fis_name(story):
    sid = story.get("id")
    name = story.get("name")
    if not isinstance(sid, str) or not re.fullmatch(r"S\d{2}", sid):
        return None
    if not isinstance(name, str):
        return None
    slug = re.sub(r"[^a-z0-9\s-]", "", name.lower())
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    if not slug:
        return None
    return f"s{sid[1:]}-{slug}.md"

def project_root(plan_dir):
    try:
        result = subprocess.run(
            ["git", "-C", plan_dir, "rev-parse", "--show-toplevel"],
            check=False, capture_output=True, text=True,
        )
    except OSError:
        return None
    return os.path.realpath(result.stdout.strip()) if result.returncode == 0 else None

def fis_provenance(fis_path):
    plan_values = []
    story_values = []
    with open(fis_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                break
            if line.startswith("**Plan**:"):
                plan_values.append(line.split(":", 1)[1].strip())
            elif line.startswith("**Story-ID**:"):
                story_values.append(line.split(":", 1)[1].strip())
    return plan_values, story_values

display_path = sys.argv[1]
path = os.path.realpath(display_path)
plan_dir = os.path.dirname(path)
with open(path, "rb") as f:
    raw = f.read()
try:
    doc = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"FAIL: malformed JSON: {e}")
    sys.exit(1)

errors = []

canonical = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
if raw != canonical.encode("utf-8"):
    errors.append("formatting is not canonical (expected 2-space indentation, stable JSON serialization, and trailing newline)")

if doc.get("schemaVersion") != "1":
    errors.append(f"schemaVersion is {doc.get('schemaVersion')!r}, expected \"1\"")

stories = doc.get("stories")
if not isinstance(stories, list):
    print("FAIL: stories[] missing or not an array")
    sys.exit(1)

ids = []
seen = set()
for i, s in enumerate(stories):
    sid = s.get("id")
    if sid is None:
        errors.append(f"story[{i}]: missing required 'id' field")
        continue
    if not isinstance(sid, str) or not re.fullmatch(r"S\d{2}", sid):
        errors.append(f"story[{i}]: invalid id {sid!r} (expected S + exactly two digits)")
        continue
    if sid in seen:
        errors.append(f"duplicate story id: {sid!r}")
    seen.add(sid)
    ids.append(sid)

id_set = set(ids)

# Reject unknown keys for all schema-defined object shapes. Legacy metadata is
# accepted for migration compatibility but ignored by current consumers.
check_unknown_keys(doc, TOP_LEVEL_KEYS, "top-level object", LEGACY_TOP_LEVEL_KEYS)
check_key_order(doc, TOP_LEVEL_KEYS, "top-level object", LEGACY_TOP_LEVEL_KEYS)
for s in stories:
    check_unknown_keys(s, STORY_KEYS, f"story {s.get('id', '?')!r}")
    check_key_order(s, STORY_KEYS, f"story {s.get('id', '?')!r}")

overview = doc.get("overview")
if isinstance(overview, dict):
    check_unknown_keys(overview, OVERVIEW_KEYS, "overview")
    check_key_order(overview, OVERVIEW_KEYS, "overview")
    phases = overview.get("phases")
    if isinstance(phases, list):
        for i, phase in enumerate(phases):
            check_unknown_keys(phase, PHASE_KEYS, f"overview.phases[{i}]")
            check_key_order(phase, PHASE_KEYS, f"overview.phases[{i}]")
for i, item in enumerate(doc.get("sharedDecisions", []) or []):
    check_unknown_keys(item, SHARED_DECISION_KEYS, f"sharedDecisions[{i}]")
    check_key_order(item, SHARED_DECISION_KEYS, f"sharedDecisions[{i}]")
for i, item in enumerate(doc.get("bindingConstraints", []) or []):
    check_unknown_keys(item, BINDING_CONSTRAINT_KEYS, f"bindingConstraints[{i}]")
    check_key_order(item, BINDING_CONSTRAINT_KEYS, f"bindingConstraints[{i}]")
for i, item in enumerate(doc.get("riskSummary", []) or []):
    check_unknown_keys(item, RISK_SUMMARY_KEYS, f"riskSummary[{i}]")
    check_key_order(item, RISK_SUMMARY_KEYS, f"riskSummary[{i}]")

for s in stories:
    sid = s.get("id", "?")
    status = s.get("status")
    if status not in STATUS_ENUM:
        errors.append(f"story {sid}: invalid status {status!r} (must be one of {sorted(STATUS_ENUM)})")
    deps = s.get("dependsOn", [])
    if not isinstance(deps, list):
        errors.append(f"story {sid}: dependsOn is not an array")
    else:
        for d in deps:
            if d not in id_set:
                errors.append(f"story {sid}: dependsOn references unknown id {d!r}")

fis_seen = {}
for s in stories:
    fis = s.get("fis")
    if fis is None:
        continue
    sid = s.get("id", "?")
    expected = canonical_fis_name(s)
    if not isinstance(fis, str):
        errors.append(f"story {sid}: fis is not a string or null")
        continue
    if fis in fis_seen:
        errors.append(f"duplicate fis path {fis!r} (used by {fis_seen[fis]} and {s.get('id')})")
    fis_seen[fis] = s.get("id")
    if expected is None:
        # An invalid id was already reported by the id loop; only a bad name is new here.
        if isinstance(sid, str) and re.fullmatch(r"S\d{2}", sid):
            errors.append(f"story {sid}: cannot derive canonical FIS basename from id/name")
        continue
    if fis != expected:
        errors.append(
            f"story {sid}: non-canonical fis {fis!r}, expected {expected!r} "
            "(legacy v1 readers may normalize only an exact canonical sibling)"
        )
        continue

    target = os.path.join(plan_dir, fis)
    if os.path.islink(target):
        errors.append(f"story {sid}: FIS target is a symlink: {fis!r}")
        continue
    if not os.path.isfile(target):
        errors.append(f"story {sid}: FIS target is missing or not a regular file: {fis!r}")
        continue
    if os.path.dirname(os.path.realpath(target)) != os.path.realpath(plan_dir):
        errors.append(f"story {sid}: FIS target escapes the plan directory: {fis!r}")
        continue

    plans, story_ids = fis_provenance(target)
    if story_ids != [sid]:
        errors.append(f"story {sid}: FIS Story-ID provenance is {story_ids!r}, expected [{sid!r}]")
    issue_dir = re.fullmatch(r"from-issue-(\d+)", os.path.basename(plan_dir))
    if issue_dir:
        expected_plan = f"github://issue/{issue_dir.group(1)}"
    else:
        root = project_root(plan_dir)
        # AndThen does not require git: without a repo root, accept a Plan
        # value that the plan's absolute path ends with.
        expected_plan = (
            os.path.relpath(path, root).replace(os.sep, "/") if root is not None else None
        )
    if expected_plan is not None:
        if plans != [expected_plan]:
            errors.append(f"story {sid}: FIS Plan provenance is {plans!r}, expected [{expected_plan!r}]")
    elif len(plans) != 1 or not path.replace(os.sep, "/").endswith("/" + plans[0]):
        errors.append(f"story {sid}: FIS Plan provenance is {plans!r}, which does not match the plan path {display_path!r}")

# Digest enforcement was retired in 0.20.0 (see CHANGELOG / plan-schema.md):
# andthen:plan no longer writes metadata.immutableDigest, and legacy 0.19.x
# blocks are ignored on read. A missing digest is therefore valid. We still
# surface a present legacy digest informationally, but never fail on it –
# benign hand edits are an allowed, trusted operation.
metadata = doc.get("metadata")
legacy_digest_note = None
if isinstance(metadata, dict) and metadata.get("immutableDigest") is not None:
    legacy_digest_note = (
        "legacy metadata.immutableDigest present (0.19.x); ignored on read, "
        "will be dropped on next regeneration"
    )

if errors:
    print("FAIL: " + str(len(errors)) + " invariant violation(s)")
    for e in errors:
        print("  - " + e)
    sys.exit(1)

print(f"OK: {display_path} validates against plan-schema.md")
print(f"  schemaVersion: {doc['schemaVersion']}")
print(f"  stories: {len(stories)}")
if "metadata" in doc:
    print("  legacy metadata: ignored")
if legacy_digest_note is not None:
    print(f"  note: {legacy_digest_note}")
PY
