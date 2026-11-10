#!/usr/bin/env python3
"""Set up AndThen on Claude Code, Codex, and Copilot CLI, and prove the result.

  andthen.py install [--ref REF] [options]

Each host whose CLI is on PATH installs the plugin from the repo tree this script
sits in, as a local marketplace. With no tree around (piped through curl) or with
`--ref REF`, the script first downloads that ref's tree (default main) to
${XDG_DATA_HOME:-~/.local/share}/andthen/<version> and runs that tree's own script.

Claude Code and Codex install a plugin as a *copy* under a version-keyed cache
directory, and Claude Code's `plugin update` leaves a stale copy in place while
the version is unchanged, so every host runs the same sequence: drop the install,
re-point the marketplace, install again. The version is read back from the
installed copy, not trusted from a success message. Copilot loads a local
marketplace live from the tree, which is why a download is kept.

Opt-in extras at user level (`install --help` lists them): --roles and --rules
place the role agents and the critical-rules block, --trust marks a project
trusted in Codex, --loose copies skills instead of installing the plugin.
Every write is read back and compared. Exit 0 only when every host installed and
verified and every requested item was written or accepted.

Stdlib only, Python 3.9+: this runs before anything is installed.
"""

from __future__ import annotations

import argparse
import filecmp
import io
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO = "IT-HUSET/andthen"
MANIFEST = ".claude-plugin/marketplace.json"
IGNORE = [".DS_Store", "__pycache__", ".in_use", ".git"]

# The tree the script sits in: source of the local marketplace and of every
# template, so a run is one version byte for byte. Piped, `__file__` is `<stdin>`, which
# resolves against the cwd, so a piped run has no tree (None) and downloads one.
REPO_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).is_file() else None


