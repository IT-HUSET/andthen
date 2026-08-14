#!/usr/bin/env bash
#
# validate-architecture-model.sh – schema invariant validator for the atlas
# model artifacts (architecture-model.json / domain-model.json)
#
# Checks a model against the machine-checkable invariants in
# plugin/references/architecture-model.md:
#   - parses as JSON
#   - schemaVersion === "1" and kind === "architecture-model" or
#     "domain-model" (the discriminator consumers key on first)
#   - required keys per collection: meta (project, generatedBy, date), contexts[]
#     (>= 1), nodes[] (>= 1), edges[] (present, may be empty), tours[] optional
#   - meta.date matches YYYY-MM-DD
#   - ids are non-empty strings, unique within each collection
#   - contextId / edge from+to / tour-step targets resolve to existing ids;
#     each tour step carries exactly one non-null nodeId|contextId
#   - nodes[].ref is repo-relative: no leading '/', no '~', no '://', and does
#     not escape the repo (normalized path must not start with '..')
#   - enum membership for context kind/evidence, node kind (branched on the
#     document kind), edge kind/evidence
#   - metrics carry only the five documented keys, as non-negative integers
#   - edge weight is a positive integer when present; string fields (names,
#     summaries, labels, notes) are strings
#   - domain-model only: edges MUST be []; node avoid, when present, is a
#     non-empty array of non-empty strings; node meanings, when present, has
#     >= 2 entries with distinct contextIds each resolving to contexts[].id
#     and non-empty label/meaning strings
#
# Parity contract: this check set is identical to the one the atlas renderer
# (plugin/skills/visualize/scripts/render-atlas.mjs) enforces before drawing.
# A model that passes here must render, and one that fails here must not –
# divergence between the two would let an invalid model reach the renderer or
# a valid one be refused. Change both together.
#
# Out of scope (intentionally not checked here): byte-level formatting, key
# order, unknown keys outside metrics, id casing, and semantic quality such as
# node-count altitude or evidence honesty. Those belong to the producer skill,
# not this structural gate.
#
# Usage: scripts/validate-architecture-model.sh <path-to-model.json>
# Exit:  0 = all invariants hold; 1 = at least one violation; 2 = bad usage / unreadable input.
#
set -o pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <path-to-model.json>" >&2
  exit 2
fi

MODEL_PATH="$1"

if [[ ! -r "$MODEL_PATH" ]]; then
  echo "error: cannot read $MODEL_PATH" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required but not found on PATH" >&2
  exit 2
fi

python3 - "$MODEL_PATH" <<'PY'
import json
import posixpath
import re
import sys

DOC_KIND_ENUM = {"architecture-model", "domain-model"}
CONTEXT_KIND_ENUM = {"bounded-context", "layer", "subsystem", "external"}
CONTEXT_EVIDENCE_ENUM = {"declared", "inferred"}
NODE_KIND_ENUM = {"module", "package", "service", "component", "store", "entrypoint", "external"}
DOMAIN_NODE_KIND_ENUM = {"entity", "action", "state", "policy"}
EDGE_KIND_ENUM = {"depends", "calls", "publishes", "consumes", "reads", "writes"}
EDGE_EVIDENCE_ENUM = {"imports", "declared", "git-coupling", "inferred"}
METRIC_KEYS = ("files", "loc", "churn", "fanIn", "fanOut")
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

def check_string(obj, key, label, required, non_empty=True):
    """Type-check a string field. Returns the value when usable, else None.

    Explicit null is a type error, never treated as absence – parity with the
    renderer's isStr/isOptStr semantics (omission is the only way to skip a key).
    """
    if key not in obj:
        if required:
            errors.append(f"{label}: missing required key '{key}'")
        return None
    value = obj[key]
    if not isinstance(value, str):
        errors.append(f"{label}: {key} must be a string, got {type(value).__name__}")
        return None
    if non_empty and not value.strip():
        errors.append(f"{label}: {key} must be a non-empty string")
        return None
    return value

def check_enum(obj, key, allowed, label):
    value = check_string(obj, key, label, required=True)
    if value is not None and value not in allowed:
        errors.append(f"{label}: invalid {key} {value!r} (must be one of {sorted(allowed)})")

