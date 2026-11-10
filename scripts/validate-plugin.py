#!/usr/bin/env python3
"""Content check for the shipped plugin: the install-clean contract CI and the
fast test tier run. Exits 0 when every check passes, 1 otherwise, printing one
`error:` line per violation.

Checks: retired path tokens, SKILL.md path shape, sigil-free references,
reference depth, canonical asset existence, role-template parity across the
three hosts, skill-asset declaration closure, and canonical mentions. The
canonical-asset tables and the two checks the loose-skill installer also runs
live in scripts/andthen_loose.py and are imported here, not copied.

Stdlib only, Python 3.9+.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from andthen_loose import (  # noqa: E402
    CANONICAL_ASSETS, CANONICAL_LOAD, CANONICAL_PREFIX, REFERENCES_ROOT, REPO_ROOT, SKILLS_ROOT,
    _check_canonical_assets, _check_skill_asset_closure, _each_source_skill, err, files_below,
    lines_of, markdown_files, read_text)

PLUGIN_ROOTS = (REPO_ROOT / "plugin",)

SOURCE_ROOTS = (SKILLS_ROOT, REFERENCES_ROOT)

# The two Claude Code path variables, retired: both hosts announce the skill
# root, Codex never substituted either token, and a literal token in skill text
# costs the model a filesystem search per invocation.
RETIRED_TOKEN = re.compile(r"CLAUDE_PLUGIN_ROOT|CLAUDE_SKILL_DIR")
SIGIL_REF = re.compile(r"/andthen:|\$andthen")


def _first_match_per_file(pattern, roots):
    """(path, line number, line) for the first match in each file under roots.

    Build artifacts are skipped for the same reason the loose installer drops
    them from an install: compiled bytecode belongs to whoever ran the source
    tree, and grepping it reports a stale copy of text that is no longer there."""
    hits = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in files_below(root):
            if path.suffix == ".pyc" or "__pycache__" in path.parts:
                continue
            try:
                text = read_text(path)
            except OSError:
                continue
            for number, line in enumerate(lines_of(text), 1):
                if pattern.search(line):
                    hits.append((path, number, line))
                    break
    return hits


def _validate_no_retired_tokens():
    """Shipped content names no host path variable: a canonical loads as
    ../../references/<asset>.md and a bundled script runs as
    <skill-dir>/scripts/<name>, both resolved from the root each host announces."""
    hits = _first_match_per_file(RETIRED_TOKEN, PLUGIN_ROOTS)
    for path, number, line in hits:
        err("error: %s:%d:%s names a retired CLAUDE_PLUGIN_ROOT/CLAUDE_SKILL_DIR token;"
            " load a canonical as %s<asset>.md and run a bundled script as"
            " <skill-dir>/scripts/<name>" % (path, number, line, CANONICAL_PREFIX))
    return not hits


# A relative path climbing out of the skill directory. The lookbehind keeps the
# match anchored at the first `..` of a chain rather than mid-path.
DOTDOT_PATH = re.compile(r"(?<![A-Za-z0-9._/-])\.\./[A-Za-z0-9._/-]*")


def _validate_skill_md_paths():
    """A SKILL.md path resolves from the announced skill root, so the only thing
    above that root a skill may name is its own plugin's canonicals. Any other
    `..` path points outside the bundle, where the installed copy has nothing."""
    ok = True
    for skill_dir, _skill in _each_source_skill():
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        for number, line in enumerate(lines_of(read_text(skill_md)), 1):
            for match in DOTDOT_PATH.finditer(line):
                token = match.group(0)
                if (token.startswith(CANONICAL_PREFIX)
                        and token[len(CANONICAL_PREFIX):] in CANONICAL_ASSETS):
                    continue
                err("error: %s:%d:%s climbs out of the skill root; the one allowed"
                    " shape is %s<canonical>.md"
                    % (skill_md, number, token, CANONICAL_PREFIX))
                ok = False
    return ok


def _validate_no_sigil_refs():
    """Shipped prose references skills as `the andthen:<name> skill` - never a
    host-specific invocation sigil (`/andthen:<x>` is Claude slash-command
    syntax, `$andthen-<x>` is Codex mention syntax). A sigil baked into an
    installed bundle renders as the wrong syntax on every other host."""
    hits = _first_match_per_file(SIGIL_REF, SOURCE_ROOTS)
    for path, number, line in hits:
        err("error: %s:%d:%s uses a sigil skill reference (/andthen: or $andthen);"
            " shipped prose must use the sigil-free form `the andthen:<name> skill`"
            % (path, number, line))
    return not hits


MARKDOWN_LINK = re.compile(r"\]\(([^)]*)\)")
RELATIVE_REF_TOKEN = re.compile(r"(^|[^A-Za-z0-9._/-])(\.\.?/|references/)[A-Za-z0-9._/-]*\.md")


def _validate_reference_depth():
    """One level deep: no file in a skill other than SKILL.md may link or path to
    another file. A chain SKILL.md -> A.md -> B.md hides B behind a partial read
    of A, so the skill body names each load site's whole read-set instead. A
    bare filename in prose - no link, no path - is a mention and stays allowed."""
    report = []
    candidates = []
    for skill_dir, _skill in _each_source_skill():
        candidates.extend(p for p in markdown_files(skill_dir) if p.name != "SKILL.md")
    for path in sorted(candidates, key=str):
        seen = set()
        for number, line in enumerate(lines_of(read_text(path)), 1):
            tokens = [match.group(1) for match in MARKDOWN_LINK.finditer(line)]
            tokens.extend(re.sub(r"^[^A-Za-z0-9._/-]", "", match.group(0))
                          for match in RELATIVE_REF_TOKEN.finditer(line))
            for token in tokens:
                token = token.split("#", 1)[0]
                if not token.endswith(".md") or "://" in token:
                    continue
                if (number, token) in seen:
                    continue
                seen.add((number, token))
                directory = token.rsplit("/", 1)[0] if "/" in token else ""
                if directory in ("", ".") or directory.endswith("references"):
                    report.append(
                        "error: %s:%d points at reference %s; a file other than SKILL.md paths"
                        " to no other file - name the whole read-set in the skill body"
                        " that loads it" % (path, number, token))
    for line in report:
        err(line)
    return not report


def _role_body_markdown(path):
    """A Markdown agent template's prompt (Claude, Copilot): everything after
    the frontmatter fences."""
    fences = 0
    body = []
    for line in lines_of(read_text(path)):
        if line == "---":
            fences += 1
            continue
        if fences >= 2:
            body.append(line)
    return _role_body_text(body)


def _role_body_codex(path):
    """The same prompt in Codex form: the developer_instructions heredoc."""
    body = []
    inside = False
    for line in lines_of(read_text(path)):
        if not inside:
            if line == 'developer_instructions = """':
                inside = True
            continue
        if line == '"""':
            break
        body.append(line)
    return _role_body_text(body)


