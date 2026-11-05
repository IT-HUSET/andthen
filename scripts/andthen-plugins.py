#!/usr/bin/env python3
"""Install, switch, or refresh the AndThen plugin on Claude Code, Codex, and
Copilot CLI.

Claude Code and Codex install a plugin as a *copy* under a version-keyed cache
directory, so nothing short of uninstall+install re-copies: Claude Code's
`plugin update` compares version strings and leaves a stale copy in place while
the version is unchanged, and switching release lines changes the marketplace
ref, not the version. Copilot copies a remote marketplace's plugin without a
version directory and loads a local one live from the checkout. Every mode here
therefore runs the same sequence - drop the installs, re-point the marketplace,
install again - and proves the result by reading the version from the installed
copy rather than trusting a success message.

Targets:
  rc          the 1.0 release candidates on develop (a tag such as v1.0.0-rc.2
              via --ref pins one)
  stable      the 0.x line on main
  --ref REF   any branch or tag of the marketplace repo
  --path DIR  a local checkout (development refresh; also diffs the copy)
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = "IT-HUSET/andthen"
# pre-release: at 1.0 `stable` is 1.0 on main and `rc` goes: here, in the module docstring's Targets list, and in the `rc|stable` text of the `ap.error` call in main().
CHANNELS = {"rc": "develop", "stable": "main"}
MANIFEST = ".claude-plugin/marketplace.json"
IGNORE = [".DS_Store", "__pycache__", ".in_use", ".git"]


def read_manifest(path: str | None, ref: str | None) -> dict:
    """Marketplace name, plugin names, and versions - from the source itself, so
    a renamed or added plugin needs no edit here."""
    if path:
        return json.loads((Path(path) / MANIFEST).read_text(encoding="utf-8"))
    url = f"https://raw.githubusercontent.com/{REPO}/{ref}/{MANIFEST}"
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 - fixed host
        return json.loads(resp.read().decode("utf-8"))


def host_root(env_var: str, default: str) -> Path:
    return Path(os.environ.get(env_var) or Path.home() / default)


def run(cmd: list[str], *, optional: bool = False, dry: bool = False) -> bool:
    if dry:
        print("  would run:", " ".join(cmd))
        return True
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode == 0:
        return True
    if not optional:
        print(f"  ! {' '.join(cmd)}\n    {(out.stderr or out.stdout).strip()}")
    return False


def installed_version(plugin_dir: Path) -> str | None:
    try:
        return json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return None


def copilot_problems(mp: str, name: str, version: str, installed: Path) -> list[str]:
    """What Copilot reports about the install. Its installer prints a skill count
    even when a skill's frontmatter fails to parse, and only `skill list` names
    the failure, by path."""
    listed = subprocess.run(["copilot", "plugin", "list", "--json"], capture_output=True, text=True)
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
        skills = subprocess.run(["copilot", "skill", "list"], capture_output=True, text=True, cwd=cwd)
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


def refresh(host: str, cli: str, cmds: dict, source: str, mf: dict, args) -> bool:
    print(f"{host}:")
    mp = mf["name"]
    plugins = [(p["name"], p["source"].lstrip("./"), p.get("version", "")) for p in mf["plugins"]]

    for name, _, _ in plugins:
        run(cmds["uninstall"](name, mp), optional=True, dry=args.dry_run)
    run(cmds["mp_remove"](mp), optional=True, dry=args.dry_run)
    if not run(cmds["mp_add"](source), dry=args.dry_run):
        return False

    ok = True
    for name, src, version in plugins:
        if not run(cmds["install"](name, mp), dry=args.dry_run):
            ok = False
            continue
        if args.dry_run:
            continue
        installed = cmds["installed"](mp, name, version, src)
        found = installed_version(installed)
        if found != version:
            print(f"  x {name}: expected {version} at {installed}, found {found or 'nothing'}")
            ok = False
            continue
        problems = cmds["check"](mp, name, version, installed) if "check" in cmds else []
        if problems:
            print(f"  x {name}: the host reports problems with the install")
            print("\n".join(f"      {p}" for p in problems[:10]))
            ok = False
            continue
        # A local refresh is the case where a stale copy is invisible, so it is
        # the case that gets diffed rather than merely located.
        diffs = differences(Path(args.path, src), installed) if args.path else []
        if diffs:
            print(f"  x {name}: installed copy differs from source")
            print("\n".join(f"      {d}" for d in diffs[:10]))
            ok = False
        else:
            print(f"  v {name} {version}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel", nargs="?", choices=sorted(CHANNELS), help="release line to install")
    ap.add_argument("--ref", help="branch or tag of the marketplace repo")
    ap.add_argument("--path", help="local checkout to install from")
    ap.add_argument("--claude-only", action="store_true")
    ap.add_argument("--codex-only", action="store_true")
    ap.add_argument("--copilot-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    chosen = [bool(args.channel), bool(args.ref), bool(args.path)]
    if sum(chosen) != 1:
        ap.error("give exactly one of: a channel (rc|stable), --ref REF, or --path DIR")

    ref = CHANNELS.get(args.channel or "", args.ref)
    if args.path:
        args.path = str(Path(args.path).resolve())
        source = args.path
    else:
        source = f"{REPO}@{ref}"

    try:
        mf = read_manifest(args.path, ref)
    except Exception as err:  # noqa: BLE001 - one message beats a traceback here
        print(f"Cannot read the marketplace manifest for {source}: {err}")
        return 1

    print(f"Marketplace: {mf['name']}  ({source})")

    hosts = {
        "Claude Code": (
            "claude",
            {
                "uninstall": lambda n, mp: ["claude", "plugin", "uninstall", f"{n}@{mp}"],
                "mp_remove": lambda mp: ["claude", "plugin", "marketplace", "remove", mp],
                "mp_add": lambda s: ["claude", "plugin", "marketplace", "add", s],
                "install": lambda n, mp: ["claude", "plugin", "install", f"{n}@{mp}", "-y"],
                "installed": lambda mp, n, v, _: host_root("CLAUDE_CONFIG_DIR", ".claude") / "plugins" / "cache" / mp / n / v,
            },
        ),
        "Codex": (
            "codex",
            {
                "uninstall": lambda n, mp: ["codex", "plugin", "remove", f"{n}@{mp}"],
                "mp_remove": lambda mp: ["codex", "plugin", "marketplace", "remove", mp],
                "mp_add": lambda s: ["codex", "plugin", "marketplace", "add", s],
                "install": lambda n, mp: ["codex", "plugin", "add", f"{n}@{mp}"],
                "installed": lambda mp, n, v, _: host_root("CODEX_HOME", ".codex") / "plugins" / "cache" / mp / n / v,
            },
        ),
        "Copilot CLI": (
            "copilot",
            {
                "uninstall": lambda n, mp: ["copilot", "plugin", "uninstall", f"{n}@{mp}"],
                "mp_remove": lambda mp: ["copilot", "plugin", "marketplace", "remove", mp],
                # Copilot has no owner/repo@ref form; a git URL fragment pins the ref.
                "source": args.path or f"https://github.com/{REPO}.git#{ref}",
                "mp_add": lambda s: ["copilot", "plugin", "marketplace", "add", s],
                "install": lambda n, mp: ["copilot", "plugin", "install", f"{n}@{mp}"],
                # A local marketplace is loaded live from the checkout, so there is no copy to go stale.
                "installed": lambda mp, n, v, src: (
                    Path(args.path, src) if args.path
                    else host_root("COPILOT_HOME", ".copilot") / "installed-plugins" / mp / n
                ),
                "check": copilot_problems,
            },
        ),
    }
    only = {"Claude Code": args.claude_only, "Codex": args.codex_only, "Copilot CLI": args.copilot_only}
    if any(only.values()):
        hosts = {host: spec for host, spec in hosts.items() if only[host]}

    failed = 0
    for host, (cli, cmds) in hosts.items():
        if not shutil.which(cli):
            print(f"{host}: `{cli}` not on PATH - skipped")
            continue
        if not refresh(host, cli, cmds, cmds.get("source", source), mf, args):
            failed = 1

    if not args.dry_run:
        print("Restart Claude Code / Codex / Copilot CLI to load the new copy.")
    return failed


if __name__ == "__main__":
    sys.exit(main())
