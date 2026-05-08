#!/usr/bin/env bash
#
# validate-plan-json.sh — schema invariant + digest validator for plan.json
#
# Checks a plan.json file against this machine-checkable subset of the
# invariants in plugin/references/plan-schema.md:
#   - schemaVersion === "1"
#   - stories[].id present and unique
#   - stories[].status in {pending, spec-ready, in-progress, done, skipped, blocked}
#   - every dependsOn[] element matches some stories[].id
#   - stories[].fis paths unique (non-null only — multiple null values are valid)
#   - metadata.immutableDigest matches the recomputed canonical-form digest
#   - top-level and per-story keys are within the schema-named set
#     (extra unknown keys fail loudly rather than silently propagating into the digest)
#
# Out of scope (intentionally not checked here): per-field type validation,
# enum membership for risk, presence of optional-but-recommended fields, and
# semantic checks (e.g. wave references in stories matching overview.phases[].waves).
# Those are owned by the producer skill, not this drift-regression harness.
#
# Usage: scripts/validate-plan-json.sh <path-to-plan.json>
# Exit:  0 = all invariants hold; 1 = at least one violation; 2 = bad usage / unreadable input.
#
# Implementation note: digest recomputation requires exact byte-level control over
# key order, indent, trailing newline, and Unicode escape policy. Python's json
# module with sort_keys=False, ensure_ascii=False, and manual key ordering is the
# only portable way to match the canonical form pinned in the schema doc.

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
import hashlib
import json
import sys
from collections import OrderedDict

TOP_LEVEL_ORDER = [
    "schemaVersion", "prd", "references", "overview",
    "sharedDecisions", "bindingConstraints", "stories",
    "riskSummary", "executionNotes", "metadata",
]
OVERVIEW_ORDER = ["summary", "phases"]
PHASE_ORDER = ["id", "name", "waves"]
SHARED_DECISION_ORDER = ["title", "description", "stories"]
BINDING_CONSTRAINT_ORDER = ["featureId", "anchor", "verbatim"]
STORY_ORDER = [
    "id", "name", "phase", "wave", "dependsOn", "parallel", "risk",
    "status", "fis", "scope", "sourceRefs", "provenance", "assetRefs", "notes",
]
RISK_SUMMARY_ORDER = ["story", "risk", "mitigation"]
STATUS_ENUM = {"pending", "spec-ready", "in-progress", "done", "skipped", "blocked"}

def order(d, keys):
    if not isinstance(d, dict):
        return d
    out = OrderedDict()
    for k in keys:
        if k in d:
            out[k] = d[k]
    for k, v in d.items():
        if k not in out:
            out[k] = v
    return out

path = sys.argv[1]
with open(path, "rb") as f:
    raw = f.read()
try:
    doc = json.loads(raw, object_pairs_hook=OrderedDict)
except json.JSONDecodeError as e:
    print(f"FAIL: malformed JSON: {e}")
    sys.exit(1)

errors = []

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
    if sid in seen:
        errors.append(f"duplicate story id: {sid!r}")
    seen.add(sid)
    ids.append(sid)

id_set = set(ids)

# Reject unknown top-level keys and unknown story keys — they would silently
# alter the canonical-form digest if propagated.
known_top = set(TOP_LEVEL_ORDER)
extra_top = [k for k in doc.keys() if k not in known_top]
if extra_top:
    errors.append(f"unknown top-level keys: {sorted(extra_top)} (allowed: {sorted(known_top)})")
known_story = set(STORY_ORDER)
for s in stories:
    extra = [k for k in s.keys() if k not in known_story]
    if extra:
        errors.append(f"story {s.get('id', '?')!r}: unknown keys {sorted(extra)} (allowed: {sorted(known_story)})")
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
    if fis in fis_seen:
        errors.append(f"duplicate fis path {fis!r} (used by {fis_seen[fis]} and {s.get('id')})")
    fis_seen[fis] = s.get("id")

# Canonical form: drop metadata, null out stories[].status and stories[].fis,
# enforce schema key order, 2-space indent, trailing newline, no Unicode escape.
canonical = OrderedDict()
for k in TOP_LEVEL_ORDER:
    if k == "metadata" or k not in doc:
        continue
    if k == "stories":
        canonical[k] = []
        for s in doc[k]:
            s2 = OrderedDict(s)
            s2["status"] = None
            s2["fis"] = None
            canonical[k].append(order(s2, STORY_ORDER))
    elif k == "overview":
        ov = order(doc[k], OVERVIEW_ORDER)
        if isinstance(ov.get("phases"), list):
            ov["phases"] = [order(p, PHASE_ORDER) for p in ov["phases"]]
        canonical[k] = ov
    elif k == "sharedDecisions":
        canonical[k] = [order(x, SHARED_DECISION_ORDER) for x in doc[k]]
    elif k == "bindingConstraints":
        canonical[k] = [order(x, BINDING_CONSTRAINT_ORDER) for x in doc[k]]
    elif k == "riskSummary":
        canonical[k] = [order(x, RISK_SUMMARY_ORDER) for x in doc[k]]
    else:
        canonical[k] = doc[k]

serialized = json.dumps(canonical, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
recomputed = "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()

stored = (doc.get("metadata") or {}).get("immutableDigest")
if stored is None:
    errors.append("metadata.immutableDigest is missing")
elif stored != recomputed:
    errors.append(
        f"metadata.immutableDigest mismatch:\n  stored:     {stored}\n  recomputed: {recomputed}"
    )

if errors:
    print("FAIL: " + str(len(errors)) + " invariant violation(s)")
    for e in errors:
        print("  - " + e)
    sys.exit(1)

print(f"OK: {path} validates against plan-schema.md")
print(f"  schemaVersion: {doc['schemaVersion']}")
print(f"  stories: {len(stories)}")
print(f"  digest:  {recomputed}")
PY