def _run(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    """The one place a host CLI runs; tests replace it. `which` resolves a
    Windows .cmd shim that a bare name would miss."""
    resolved = [shutil.which(cmd[0]) or cmd[0]] + cmd[1:]
    return subprocess.run(resolved, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          cwd=cwd)


def _which(cli: str) -> str | None:
    return shutil.which(cli)


class Report:
    """Per-host summary in the `  v` / `  x` style; any `x` fails the run."""

    def __init__(self) -> None:
        self.failed = False

    def ok(self, message: str) -> None:
        print(f"  v {message}")

    def bad(self, message: str, detail: list[str] | None = None) -> None:
        print(f"  x {message}")
        for line in detail or []:
            print(f"      {line}")
        self.failed = True


# ---------------------------------------------------------------------------
# Hosts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Host:
    key: str
    name: str
    cli: str
    home_env: str
    home_dir: str
    uninstall: Callable[[str, str], list[str]]
    mp_remove: Callable[[str], list[str]]
    mp_add: Callable[[str], list[str]]
    install: Callable[[str, str], list[str]]

    def home(self) -> Path:
        return Path(os.environ.get(self.home_env) or Path.home() / self.home_dir)


HOSTS = [
    Host("claude", "Claude Code", "claude", "CLAUDE_CONFIG_DIR", ".claude",
         lambda n, mp: ["claude", "plugin", "uninstall", f"{n}@{mp}"],
         lambda mp: ["claude", "plugin", "marketplace", "remove", mp],
         lambda s: ["claude", "plugin", "marketplace", "add", s],
         lambda n, mp: ["claude", "plugin", "install", f"{n}@{mp}", "-y"]),
    Host("codex", "Codex", "codex", "CODEX_HOME", ".codex",
         lambda n, mp: ["codex", "plugin", "remove", f"{n}@{mp}"],
         lambda mp: ["codex", "plugin", "marketplace", "remove", mp],
         lambda s: ["codex", "plugin", "marketplace", "add", s],
         lambda n, mp: ["codex", "plugin", "add", f"{n}@{mp}"]),
    Host("copilot", "Copilot CLI", "copilot", "COPILOT_HOME", ".copilot",
         lambda n, mp: ["copilot", "plugin", "uninstall", f"{n}@{mp}"],
         lambda mp: ["copilot", "plugin", "marketplace", "remove", mp],
         lambda s: ["copilot", "plugin", "marketplace", "add", s],
         lambda n, mp: ["copilot", "plugin", "install", f"{n}@{mp}"]),
]

HOST = {h.key: h for h in HOSTS}


def run_step(cmd: list[str], report: Report, *, optional: bool = False, dry: bool = False) -> bool:
    if dry:
        print("  would run:", " ".join(cmd))
        return True
    out = _run(cmd)
    if out.returncode == 0:
        return True
    if not optional:
        report.bad(" ".join(cmd), [(out.stderr or out.stdout).strip()])
    return False


def installed_version(plugin_dir: Path) -> str | None:
    try:
        return json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return None


def claude_install_record(mp: str, name: str) -> tuple[Path, str | None]:
    """Where Claude Code says it installed `name@mp`, and the version it
    recorded, from installed_plugins.json: the cache layout is not ours to
    compute, and a local marketplace may be loaded in place."""
    record = HOSTS[0].home() / "plugins" / "installed_plugins.json"
    entries = json.loads(record.read_text(encoding="utf-8"))["plugins"][f"{name}@{mp}"]
    entry = next((e for e in entries if e.get("scope") == "user"), entries[0])
    return Path(entry["installPath"]), entry.get("version")


def locate_install(host: Host, mp: str, name: str, version: str, src: str) -> tuple[Path, str | None]:
    """(installed copy, version the host recorded for it, if it records one)."""
    if host.key == "claude":
        return claude_install_record(mp, name)
    if host.key == "copilot":
        # A local marketplace is loaded live from the tree, so there is no copy to go stale.
        return REPO_ROOT / src, None  # only for copilot_problems to recognise the plugin's own paths
    return host.home() / "plugins" / "cache" / mp / name / version, None


def copilot_problems(mp: str, name: str, version: str, installed: Path) -> list[str]:
    """What Copilot reports about the install. Its installer prints a skill count
    even when a skill's frontmatter fails to parse, and only `skill list` names
    the failure, by path."""
    listed = _run(["copilot", "plugin", "list", "--json"])
    try:
        entries = json.loads(listed.stdout)
    except ValueError:
        return [f"`copilot plugin list --json` gave no JSON: {listed.stderr.strip()}"]
    if not any(e.get("name") == name and e.get("marketplace") == mp and e.get("version") == version
               for e in entries):
        return [f"`copilot plugin list` shows no {name}@{mp} {version}"]
    # An empty cwd: inside a repo, project skills join the listing, and under an
    # ancestor of the plugin, failure paths print relative to it.
    with tempfile.TemporaryDirectory() as cwd:
        skills = _run(["copilot", "skill", "list"], cwd=cwd)
    output = (skills.stdout + skills.stderr).splitlines()
    if not any(line.startswith("Plugin skills:") for line in output):
        return ["`copilot skill list` shows no plugin skills"]
    # Failures print one path per line; the plugin's own are the ones under it,
    # in either spelling of a symlinked home (macOS /var vs /private/var).
    roots = {str(installed), str(installed.resolve())}
    return [line.strip() for line in output if any(root in line for root in roots)]


def differences(src: Path, dst: Path) -> list[str]:
    cmp = filecmp.dircmp(src, dst, ignore=IGNORE)
    diffs = [f"{cmp.left}: {n}" for n in cmp.left_only + cmp.right_only + cmp.diff_files]
    for sub in cmp.subdirs.values():
        diffs += differences(Path(sub.left), Path(sub.right))
    return diffs


def seed_holding(mp: str) -> Path | None:
    """The first Claude Code plugin seed (CLAUDE_CODE_PLUGIN_SEED_DIR, a
    pathsep-separated list) that holds marketplace `mp`. A seed is read-only
    and has the layout of ~/.claude/plugins: known_marketplaces.json,
    marketplaces/<name>/, cache/<marketplace>/<plugin>/<version>/."""
    for entry in filter(None, os.environ.get("CLAUDE_CODE_PLUGIN_SEED_DIR", "").split(os.pathsep)):
        seed = Path(entry)
        try:
            known = json.loads((seed / "known_marketplaces.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            known = {}
        if mp in known or (seed / "marketplaces" / mp).is_dir():
            return seed
    return None


def verify_plugin(host: Host, mp: str, name: str, version: str, installed: Path,
                  listed: str | None, src: str, report: Report) -> None:
    if host.key == "copilot":
        # Copilot's "installed copy" is the source tree itself, so reading its version or diffing
        # it against the source would compare the tree with itself: `copilot plugin list --json` is the check.
        problems = copilot_problems(mp, name, version, installed)
        if problems:
            report.bad(f"{name}: the host reports problems with the install", problems[:10])
        else:
            report.ok(f"{name} {version}")
        return
    found = installed_version(installed)
    if found != version or listed not in (None, version):
        report.bad(f"{name}: expected {version} at {installed}, found {found or 'nothing'}"
                   + (f" (host recorded {listed})" if listed not in (None, found) else ""))
        return
    # A stale copy is invisible to the host, so the installed copy is diffed
    # against the source rather than merely located.
    diffs = differences(REPO_ROOT / src, installed)
    if diffs:
        report.bad(f"{name}: installed copy differs from source", diffs[:10])
    else:
        report.ok(f"{name} {version}")


def install_plugin(host: Host, mf: dict, dry: bool, report: Report) -> None:
    mp = mf["name"]
    plugins = [(p["name"], p["source"].lstrip("./"), p.get("version", "")) for p in mf["plugins"]]

    seed = seed_holding(mp) if host.key == "claude" else None
    if seed:
        # Claude Code never writes to a seed, and `marketplace remove` on one
        # fails, so the remove-and-reinstall is skipped and the seed verified.
        print(f"  seeded marketplace at {seed}: nothing to reinstall, verifying")
        for name, src, version in plugins:
            verify_plugin(host, mp, name, version, seed / "cache" / mp / name / version, None, src, report)
        # Presence only (ADR-030): enablement lives in managed or project
        # settings, which the script cannot read reliably, so it is not checked.
        keys = ", ".join(f'"{n}@{mp}": true' for n, _, _ in plugins)
        print(f"  The seed's plugins load only where enabledPlugins names them ({keys} in"
              " managed settings or the project's .claude/settings.json); confirm with"
              " `claude -p --output-format stream-json --verbose`.")
        return

    for name, _, _ in plugins:
        run_step(host.uninstall(name, mp), report, optional=True, dry=dry)
    run_step(host.mp_remove(mp), report, optional=True, dry=dry)
    if not run_step(host.mp_add(str(REPO_ROOT)), report, dry=dry):
        return
    for name, src, version in plugins:
        if not run_step(host.install(name, mp), report, dry=dry) or dry:
            continue
        try:
            installed, listed = locate_install(host, mp, name, version, src)
        except (OSError, ValueError, KeyError, IndexError) as err:
            report.bad(f"{name}: cannot find where {host.name} installed it ({type(err).__name__}: {err})")
            continue
        verify_plugin(host, mp, name, version, installed, listed, src, report)


# ---------------------------------------------------------------------------
# Placement: role agents, rules, and Codex trust, at user level. These write files
# the user owns, so comparisons ignore line-ending and trailing-whitespace
# differences (a Windows checkout arrives CRLF), a differing file is refused
# rather than merged, and every write is read back.
# ---------------------------------------------------------------------------

TEMPLATES = "plugin/skills/init/templates"
RULES_HEADING = "# Critical Rules and Guardrails"
RULES_FILE = {"claude": "CLAUDE.md", "codex": "AGENTS.md", "copilot": "copilot-instructions.md"}
ROLE_SUFFIX = {"claude": ".md", "codex": ".toml", "copilot": ".agent.md"}
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s")
RULES_HEADING_ANY_LEVEL = re.compile(r"^#{1,6}\s+Critical Rules and Guardrails\s*$")
BOM = "\ufeff"
LINE_BREAK = re.compile(r"\r\n|\r|\n")


def _write(path: Path, data: bytes) -> None:
    """Every placement write goes through here; tests replace it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _write_verified(path: Path, data: bytes, original: bytes | None, matches: Callable[[], bool]) -> str | None:
    """Write `data`, then ask `matches` whether it reads back right. None when it
    does. When it does not, the file goes back to `original` (removed when it did
    not exist), so a failed run never leaves a half-edited file of the user's
    behind, and the returned phrase says what became of it."""
    _write(path, data)
    if matches():
        return None
    try:
        if original is None:
            path.unlink()
            return "the new file was removed"
        path.write_bytes(original)
        return "the file was put back as it was"
    except OSError as err:
        return f"restoring it failed: {err}"


def _text(data: bytes) -> str:
    return data.decode("utf-8", errors="surrogateescape")


def _bytes(text: str) -> bytes:
    return text.encode("utf-8", errors="surrogateescape")


def normalized(text: str) -> str:
    lines = [line.rstrip() for line in LINE_BREAK.split(text)]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def eol_of(data: bytes) -> str:
    return "\r\n" if b"\r\n" in data else "\n"


def append_block(existing: bytes, addition: str) -> bytes:
    """`addition` after one blank line, in the file's own line endings, with
    everything already there left as it was."""
    eol = eol_of(existing)
    tail = _text(existing)
    gap = "" if not tail or tail.endswith(eol + eol) else eol if tail.endswith(eol) else eol + eol
    return existing + _bytes(gap + addition.replace("\n", eol))


def place_roles(host: Host, replace: bool, dry: bool, report: Report) -> None:
    templates = (REPO_ROOT / TEMPLATES / "agents" / host.key).iterdir()
    for template in sorted(t for t in templates if t.is_file() and t.name.endswith(ROLE_SUFFIX[host.key])):
        target = host.home() / "agents" / template.name
        wanted = normalized(_text(template.read_bytes()))
        original = target.read_bytes() if target.is_file() else None
        if original is not None:
            if normalized(_text(original)) == wanted:
                report.ok(f"{target} accepted (matches its template)")
                continue
            if not replace:
                report.bad(f"{target}: differs from its template, not replaced",
                           ["Review it with the andthen:init skill's role-agent offer,"
                            " or pass --replace-roles to overwrite it."])
                continue
            verb = "replaced"
        else:
            verb = "written"
        if dry:
            print(f"  would write {target}")
            continue
        failed = _write_verified(target, template.read_bytes(), original,
                                 lambda: normalized(_text(target.read_bytes())) == wanted)
        if failed:
            report.bad(f"{target}: differs from its template after the write ({failed})")
        else:
            report.ok(f"{target} {verb}")


def rules_block(text: str, own_headings: set[str]) -> str | None:
    """The bounded block (`offers.md`, Adopt): from the rules heading to the next
    heading of any level that is not one of the guideline's own, so the user's
    other content, before or after it, is no part of the comparison."""
    # A byte order mark (an editor's UTF-8 signature) is not part of the first line.
    lines = LINE_BREAK.split(text.removeprefix(BOM))
    start = next((i for i, line in enumerate(lines) if line.rstrip() == RULES_HEADING), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines))
                if MARKDOWN_HEADING.match(lines[i]) and lines[i].rstrip() not in own_headings), len(lines))
    return "\n".join(lines[start:end])


def place_rules(host: Host, dry: bool, report: Report) -> None:
    template = _text((REPO_ROOT / TEMPLATES / "guidelines" / "CRITICAL-RULES-AND-GUARDRAILS.md").read_bytes())
    if not template.startswith(RULES_HEADING):
        report.bad(f"the rules template does not start with `{RULES_HEADING}`")
        return
    own = {line.rstrip() for line in LINE_BREAK.split(template) if MARKDOWN_HEADING.match(line)}
    wanted = normalized(template)
    target = host.home() / RULES_FILE[host.key]

    existing = target.read_bytes() if target.is_file() else None
    current = rules_block(_text(existing), own) if existing is not None else None
    if current is not None:
        if normalized(current) == wanted:
            report.ok(f"{target} accepted (its rules block matches)")
        else:
            report.bad(f"{target}: its `{RULES_HEADING}` block differs from the template, not replaced",
                       ["The file is yours, so the script never overwrites it."
                        " Resolve it with the andthen:init skill's rules offer."])
        return
    if existing is not None and any(RULES_HEADING_ANY_LEVEL.match(line) for line in
                                    LINE_BREAK.split(_text(existing).removeprefix(BOM))):
        # Same words at another heading level: the user's own take on the block, which a
        # second copy appended below would contradict.
        report.bad(f"{target}: it has the `{RULES_HEADING}` text at another heading level, not changed",
                   ["The file is yours, so the script never edits around it."
                    " Resolve it with the andthen:init skill's rules offer."])
        return
    if dry:
        print(f"  would write the rules block into {target}")
        return

    def reads_back() -> bool:
        placed = rules_block(_text(target.read_bytes()), own)
        return placed is not None and normalized(placed) == wanted

    block = wanted + "\n"
    failed = _write_verified(target, append_block(existing, block) if existing else _bytes(block),
                             existing, reads_back)
    if failed:
        report.bad(f"{target}: the rules block differs from its template after the write ({failed})")
    else:
        report.ok(f"{target} {'appended' if existing else 'written'}")


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def toml_table_pattern(group: str, key: str) -> re.Pattern:
    """The header Codex writes for `[group."key"]`, in its basic-string or its
    literal-string spelling. No TOML parser: `tomllib` needs Python 3.11."""
    spellings = [re.escape(f'"{toml_escape(key)}"')] + ([re.escape(f"'{key}'")] if "'" not in key else [])
    return re.compile(rf"^\s*\[{re.escape(group)}\.(?:{'|'.join(spellings)})\]\s*(?:#.*)?$")


TRUST_LEVEL = re.compile(r"""^\s*trust_level\s*=\s*(?:"([^"]*)"|'([^']*)')""")


def trust_state(text: str, project: str) -> tuple[int | None, str | None]:
    """(index of the project's table header line, its trust_level) in a Codex
    config.toml; (None, None) when there is no such table."""
    header = toml_table_pattern("projects", project)
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if header.match(line):
            for body in lines[index + 1:]:
                if body.lstrip().startswith("["):
                    break
                found = TRUST_LEVEL.match(body)
                if found:
                    return index, found.group(1) if found.group(1) is not None else found.group(2)
            return index, None
    return None, None


def trust_spelled_elsewhere(text: str, project: str) -> bool:
    """Whether the project's path names a key anywhere but on a header trust_state
    reads: a padded header, a dotted key, an inline table. A table appended beside
    one of those would be invalid TOML. The same path as a value (a marketplace
    `source`, an MCP `cwd`) names no key, so it does not count."""
    header = toml_table_pattern("projects", project)
    spellings = "|".join(re.escape(s) for s in (f'"{toml_escape(project)}"', f"'{project}'"))
    keys = [  # a header under projects, `projects."p".…`, and `"p" =` or `"p".…` at a key position
        re.compile(rf"^\s*\[\[?\s*projects\s*\.\s*(?:{spellings})"),
        re.compile(rf"^\s*projects\s*\.\s*(?:{spellings})"),
        re.compile(rf"(?:^|[{{,])\s*(?:{spellings})\s*[.=]"),
    ]
    return any(not header.match(line) and any(k.search(line) for k in keys) for line in text.splitlines())


def place_trust(path: Path, dry: bool, report: Report) -> None:
    project = str(path)
    config = HOST["codex"].home() / "config.toml"
    existing = config.read_bytes() if config.is_file() else None
    before = existing or b""
    header_index, level = trust_state(_text(before), project)
    if level == "trusted":
        report.ok(f"{config}: {project} already trusted")
        return
    if level is not None:
        report.bad(f"{config}: {project} already has trust_level = \"{level}\", not changed")
        return
    if trust_spelled_elsewhere(_text(before), project):
        report.bad(f"{config}: {project} is written in a form this script does not edit, not changed",
                   ['Set trust_level = "trusted" for it by hand.'])
        return
    if dry:
        print(f"  would mark {project} trusted in {config}")
        return
    if header_index is None:
        data = append_block(before, f'[projects."{toml_escape(project)}"]\ntrust_level = "trusted"\n')
    else:  # a table Codex wrote for another setting, such as `enabled = true`
        eol = eol_of(before)
        lines = _text(before).splitlines(keepends=True)
        if lines[header_index].splitlines()[0] == lines[header_index]:  # last line, no line break
            lines[header_index] += eol
        lines.insert(header_index + 1, 'trust_level = "trusted"' + eol)
        data = _bytes("".join(lines))
    failed = _write_verified(config, data, existing,
                             lambda: trust_state(_text(config.read_bytes()), project)[1] == "trusted")
    if failed:
        report.bad(f"{config}: {project} is not trusted after the write ({failed})")
    else:
        report.ok(f"{config}: {project} marked trusted")


def codex_plugin_installed() -> bool:
    config = HOST["codex"].home() / "config.toml"
    if not config.is_file():
        return False
    header = toml_table_pattern("plugins", "andthen@andthen")
    return any(header.match(line) for line in _text(config.read_bytes()).splitlines())


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="andthen.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    ins = sub.add_parser("install", help="install AndThen on every host whose CLI is on PATH",
                         description="Install AndThen from the repo tree this script sits in, or from the"
                                     " tree --ref downloads.")
    # Handled by `main` before this parser runs, so a newer tree's flags never meet this copy's
    # parser; declared here so `install --help` documents it.
    ins.add_argument("--ref", metavar="REF",
                     help="download that branch or tag (default main) and run its own script"
                          " instead of the tree this script sits in")
    ins.add_argument("--loose", action="store_true",
                     help="copy skills as andthen-<name> into --skills-dir instead of installing the plugin")
    ins.add_argument("--skills", metavar="LIST",
                     help="with --loose: comma-separated skill names (default: all), e.g. clarify,plan")
    ins.add_argument("--skills-dir", metavar="PATH",
                     help="with --loose: destination (default: ~/.agents/skills, refused while the AndThen"
                          " Codex plugin is installed, because Codex would list every skill twice)")
    ins.add_argument("--roles", action="store_true",
                     help="place the role agents in each host's agents/ directory; a differing file is refused")
    ins.add_argument("--replace-roles", action="store_true",
                     help="with --roles, overwrite a differing role file (implies --roles)")
    ins.add_argument("--rules", action="store_true",
                     help="place the critical-rules block in each host's user instruction file;"
                          " a differing block is refused, never overwritten")
    ins.add_argument("--trust", metavar="PATH", help="mark PATH trusted in Codex's config.toml (never a default)")
    ins.add_argument("--claude-only", action="store_true")
    ins.add_argument("--codex-only", action="store_true")
    ins.add_argument("--copilot-only", action="store_true")
    ins.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    args = ap.parse_args(argv)
    for flag, value in (("--skills", args.skills), ("--skills-dir", args.skills_dir), ("--trust", args.trust)):
        if value == "":  # never a silent fallback to the default
            ap.error(f"{flag} given an empty value")
    if (args.skills is not None or args.skills_dir is not None) and not args.loose:
        ap.error("--skills and --skills-dir need --loose")
    args.roles = args.roles or args.replace_roles
    if args.loose and not (args.roles or args.rules or args.trust) and \
            (args.claude_only or args.codex_only or args.copilot_only):
        ap.error("--claude-only, --codex-only and --copilot-only select hosts, which --loose uses only"
                 " with --roles, --rules or --trust")
    return args