def _role_body_text(body):
    while body and body[0] == "":
        body.pop(0)
    return "\n".join(body).rstrip("\n")


def _check_role_template_parity():
    """Each optional role agent ships in three host formats, and only the
    frontmatter differs by contract. A body that drifts ships two personas under
    one role name."""
    templates = REPO_ROOT / "plugin" / "skills" / "init" / "templates" / "agents"
    if not (templates / "claude").is_dir():
        return True
    ok = True
    for claude_template in sorted((templates / "claude").glob("*.md")):
        if not claude_template.is_file():
            continue
        role = claude_template.stem
        codex_template = templates / "codex" / (role + ".toml")
        if not codex_template.is_file():
            err("error: role %s has no Codex template at %s" % (role, codex_template))
            ok = False
            continue
        if _role_body_markdown(claude_template) != _role_body_codex(codex_template):
            err("error: role %s body differs between its Claude and Codex templates;"
                " the two hosts ship one persona" % role)
            ok = False
        copilot_template = templates / "copilot" / (role + ".agent.md")
        if not copilot_template.is_file():
            err("error: role %s has no Copilot template at %s" % (role, copilot_template))
            ok = False
        elif _role_body_markdown(claude_template) != _role_body_markdown(copilot_template):
            err("error: role %s body differs between its Claude and Copilot templates;"
                " the hosts ship one persona" % role)
            ok = False
    return ok


BACKTICKED_FILENAME = re.compile(r"`([A-Za-z0-9._-]+\.(?:md|json))`")


def _check_canonical_mentions():
    """A bare backticked filename is a mention, not a load, so a SKILL.md that
    names a canonical that way without loading it by path points at a file the
    model never reads. Legal only beside the skill's own load of that canonical."""
    ok = True
    for skill_dir, skill in _each_source_skill():
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = read_text(skill_md)
        # A mention is legal only when the same body loads the file: a path in a
        # sibling reference or checklist is invisible to a reader of SKILL.md.
        loads = set(match.group(0).rsplit("/", 1)[1] for match in CANONICAL_LOAD.finditer(text))
        for name in sorted(set(match.group(1) for match in BACKTICKED_FILENAME.finditer(text))):
            if name not in CANONICAL_ASSETS or name in loads:
                continue
            err("error: %s mentions canonical asset %s in SKILL.md but never loads it; load it"
                " where it is read (%s%s) or drop the backticked"
                " filename" % (skill, name, CANONICAL_PREFIX, name))
            ok = False
    return ok


CHECKS = (_validate_no_retired_tokens, _validate_skill_md_paths, _validate_no_sigil_refs,
          _validate_reference_depth, _check_canonical_assets, _check_role_template_parity,
          _check_skill_asset_closure, _check_canonical_mentions)


def main(argv=None):
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    # Every check runs, so one pass reports every violation.
    results = [check() for check in CHECKS]
    if not all(results):
        return 1
    print("Validation passed: plugin content is install-clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
