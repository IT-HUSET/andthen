#!/usr/bin/env python3
"""Assemble the tracker payloads a plan.json projects into.

Payload assembly only - this script never calls a network. For the live path it
can materialize deterministic body files under a caller-selected directory;
dry runs omit that option and remain read-only.
The skill sends the same payloads through the Issue Tracker document's
operation table; `--dry-run` is where the skill stops after printing them.
"""

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

PLAN_SCHEMA_VERSION = "2"
# Invocation namespace for user-facing skill mentions. The loose-skill installer
# rewrites this one assignment line to the exported prefix. The machine marker
# below keeps its literal `andthen:tracker` token - it is a storage identifier
# matched on read, not an invocation.
SKILL_NS = "andthen:"


def load_plan(path):
    with pathlib.Path(path).open(encoding="utf-8") as handle:
        plan = json.load(handle)
    version = plan.get("schemaVersion") if isinstance(plan, dict) else None
    if version != PLAN_SCHEMA_VERSION:
        sys.exit(f"BLOCKED: unsupported plan.json schemaVersion {version!r}; "
                 f"re-run the {SKILL_NS}plan skill to regenerate")
    return plan


def load_existing(path):
    """Issues already in the tracker, as `gh issue list --json number,body` emits."""
    if not path:
        return []
    with pathlib.Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def canonical_plan_path(path, repo_root=None):
    """Return the plan's stable repository-relative POSIX identity."""
    plan = pathlib.Path(path).resolve()
    if repo_root is None:
        try:
            result = subprocess.run(
                ["git", "-C", str(plan.parent), "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            sys.exit(f"BLOCKED: plan is not inside a Git repository: {plan}")
        repo_root = result.stdout.strip()
    root = pathlib.Path(repo_root).resolve()
    try:
        return plan.relative_to(root).as_posix()
    except ValueError:
        sys.exit(f"BLOCKED: plan is outside repository root {root}: {plan}")


def machine_marker(plan_path, story_id=None):
    suffix = f" story={story_id}" if story_id else ""
    return f"<!-- andthen:tracker plan={plan_path}{suffix} -->"


def resolve(existing, marker):
    """Create, or update the sole issue carrying this exact machine marker."""
    matches = [issue for issue in existing
               if marker in (issue.get("body") or "").splitlines()]
    if len(matches) > 1:
        numbers = ", ".join(f"#{issue.get('number')}" for issue in matches)
        sys.exit(f"BLOCKED: multiple tracker issues match {marker}: {numbers}")
    if matches:
        return {"action": "update", "number": matches[0].get("number")}
    return {"action": "create", "number": None}


def checklist(plan):
    lines = []
    for story in plan.get("stories", []):
        box = "x" if story.get("status") in ("done", "skipped") else " "
        lines.append(f"- [{box}] {story['id']} - {story['name']}")
    return lines


def parent_payload(plan, plan_path, existing):
    marker = machine_marker(plan_path)
    body = [plan.get("overview", {}).get("summary", ""), ""]
    prd = plan.get("prd")
    if prd:
        body += [f"PRD: {prd}", ""]
    body += ["## Stories", ""] + checklist(plan) + ["", marker]
    payload = {
        "kind": "parent",
        "title": f"Plan: {pathlib.PurePosixPath(plan_path).parent.name or plan_path}",
        "body": "\n".join(body),
        "search": marker,
    }
    payload.update(resolve(existing, marker))
    return payload


def child_payload(story, plan, plan_path, sha, existing):
    marker = machine_marker(plan_path, story["id"])
    plan_dir = pathlib.PurePosixPath(plan_path).parent
    body = [story.get("scope", ""), ""]
    for ref in story.get("sourceRefs") or []:
        body.append(f"PRD: {ref}")
    if story.get("fis"):
        body.append(f"FIS: {plan_dir / story['fis']}@{sha}")
    if story.get("dependsOn"):
        body.append(f"Blocked by: {', '.join(story['dependsOn'])}")
    if story.get("completedTaskIds"):
        body.append(f"Completed tasks: {', '.join(story['completedTaskIds'])}")
    body += ["", marker]
    payload = {
        "kind": "story",
        "id": story["id"],
        "title": f"{story['id']} - {story['name']}",
        "assignee": story.get("owner"),
        "dependsOn": story.get("dependsOn") or [],
        "body": "\n".join(body),
        "search": marker,
    }
    payload.update(resolve(existing, marker))
    return payload


def publish(plan, plan_path, sha, existing):
    return {
        "verb": "publish",
        "plan": plan_path,
        "parent": parent_payload(plan, plan_path, existing),
        "children": [child_payload(s, plan, plan_path, sha, existing)
                     for s in plan.get("stories", [])],
    }


def materialize_bodies(payload, body_dir):
    """Write stable live-transport files and add their paths to the payload."""
    identity = hashlib.sha256(payload["plan"].encode("utf-8")).hexdigest()[:12]
    target = pathlib.Path(body_dir) / identity
    target.mkdir(parents=True, exist_ok=True)
    rows = [payload["parent"], *payload["children"]]
    for index, row in enumerate(rows):
        name = "parent.md" if row["kind"] == "parent" else f"story-{index:03}.md"
        path = target / name
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(row["body"])
        row["body_file"] = str(path.resolve())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verb", choices=("publish",))
    parser.add_argument("plan", help="path to plan.json")
    parser.add_argument("--sha", default="HEAD",
                        help="commit the FIS links pin to (default: HEAD)")
    parser.add_argument("--existing", metavar="PATH",
                        help="JSON array of issues already in the tracker "
                             "(number, body) - matched on the back-reference so a "
                             "re-run updates instead of duplicating")
    parser.add_argument("--body-dir", metavar="PATH",
                        help="materialize deterministic publish body files here "
                             "for argv-safe live transport")
    parser.add_argument("--dry-run", action="store_true",
                        help="assemble without materializing body files")
    args = parser.parse_args(argv)

    # Story names carry en dashes; a redirected Windows stdout defaults to cp1252.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    plan_path = canonical_plan_path(args.plan)
    plan = load_plan(args.plan)
    existing = load_existing(args.existing)
    out = publish(plan, plan_path, args.sha, existing)
    if args.body_dir and not args.dry_run:
        materialize_bodies(out, args.body_dir)
    if args.dry_run and args.existing is None:
        # Create-versus-update is what the tracker lookup decides, and a dry
        # run makes no tracker call: saying `create` here would be a guess.
        for row in [out["parent"], *out["children"]]:
            row.update(action="unknown", number=None)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