def check_collection(doc, key, minimum):
    """Return the collection as a list of objects, or None when unusable."""
    value = doc.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}[] is missing or not an array")
        return None
    if len(value) < minimum:
        errors.append(f"{key}[] must contain at least {minimum} entr{'y' if minimum == 1 else 'ies'}")
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{key}[{i}]: expected an object, got {type(item).__name__}")
    return [item for item in value if isinstance(item, dict)]

def collect_ids(items, label):
    """Return the set of usable ids, reporting duplicates and bad id values."""
    ids = set()
    for i, item in enumerate(items):
        value = check_string(item, "id", f"{label}[{i}]", required=True)
        if value is None:
            continue
        if value in ids:
            errors.append(f"duplicate id in {label}[]: {value!r}")
        ids.add(value)
    return ids

def check_ref(node, label):
    value = check_string(node, "ref", label, required=True)
    if value is None:
        return
    path = value.split("#", 1)[0]
    normalized = posixpath.normpath(path)
    if value.startswith("/"):
        errors.append(f"{label}: ref {value!r} is an absolute path (must be repo-relative)")
    elif "://" in value:
        errors.append(f"{label}: ref {value!r} is a URL (must be a repo-relative path)")
    elif value.startswith("~"):
        errors.append(f"{label}: ref {value!r} is home-relative (must be repo-relative)")
    elif normalized == ".." or normalized.startswith("../"):
        errors.append(f"{label}: ref {value!r} escapes the repository root")

def check_metrics(node, label):
    if "metrics" not in node:
        return
    metrics = node["metrics"]
    if not isinstance(metrics, dict):
        errors.append(f"{label}: metrics must be an object, got {type(metrics).__name__}")
        return
    unknown = [k for k in metrics if k not in METRIC_KEYS]
    if unknown:
        errors.append(f"{label}: unknown metrics key(s) {sorted(unknown)} (allowed: {list(METRIC_KEYS)})")
    for key in METRIC_KEYS:
        if key not in metrics:
            continue
        value = metrics[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errors.append(f"{label}: metrics.{key} is {value!r} (must be a non-negative integer)")

def check_avoid(node, label):
    if "avoid" not in node:
        return
    avoid = node["avoid"]
    if not isinstance(avoid, list) or not avoid:
        errors.append(f"{label}: avoid must be a non-empty array when present (omit the key instead of [])")
        return
    for j, entry in enumerate(avoid):
        if not isinstance(entry, str) or not entry.strip():
            errors.append(f"{label}: avoid[{j}] must be a non-empty string, got {entry!r}")

def check_meanings(node, label, context_ids):
    if "meanings" not in node:
        return
    meanings = node["meanings"]
    if not isinstance(meanings, list):
        errors.append(f"{label}: meanings must be an array when present")
        return
    if len(meanings) < 2:
        errors.append(f"{label}: meanings must have at least 2 entries, found {len(meanings)}")
    seen_contexts = set()
    for j, entry in enumerate(meanings):
        at = f"{label} meanings[{j}]"
        if not isinstance(entry, dict):
            errors.append(f"{at}: expected an object, got {type(entry).__name__}")
            continue
        check_string(entry, "label", at, required=True)
        check_string(entry, "meaning", at, required=True)
        context_id = check_string(entry, "contextId", at, required=True)
        if context_id is None:
            continue
        if context_id not in context_ids:
            errors.append(f"{at}: contextId references unknown context {context_id!r}")
        if context_id in seen_contexts:
            errors.append(f"{at}: duplicate meanings contextId {context_id!r} (contextIds must be distinct)")
        seen_contexts.add(context_id)

display_path = sys.argv[1]
with open(display_path, "rb") as f:
    raw = f.read()
try:
    doc = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"FAIL: malformed JSON: {e}")
    sys.exit(1)

if not isinstance(doc, dict):
    print("FAIL: top-level value is not an object")
    sys.exit(1)

errors = []

doc_kind = doc.get("kind")
if doc_kind not in DOC_KIND_ENUM:
    errors.append(f"kind is {doc_kind!r}, expected \"architecture-model\" or \"domain-model\"")
is_domain = doc_kind == "domain-model"
node_kind_enum = DOMAIN_NODE_KIND_ENUM if is_domain else NODE_KIND_ENUM
if doc.get("schemaVersion") != "1":
    errors.append(f"schemaVersion is {doc.get('schemaVersion')!r}, expected \"1\"")

meta = doc.get("meta")
if not isinstance(meta, dict):
    errors.append("meta is missing or not an object")
