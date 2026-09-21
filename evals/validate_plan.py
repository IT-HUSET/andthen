"""Schema-only `plan.json` validator for eval checks.

`ops.py` is gone (ADR-003, ADR-013): the skill that writes a plan checks its own
candidate against `plan.schema.json` now, so a case's `check.json` needs its own
way to fail on a malformed plan. This lifts the minimal `validate_instance`
walker from `ops.py` (see `git show ea80fe3^:plugin/skills/ops/scripts/ops.py`)
rather than adding a jsonschema dependency the repo does not otherwise need.
It checks shape, plus the one invariant JSON Schema cannot state - story ids
unique within the plan - which is enough to catch a plan a run corrupted.

    python3 evals/validate_plan.py <path-to-plan.json>

Exit 0 and `OK: ...` on a valid plan, exit 1 and one `ERROR: ...` line per
violation otherwise.
"""

import json
import re
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "plugin" / "references" / "plan.schema.json"

KNOWN_KEYWORDS = {"$schema", "$id", "title", "description", "$defs", "$ref", "type",
                  "enum", "const", "required", "properties", "additionalProperties",
                  "items", "minItems", "maxItems", "minLength", "minimum", "pattern",
                  "uniqueItems", "if", "then", "else"}
JSON_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool,
              "integer": int, "null": type(None)}


def json_type_ok(value, name):
    # bool is an int in Python; JSON Schema keeps them apart.
    if name == "integer" and isinstance(value, bool):
        return False
    return isinstance(value, JSON_TYPES[name])


def validate_instance(value, schema, root, where, errors):
    unknown = set(schema) - KNOWN_KEYWORDS
    if unknown:
        errors.append(f"{root.get('$id', 'schema')} uses unsupported keyword(s) {sorted(unknown)}")
        return
    if "if" in schema:
        probe = []
        validate_instance(value, schema["if"], root, where, probe)
        branch = schema.get("then") if not probe else schema.get("else")
        if branch is not None:
            validate_instance(value, branch, root, where, errors)
    if "$ref" in schema:
        target = root
        for step in schema["$ref"].lstrip("#/").split("/"):
            target = target[step]
        return validate_instance(value, target, root, where, errors)
    if "const" in schema and value != schema["const"]:
        errors.append(f"{where}: is {value!r}, expected {schema['const']!r}")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: is {value!r}, expected one of {schema['enum']}")
        return
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(json_type_ok(value, n) for n in names):
            errors.append(f"{where}: is {type(value).__name__}, expected {'/'.join(names)}")
            return
    if schema.get("uniqueItems") is True and isinstance(value, list):
        rendered = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
        if len(rendered) != len(set(rendered)):
            errors.append(f"{where}: contains duplicate items")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{where}: is {value!r}, below the minimum {schema['minimum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{where}: is shorter than {schema['minLength']} character(s)")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{where}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{where}: has {len(value)} item(s), needs {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{where}: has {len(value)} item(s), allows {schema['maxItems']}")
        for i, item in enumerate(value):
            if "items" in schema:
                validate_instance(item, schema["items"], root, f"{where}[{i}]", errors)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{where}: missing required field {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(props))
            if extra:
                errors.append(f"{where}: unknown field(s) {extra}")
        for key, sub in props.items():
            if key in value:
                validate_instance(value[key], sub, root, f"{where}.{key}", errors)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.stderr.write("usage: python3 evals/validate_plan.py <path-to-plan.json>\n")
        return 2
    path = Path(argv[0])
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"ERROR: {path} - cannot read or parse - {exc}\n")
        return 1
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = []
    validate_instance(doc, schema, schema, "plan", errors)
    stories = doc.get("stories") if isinstance(doc, dict) else None
    ids = [story.get("id") for story in stories if isinstance(story, dict)] if isinstance(stories, list) else []
    duplicates = sorted({str(i) for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append(f"plan.stories: duplicate story id(s) {duplicates} - the row a lookup resolves to is arbitrary")
    for error in errors:
        sys.stderr.write(f"ERROR: {path} - {error}\n")
    if errors:
        return 1
    print(f"OK: {path} validates against {SCHEMA_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