def selected_hosts(args: argparse.Namespace, report: Report) -> list[Host]:
    only = {"claude": args.claude_only, "codex": args.codex_only, "copilot": args.copilot_only}
    wanted = [h for h in HOSTS if only[h.key]] if any(only.values()) else list(HOSTS)
    found = []
    for host in wanted:
        if _which(host.cli):
            found.append(host)
        elif any(only.values()):
            report.bad(f"{host.name}: `{host.cli}` not on PATH")
        else:
            print(f"{host.name}: `{host.cli}` not on PATH - skipped")
    if not found and not report.failed:
        report.bad("no host CLI (claude, codex, copilot) on PATH")
    return found


def install_loose(args: argparse.Namespace, report: Report) -> None:
    print("Loose skills:")
    if args.skills_dir is None and codex_plugin_installed():
        report.bad("not installed into ~/.agents/skills: the AndThen Codex plugin is installed, and Codex"
                   " reads that directory too, so it would list every skill twice",
                   ["Name another directory with --skills-dir, or drop --loose."])
        return
    import andthen_loose  # not at the top: piped through curl there is no sibling to import
    try:
        count, destination = andthen_loose.install(
            andthen_loose.default_skills_dir() if args.skills_dir is None else args.skills_dir,
            "" if args.skills is None else args.skills, args.dry_run)
    except andthen_loose.InstallError:
        report.bad("loose install failed")
        return
    report.ok(f"{'would install' if args.dry_run else 'installed'} {count} skills into {destination}")