else:
    check_string(meta, "project", "meta", required=True)
    check_string(meta, "generatedBy", "meta", required=True)
    check_string(meta, "revision", "meta", required=False)
    check_string(meta, "summary", "meta", required=False, non_empty=False)
    date = check_string(meta, "date", "meta", required=True)
    if date is not None and not DATE_RE.fullmatch(date):
        errors.append(f"meta: date {date!r} is not in YYYY-MM-DD form")

contexts = check_collection(doc, "contexts", 1)
nodes = check_collection(doc, "nodes", 1)
edges = check_collection(doc, "edges", 0)
tours = [] if "tours" not in doc else check_collection(doc, "tours", 0)
if contexts is None or nodes is None or edges is None or tours is None:
    print("FAIL: " + str(len(errors)) + " invariant violation(s)")
    for e in errors:
        print("  - " + e)
    sys.exit(1)

context_ids = collect_ids(contexts, "contexts")
node_ids = collect_ids(nodes, "nodes")
collect_ids(tours, "tours")

for i, ctx in enumerate(contexts):
    label = f"contexts[{i}]"
    check_string(ctx, "name", label, required=True)
    check_string(ctx, "summary", label, required=True)
    check_enum(ctx, "kind", CONTEXT_KIND_ENUM, label)
    check_enum(ctx, "evidence", CONTEXT_EVIDENCE_ENUM, label)

for i, node in enumerate(nodes):
    label = f"node {node['id']!r}" if isinstance(node.get("id"), str) else f"nodes[{i}]"
    check_string(node, "name", label, required=True)
    check_string(node, "summary", label, required=False, non_empty=False)
    check_enum(node, "kind", node_kind_enum, label)
    check_ref(node, label)
    check_metrics(node, label)
    context_id = check_string(node, "contextId", label, required=True)
    if context_id is not None and context_id not in context_ids:
        errors.append(f"{label}: contextId references unknown context {context_id!r}")
    if is_domain:
        check_avoid(node, label)
        check_meanings(node, label, context_ids)

if is_domain and edges:
    errors.append(f"edges[] must be empty for a domain-model (found {len(edges)} entr{'y' if len(edges) == 1 else 'ies'})")

for i, edge in enumerate(edges):
    label = f"edges[{i}]"
    check_enum(edge, "kind", EDGE_KIND_ENUM, label)
    check_enum(edge, "evidence", EDGE_EVIDENCE_ENUM, label)
    check_string(edge, "label", label, required=False, non_empty=False)
    if "weight" in edge:
        weight = edge["weight"]
        if isinstance(weight, bool) or not isinstance(weight, int) or weight < 1:
            errors.append(f"{label}: weight is {weight!r} (must be a positive integer)")
    for end in ("from", "to"):
        value = check_string(edge, end, label, required=True)
        if value is not None and value not in node_ids:
            errors.append(f"{label}: {end} references unknown node {value!r}")

for i, tour in enumerate(tours):
    label = f"tour {tour['id']!r}" if isinstance(tour.get("id"), str) else f"tours[{i}]"
    check_string(tour, "title", label, required=True)
    steps = tour.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{label}: steps must be a non-empty array")
        continue
    for j, step in enumerate(steps):
        step_label = f"{label} step[{j}]"
        if not isinstance(step, dict):
            errors.append(f"{step_label}: expected an object, got {type(step).__name__}")
            continue
        check_string(step, "note", step_label, required=True)
        targets = [k for k in ("nodeId", "contextId") if step.get(k) is not None]
        if len(targets) != 1:
            errors.append(f"{step_label}: needs exactly one of nodeId/contextId, found {targets}")
            continue
        target = targets[0]
        value = check_string(step, target, step_label, required=True)
        if value is None:
            continue
        known = node_ids if target == "nodeId" else context_ids
        if value not in known:
            errors.append(f"{step_label}: {target} references unknown id {value!r}")

if errors:
    print("FAIL: " + str(len(errors)) + " invariant violation(s)")
    for e in errors:
        print("  - " + e)
    sys.exit(1)

print(f"OK: {display_path} validates against architecture-model.md")
print(f"  schemaVersion: {doc['schemaVersion']}")
print(f"  contexts: {len(contexts)}")
print(f"  nodes: {len(nodes)}")
print(f"  edges: {len(edges)}")
print(f"  tours: {len(tours)}")
PY
