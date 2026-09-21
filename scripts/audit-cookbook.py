#!/usr/bin/env python3
"""Release check: every invocation printed in the user-facing docs
must still exist in the shipped surface.

The docs are the only place a user learns what to type, so a renamed skill or a cut
flag is a broken instruction the moment it ships. Sources: `COOKBOOK.md`,
`README.md`, the plugin README, and `MIGRATING-FROM-0.x.md`.

Per invocation: the skill exists in the plugin dir its sigil names; each `--flag`
appears in that skill's `argument-hint`; each `--mode` value appears in the hint when
the hint enumerates values, otherwise in the skill body (`--mode <mode>[,<mode>...]`
hints name no values).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["COOKBOOK.md", "README.md", "plugin/README.md", "MIGRATING-FROM-0.x.md"]
CALL = re.compile(r"/andthen:([a-z][a-z0-9-]*)")
FLAG = re.compile(r"(?<![\w-])--([a-z][a-z0-9-]*)")


def segments(text):
    """(skill, argument text) per invocation. A segment ends at the next
    invocation on the line or at a trailing `#` comment - both carry no arguments."""
    for line in text.splitlines():
        hits = [(m.start(), m.end(), m.group(1)) for m in CALL.finditer(line)]
        for i, (_, end, skill) in enumerate(hits):
            seg_end = hits[i + 1][0] if i + 1 < len(hits) else len(line)
            seg = line[end:seg_end]
            seg = seg.split("#", 1)[0].split("`", 1)[0]
            # A quoted argument is the user's prose request, not the option surface:
            # `implement-fix "add a --json flag"` names no skill flag.
            seg = re.sub(r'"[^"]*"', " ", seg)
            yield skill, seg


def hint_of(skill_md):
    m = re.search(r'^argument-hint:\s*"(.*)"\s*$', skill_md.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def check(skill, seg, where, misses):
    skill_md = ROOT / "plugin" / "skills" / skill / "SKILL.md"
    if not skill_md.exists():
        misses.append(f"{where}: skill `{skill}` does not exist in plugin/skills/")
        return
    hint = hint_of(skill_md)
    body = skill_md.read_text(encoding="utf-8")
    for flag in dict.fromkeys(FLAG.findall(seg)):
        if f"--{flag}" not in hint:
            misses.append(f"{where}: `{skill} --{flag}` is not in its argument-hint: {hint}")
    m = re.search(r"--mode\s+([a-z][a-z0-9,-]*)", seg)
    if m:
        enumerated = re.search(r"--mode\s+([a-z<][a-z0-9|,<>.\[\]-]*)", hint)
        listed = enumerated.group(1) if enumerated else ""
        for value in m.group(1).split(","):
            if value in listed:
                continue
            if "<mode>" in listed and re.search(rf"\b{re.escape(value)}\b", body):
                continue
            misses.append(f"{where}: `{skill} --mode {value}` is named in neither "
                          f"the argument-hint nor the skill body")


def main():
    misses = []
    seen = set()
    for doc in DOCS:
        path = ROOT / doc
        if not path.exists():
            misses.append(f"{doc}: missing")
            continue
        for skill, seg in segments(path.read_text(encoding="utf-8")):
            key = (doc, skill, seg.strip())
            if key in seen:
                continue
            seen.add(key)
            check(skill, seg, f"{doc}: /andthen:{skill}", misses)
    if misses:
        print(f"FAIL: {len(misses)} cookbook/README invocation(s) do not match the shipped surface")
        for m in dict.fromkeys(misses):
            print(f"  {m}")
        return 1
    print(f"PASS: {len(seen)} invocations across {len(DOCS)} documents resolve "
          f"to a shipped skill, flag, and mode")
    return 0


if __name__ == "__main__":
    sys.exit(main())
