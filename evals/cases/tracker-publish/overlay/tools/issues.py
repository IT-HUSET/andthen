#!/usr/bin/env python3
"""A small local issue tracker over one JSON file beside this script.

    issues.py fetch <N>
    issues.py list [--state open|closed|all] [--search <phrase>]
    issues.py create --title <title> --body-file <file>
    issues.py edit <N> --body-file <file>
    issues.py comment <N> --body-file <file>
    issues.py label add|remove <N> <label>
    issues.py close <N>
    issues.py checkpoint

Every command prints JSON on stdout and exits 0, or prints one line on stderr and
exits 1 (argparse usage errors exit 2); `list` includes each issue's body. `--search` takes one exact phrase: an issue matches when its body
contains the phrase as a contiguous, case-insensitive substring. A surrounding
pair of double quotes and an `in:body` qualifier are accepted and ignored.
`checkpoint` writes a marker into the activity log and nothing else.

Python 3.9+, standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

STORE = Path(__file__).resolve().with_name("issues.json")
QUALIFIER = re.compile(r"(?:^|\s)in:(?:body|title|comments)\b")


class Failure(Exception):
    pass


def load():
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Failure("cannot read %s: %s" % (STORE.name, exc))


def save(store):
    STORE.write_text(json.dumps(store, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find(store, number):
    for issue in store["issues"]:
        if issue["number"] == number:
            return issue
    raise Failure("no issue #%d" % number)


def number_arg(text):
    try:
        return int(text.lstrip("#"))
    except ValueError:
        raise Failure("not an issue number: %r" % text)


def read_body(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Failure("cannot read %s as UTF-8: %s" % (path, exc))


def summary(issue):
    return {"number": issue["number"], "title": issue["title"],
            "state": issue["state"], "labels": issue["labels"]}


def phrase(query):
    text = QUALIFIER.sub(" ", query).strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    if not text:
        raise Failure("--search needs a non-empty phrase")
    return text.lower()


def run(args):
    store = load()
    log = store["log"]
    if args.command == "fetch":
        return find(store, number_arg(args.number))
    if args.command == "list":
        wanted = phrase(args.search) if args.search else None
        return [dict(summary(i), body=i["body"]) for i in store["issues"]
                if args.state in ("all", i["state"])
                and (wanted is None or wanted in i["body"].lower())]
    if args.command == "checkpoint":
        log.append({"op": "checkpoint"})
        save(store)
        return {"checkpoint": len(log)}
    if args.command == "create":
        issue = {"number": store["next"], "title": args.title, "body": read_body(args.body_file),
                 "state": "open", "labels": [], "comments": []}
        store["next"] += 1
        store["issues"].append(issue)
        log.append({"op": "create", "number": issue["number"]})
        save(store)
        return {"number": issue["number"], "title": issue["title"], "url": "local:%d" % issue["number"]}
    issue = find(store, number_arg(args.number))
    if args.command == "edit":
        issue["body"] = read_body(args.body_file)
    elif args.command == "comment":
        issue["comments"].append(read_body(args.body_file))
    elif args.command == "label":
        if args.action == "add" and args.label not in issue["labels"]:
            issue["labels"].append(args.label)
        elif args.action == "remove":
            issue["labels"] = [l for l in issue["labels"] if l != args.label]
    elif args.command == "close":
        issue["state"] = "closed"
    log.append({"op": args.command, "number": issue["number"]})
    save(store)
    return summary(issue)


def parser():
    top = argparse.ArgumentParser(prog="issues.py")
    sub = top.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch").add_argument("number")
    lister = sub.add_parser("list")
    lister.add_argument("--state", choices=("open", "closed", "all"), default="open")
    lister.add_argument("--search")
    creator = sub.add_parser("create")
    creator.add_argument("--title", required=True)
    creator.add_argument("--body-file", required=True)
    for name in ("edit", "comment"):
        sp = sub.add_parser(name)
        sp.add_argument("number")
        sp.add_argument("--body-file", required=True)
    labeller = sub.add_parser("label")
    labeller.add_argument("action", choices=("add", "remove"))
    labeller.add_argument("number")
    labeller.add_argument("label")
    sub.add_parser("close").add_argument("number")
    sub.add_parser("checkpoint")
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = run(args)
    except Failure as exc:
        sys.stderr.write("issues.py: %s\n" % exc)
        return 1
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