def bootstrap(args: list[str], *, home: Path | None = None,
              fetch: Callable[[str], bytes] = lambda url: urllib.request.urlopen(url, timeout=60).read()) -> int:
    """Download a ref's tree to <data home>/andthen/<version> and run that tree's
    own script on the other args, as a child process: os.execv loses the exit code
    on Windows. Dropping `--ref` is the loop guard, and lets the child place roles
    and rules, being inside a tree."""
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--ref", default="main")
    ns, rest = parser.parse_known_args(args)
    url = f"https://codeload.github.com/{REPO}/tar.gz/{ns.ref}"
    home = home or Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "andthen"
    try:
        data = fetch(url)
    except OSError as err:
        print(f"Cannot download {url}: {err}")
        if isinstance(getattr(err, "reason", err), ssl.SSLError):
            print("Python ignores the system CA store: set SSL_CERT_FILE to the bundle curl trusts.")
        return 1
    home.mkdir(parents=True, exist_ok=True)
    # The scratch dir sits beside the destination: the rename stays on one filesystem.
    with tempfile.TemporaryDirectory(dir=home, prefix=".fetch-") as scratch, \
            tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        # The `data` filter is absent on stock macOS 3.9, and 3.12+ warns without it.
        tar.extractall(scratch, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
        tree = next(Path(scratch).iterdir(), Path(scratch))  # GitHub names it andthen-<ref>: never computed
        try:
            plugins = json.loads((tree / MANIFEST).read_text(encoding="utf-8"))["plugins"]
            version = next(p["version"] for p in plugins if p["name"] == "andthen")
        except (OSError, ValueError, KeyError, StopIteration):
            print(f"{ns.ref} is not an AndThen tree: no `andthen` entry in {MANIFEST}")
            return 1
        if not (tree / "scripts" / "andthen.py").is_file():
            print(f"{ns.ref} predates scripts/andthen.py; follow that tag's own README")
            return 1
        destination = home / version
        try:
            if destination.exists():
                shutil.rmtree(destination)  # replace, never overlay: a dropped file must go
            tree.rename(destination)
        except OSError as err:  # Windows refuses to delete a file a running host holds open
            print(f"Cannot replace {destination}: {err}\n"
                  "  It may be in use: close Claude Code, Codex, and Copilot CLI, then run again.")
            return 1
    # Flushed, or a piped stdout prints this after the child's own output.
    print(f"AndThen {version} ({ns.ref}) downloaded to {destination}", flush=True)
    return subprocess.call([sys.executable, str(destination / "scripts" / "andthen.py"), *rest])


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # One rule: `--ref` means "fetch that version", wherever the script runs. It is handled here, before
    # parse_args, so a newer tree's flags never meet this copy's parser.
    if any(a == "--ref" or a.startswith("--ref=") for a in argv) or REPO_ROOT is None \
            or not (REPO_ROOT / MANIFEST).is_file():
        return bootstrap(argv)
    args = parse_args(argv)
    report = Report()

    mf = None if args.loose else json.loads((REPO_ROOT / MANIFEST).read_text(encoding="utf-8"))
    if mf:
        print(f"Marketplace: {mf['name']}  ({REPO_ROOT})")
    else:
        install_loose(args, report)

    if mf or args.roles or args.rules or args.trust:
        hosts = selected_hosts(args, report)
        for host in hosts:
            print(f"{host.name}:")
            if mf:
                install_plugin(host, mf, args.dry_run, report)
            if args.roles:
                place_roles(host, args.replace_roles, args.dry_run, report)
            if args.rules:
                place_rules(host, args.dry_run, report)
            if args.trust and host.key == "codex":
                place_trust(Path(args.trust).resolve(), args.dry_run, report)
        if args.trust and "codex" not in {h.key for h in hosts}:
            report.bad("--trust needs Codex: `codex` is not on PATH, or another --*-only flag excludes it")

    if mf and not args.dry_run:
        print("Restart Claude Code / Codex / Copilot CLI to load the new copy.")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
