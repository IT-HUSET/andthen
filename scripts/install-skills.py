#!/usr/bin/env python3
"""Install AndThen skills into an agent skills directory (loose-skill channel).

`scripts/install-skills.sh` is a shim that execs this module, so every
documented `bash scripts/install-skills.sh ...` invocation still works.

Stdlib only, Python 3.9+: the installer runs wherever the plugin is cloned,
before anything is installed.
"""

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

USAGE = """Install AndThen skills into an agent skills directory.

Usage:
  ./scripts/install-skills.sh [options]

Options:
  --skills-dir PATH         Destination for skill directories (default: ~/.agents/skills)
  --claude, --claude-user   Also install skills for Claude Code at the user-level
                            default (~/.claude/skills), using the same <prefix>
                            so invocation is /<prefix><name>.
                            (Set implicitly by --claude-skills-dir.)
                            Alternative to the Claude Code plugin. Safe to combine
                            with the plugin only when --prefix differs from the
                            default (andthen-); same prefix would expose duplicate
                            skills.
  --claude-skills-dir PATH  Override the Claude Code skills destination (implies a
                            Claude Code install). Use to target a project-local
                            location like <project>/.claude/skills for downstream
                            toolkits that bundle AndThen with their own --prefix.
  --skills LIST             Comma-separated source skill names to install
                            (default: all). Example: clarify,plan,review.
                            Names may be unprefixed or use the current exported
                            prefix (e.g. andthen-plan with the default prefix).
  --prefix PREFIX           Prefix for exported names (letters, numbers, '_',
                            and '-' only; must end with '-'; default: andthen-)
  --display-brand BRAND     Human-readable brand name substituted for "AndThen"
                            in installed skill agents/openai.yaml files.
                            Default: AndThen (no rewrite). Use for white-label
                            installs where the namespace prefix is not
                            "andthen-" (e.g. --prefix dartclaw- pairs with
                            --display-brand DartClaw).
  --dry-run                 Print planned operations without copying files
  --validate-only           Run the pre-copy content validations (retired path
                            tokens, SKILL.md path shape, sigil-free references,
                            canonical asset existence and closure) and exit
                            without installing. Intended for CI and pre-release
                            checks.
  -h, --help                Show this help text

Notes:
  - Skills come from plugin/skills.
  - All skills are exported as directories named <prefix><skill-name>/
  - This installer propagates skills, not agents. The init skill separately
    offers four opt-in role templates; without them, delegation uses generic
    inherited subagents.
  - When --skills is set, only those source skills are exported. Missing names
    fail before any install work starts.
  - Skills are fully self-contained at install time: each skill owns its
    references/, templates/, and scripts/ locally. Shared assets at
    plugin/references/ are inlined into each consuming skill's references/
    and ../../references/ paths are rewritten to local-relative form,
    alongside the andthen: → <prefix> namespace rewrite.
  - Existing owned skill directories are replaced from a validated staged
    bundle, so files removed from the current release do not survive an upgrade.
  - Skipping the Claude Code install on a later run does NOT remove previously
    installed <claude-skills-dir>/<prefix>* – delete those manually if
    switching back to the Claude Code plugin as the primary path or
    relocating the install.
"""

REPO_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))

SKILLS_ROOT = REPO_ROOT / "plugin" / "skills"
REFERENCES_ROOT = REPO_ROOT / "plugin" / "references"

HOME = os.path.expanduser("~")

# ---------------------------------------------------------------------------
# Canonical install-inlined assets at plugin/references/ - consumed by one or
# more skills. Inlined into each consuming skill's references/ at install time
# so the installed bundle is self-contained (no path leaves the skill root).
#
# The table spelling is `name="a.md b.md"`, unchanged from the shell version:
# the error messages, the docs, and tests/test_skill_review.py all name these
# variables, and a skill author editing them finds the same shape.
# ---------------------------------------------------------------------------

# Names of the canonical shared assets (filenames only). A model reference's
# `.json` schema is a canonical of its own: it ships beside the reference and is
# read with it, so it travels into every consuming bundle the same way.
# Each must exist at plugin/references/<asset> and be listed by every consuming skill.
_canonical_assets="architecture-model.md architecture-model.schema.json automation-mode.md board-models.md context-map.schema.json design-tree.md event-storm.schema.json execution-discipline.md fis-authoring-guidelines.md fis-contract.md fis-mutability.md intent-and-rules-context.md lens-adversarial.md plan-schema.md plan.schema.json preflight.md project-document-templates.md review-calibration.md self-review.md testing-strategy.md verification-evidence.md"

# Per-skill declarations: `_skill_assets_<skill with - as _>` names the canonical
# assets that skill consumes. Only skills that reference ../../references/<asset>
# are listed, and the declaration must equal what the skill's own files reference
# - _check_skill_asset_closure proves both directions before any copy.
# plan orchestrates FIS authoring but never edits FIS prose, so fis-mutability is spec's and exec-spec's.
_skill_assets_plan="automation-mode.md fis-authoring-guidelines.md fis-contract.md plan-schema.md plan.schema.json preflight.md project-document-templates.md self-review.md"
_skill_assets_spec="automation-mode.md fis-authoring-guidelines.md fis-contract.md plan-schema.md plan.schema.json preflight.md project-document-templates.md self-review.md"
_skill_assets_exec_spec="automation-mode.md execution-discipline.md fis-contract.md fis-mutability.md plan-schema.md verification-evidence.md"
_skill_assets_exec_plan="automation-mode.md execution-discipline.md plan-schema.md verification-evidence.md"
_skill_assets_review="automation-mode.md fis-contract.md fis-mutability.md intent-and-rules-context.md lens-adversarial.md plan-schema.md review-calibration.md verification-evidence.md"
_skill_assets_architecture="automation-mode.md board-models.md context-map.schema.json design-tree.md event-storm.schema.json project-document-templates.md review-calibration.md"
_skill_assets_clarify="design-tree.md project-document-templates.md self-review.md"
_skill_assets_testing="automation-mode.md testing-strategy.md verification-evidence.md"
_skill_assets_triage="automation-mode.md project-document-templates.md verification-evidence.md"
_skill_assets_init="project-document-templates.md"
# describe merges what map-codebase and ubiquitous-language each consumed.
_skill_assets_describe="architecture-model.md architecture-model.schema.json project-document-templates.md"
_skill_assets_implement_fix="automation-mode.md fis-mutability.md intent-and-rules-context.md review-calibration.md verification-evidence.md"
_skill_assets_ui_ux_design="automation-mode.md"
_skill_assets_backlog_triage="automation-mode.md project-document-templates.md"
_skill_assets_simplify_code="automation-mode.md intent-and-rules-context.md verification-evidence.md"
_skill_assets_tracker="automation-mode.md project-document-templates.md"
# skill-review is self-contained: the finding contract, the Critic posture, and the
# rules-context bundle come from canonicals, never from the review skill's own files.
_skill_assets_skill_review="intent-and-rules-context.md lens-adversarial.md review-calibration.md"

CANONICAL_ASSETS = _canonical_assets.split()


def _skill_assets_var(skill):
    """The declaration variable name for a skill, as the errors name it."""
    return "_skill_assets_" + skill.replace("-", "_")


def _get_skill_assets(skill):
    """Canonical assets declared for a skill; empty for a skill that declares none."""
    return globals().get(_skill_assets_var(skill), "").split()


class InstallError(Exception):
    """A failure whose message has already been printed; abort with status 1."""


def err(message):
    sys.stderr.write(message + "\n")


def read_text(path):
    """File contents as text, byte-preserving (line endings and all)."""
    with open(str(path), "r", encoding="utf-8", errors="surrogateescape", newline="") as handle:
        return handle.read()


def write_text(path, text):
    with open(str(path), "w", encoding="utf-8", errors="surrogateescape", newline="") as handle:
        handle.write(text)


def lines_of(text):
    """Text as grep sees it: split on newlines only, no trailing empty line."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return parts


def substitute(path, old, new):
    """Replace every occurrence of `old` in a file, leaving it untouched otherwise."""
    text = read_text(path)
    if old in text:
        write_text(path, text.replace(old, new))


def markdown_files(directory):
    """Every .md file below a directory, in byte-stable order."""
    return sorted((p for p in Path(directory).rglob("*.md") if p.is_file()), key=str)


def files_below(directory):
    return sorted((p for p in Path(directory).rglob("*") if p.is_file()), key=str)


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

class Options(object):
    """Parsed command line. Mirrors the shell version's flag surface exactly."""

    def __init__(self):
        self.skills_dir = os.path.join(HOME, ".agents", "skills")
        self.claude_skills_dir = os.path.join(HOME, ".claude", "skills")
        self.install_claude_user = False
        self.prefix = "andthen-"
        self.display_brand = "AndThen"
        self.dry_run = False
        self.validate_only = False
        self.selected_skills_raw = ""
        self.selected_skills = []


def require_option_value(option, value):
    if not value:
        err("error: %s requires a value" % option)
        raise SystemExit(1)


def parse_args(argv):
    """Hand-rolled to keep the accepted surface exact: no --opt=value, no
    abbreviations, and the same error text as before."""
    opts = Options()
    index = 0
    while index < len(argv):
        arg = argv[index]
        following = argv[index + 1] if index + 1 < len(argv) else ""
        if arg == "--skills-dir":
            require_option_value(arg, following)
            opts.skills_dir = following
            index += 2
        elif arg in ("--claude", "--claude-user"):
            opts.install_claude_user = True
            index += 1
        elif arg == "--claude-skills-dir":
            require_option_value(arg, following)
            opts.claude_skills_dir = following
            opts.install_claude_user = True
            index += 2
        elif arg == "--skills":
            if not following:
                err("error: --skills requires a comma-separated list of skill names")
                raise SystemExit(1)
            opts.selected_skills_raw = following
            index += 2
        elif arg == "--prefix":
            require_option_value(arg, following)
            opts.prefix = following
            index += 2
        elif arg == "--display-brand":
            require_option_value(arg, following)
            opts.display_brand = following
            index += 2
        elif arg == "--dry-run":
            opts.dry_run = True
            index += 1
        elif arg == "--validate-only":
            opts.validate_only = True
            index += 1
        elif arg in ("-h", "--help"):
            sys.stdout.write(USAGE)
            raise SystemExit(0)
        else:
            err("Unknown option: %s\n" % arg)
            sys.stderr.write(USAGE)
            raise SystemExit(1)
    return opts


def validate_prefix(prefix):
    if not prefix.endswith("-"):
        err("error: --prefix must end with `-` (got %s)" % prefix)
        raise SystemExit(1)
    if re.search(r"[^a-zA-Z0-9_-]", prefix):
        err("error: --prefix may only contain letters, numbers, `_`, and `-` (got %s)" % prefix)
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Skill selection
# ---------------------------------------------------------------------------

def _available_skills():
    return ",".join(sorted(child.name for child in SKILLS_ROOT.iterdir() if child.is_dir()))


def _normalize_selected_skills(raw, prefix):
    if not raw:
        return []
    if raw.startswith(",") or raw.endswith(",") or ",," in raw:
        err("error: --skills contains an empty skill name in %s" % raw)
        raise InstallError()

    selected = []
    for token in raw.split(","):
        # Source skill names never contain whitespace; trimming lets users write
        # "clarify, plan" without carrying the space into validation.
        name = re.sub(r"[ \t\n\r\f\v]", "", token)
        if not name:
            err("error: --skills contains an empty skill name in %s" % raw)
            raise InstallError()

        for sigil in ("/andthen:", "andthen:"):
            if name.startswith(sigil):
                name = name[len(sigil):]
                break
        if name.startswith(prefix):
            name = name[len(prefix):]
        elif name.startswith("andthen-"):
            name = name[len("andthen-"):]

        if not name:
            err("error: --skills contains an empty skill name in %s" % raw)
            raise InstallError()
        if re.search(r"[^a-zA-Z0-9_-]", name):
            err("error: invalid skill name in --skills: %s" % name)
            err("available skills: %s" % _available_skills())
            raise InstallError()
        if not (SKILLS_ROOT / name).is_dir():
            err("error: unknown skill in --skills: %s" % name)
            err("available skills: %s" % _available_skills())
            raise InstallError()

        if name not in selected:
            selected.append(name)
    return selected


def _should_install_skill(name, selected):
    return not selected or name in selected


# ---------------------------------------------------------------------------
# Destination canonicalization
#
# The <skill-dir> rewrite bakes the destination into installed .md files, so a
# relative --skills-dir would produce broken invocations at runtime (the agent's
# cwd is not the installer's). The defaults are already absolute; this only
# matters for a relative destination flag.
# ---------------------------------------------------------------------------

def _canonicalize_dir(path):
    # An empty destination would otherwise resolve to the launch directory
    # (typically the repo root) and install there. Reject it loudly.
    if not path:
        err("error: cannot canonicalize empty path (got empty destination argument)")
        raise InstallError()
    if path.startswith("/"):
        return path
    # Create the destination so it can be resolved; install would create it
    # anyway. Keep the underlying cause (permission denied, ENOTDIR on a parent
    # that is a file) rather than collapsing into a generic failure.
    mkdir_error = ""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        mkdir_error = str(exc)
    if not os.path.isdir(path):
        # Fail loud rather than fall through to the original relative path.
        if mkdir_error:
            err("error: cannot canonicalize directory %s (mkdir failed: %s)" % (path, mkdir_error))
        else:
            err("error: cannot canonicalize directory %s (mkdir/cd failed)" % path)
        raise InstallError()
    return os.path.normpath(os.path.join(os.getcwd(), path))


def warn_about_plugin_collision(opts):
    """The Claude Code plugin cache layout is not a stable public contract, so
    this is best effort: check the current cache/<marketplace>/andthen layout
    plus a direct cache/andthen fallback."""
    cache = Path(HOME) / ".claude" / "plugins" / "cache"
    candidates = sorted(cache.glob("*/andthen")) + [cache / "andthen"]
    if not any(candidate.is_dir() for candidate in candidates):
        return
    # Only warn when prefixes would actually collide AND the install path is
    # going to the user-tier default. Downstream tools that wrap this installer
    # with their own --prefix (e.g. dartclaw-) or redirect --claude-skills-dir
    # coexist under disjoint namespaces or scopes and shouldn't see this.
    if opts.prefix != "andthen-":
        return
    if opts.claude_skills_dir != os.path.join(HOME, ".claude", "skills"):
        return
    err("warning: Claude user-tier install enabled with the default prefix and user-tier path"
        " but an andthen Claude Code plugin install appears present under ~/.claude/plugins/."
        " Running both will create duplicate skills under andthen:<name> (plugin) and"
        " andthen-<name> (user). Uninstall the plugin (/plugin uninstall andthen) before using"
        " the user-tier install, pass a distinct --prefix, or target a project-local"
        " --claude-skills-dir to coexist.")


# ---------------------------------------------------------------------------
# Pre-copy validations
# ---------------------------------------------------------------------------

PLUGIN_ROOTS = (REPO_ROOT / "plugin",)

SOURCE_ROOTS = (SKILLS_ROOT, REFERENCES_ROOT)

# The two Claude Code path variables, retired: both hosts announce the skill
# root, Codex never substituted either token, and a literal token in skill text
# costs the model a filesystem search per invocation.
RETIRED_TOKEN = re.compile(r"CLAUDE_PLUGIN_ROOT|CLAUDE_SKILL_DIR")
SIGIL_REF = re.compile(r"/andthen:|\$andthen")

CANONICAL_PREFIX = "../../references/"
SKILL_DIR_PLACEHOLDER = "<skill-dir>"


def _first_match_per_file(pattern, roots):
    """(path, line number, line) for the first match in each file under roots.

    Build artifacts are skipped for the same reason strip_build_artifacts drops
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
            " %s/scripts/<name>" % (path, number, line, CANONICAL_PREFIX,
                                    SKILL_DIR_PLACEHOLDER))
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


def _role_body_claude(path):
    """An agent template's prompt: everything after the frontmatter fences."""
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
    """Each optional role agent ships in two host formats, and only the
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
        if _role_body_claude(claude_template) != _role_body_codex(codex_template):
            err("error: role %s body differs between its Claude and Codex templates;"
                " the two hosts ship one persona" % role)
            ok = False
    return ok


def _check_canonical_assets():
    """Every canonical exists before any copy starts."""
    for asset in CANONICAL_ASSETS:
        if not (REFERENCES_ROOT / asset).is_file():
            err("error: %s/%s not found; cannot inline for consuming skills"
                % (REFERENCES_ROOT, asset))
            return False
    return True


CANONICAL_LOAD = re.compile(r"\.\./\.\./references/[A-Za-z0-9._-]+\.(?:md|json)")
BACKTICKED_FILENAME = re.compile(r"`([A-Za-z0-9._-]+\.(?:md|json))`")


def _direct_canonical_refs(path):
    """The canonicals a path loads: a load is a ../../references/ path in any of
    its markdown files, link or code span alike. A bare backticked filename loads
    nothing - it is a mention, checked by _check_canonical_mentions."""
    found = set()
    for markdown in markdown_files(path):
        for match in CANONICAL_LOAD.finditer(read_text(markdown)):
            found.add(match.group(0).rsplit("/", 1)[1])
    return sorted(found)


def _each_source_skill():
    """(skill dir, skill name) for every skill in the plugin dir."""
    for skill_dir in sorted(SKILLS_ROOT.iterdir(), key=lambda p: p.name):
        if skill_dir.is_dir() and not skill_dir.name.startswith("."):
            yield skill_dir, skill_dir.name


def _check_skill_asset_closure():
    """A skill's declaration must equal the direct references actually present in
    that skill's own files. This catches undeclared direct dependencies and
    stale declarations before any copy."""
    ok = True
    for skill_dir, skill in _each_source_skill():
        declared = _get_skill_assets(skill)
        required = _direct_canonical_refs(skill_dir)

        for asset in required:
            if asset not in CANONICAL_ASSETS:
                err("error: %s directly references %s, which is not in _canonical_assets"
                    % (skill, asset))
                ok = False

        for asset in required:
            if asset not in declared:
                err("error: %s references canonical asset %s, but it is not in %s"
                    % (skill, asset, _skill_assets_var(skill)))
                ok = False

        for asset in declared:
            if asset not in required:
                err("error: %s declares stale canonical asset %s in %s"
                    % (skill, asset, _skill_assets_var(skill)))
                ok = False
    return ok


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


INSTALLED_LINK = re.compile(r"\]\(([^)]*\.md)(#[^)]*)?\)")


def _check_rewritten_canonical_refs(skill_dir, skill):
    """Verify the paths produced by canonical-reference rewriting against the
    copied bundle, rather than assuming a successful pre-copy declaration caused
    a file to arrive. This catches copy/rewrite regressions at the installed
    boundary."""
    ok = True
    for asset in _get_skill_assets(skill):
        if not (Path(skill_dir) / "references" / asset).is_file():
            err("error: installed %s is missing canonical asset references/%s" % (skill, asset))
            ok = False
    for markdown in markdown_files(skill_dir):
        text = read_text(markdown)
        if CANONICAL_PREFIX in text:
            err("error: installed %s still carries %s in %s"
                % (skill, CANONICAL_PREFIX, markdown))
            ok = False
        if SKILL_DIR_PLACEHOLDER in text:
            err("error: installed %s still carries %s in %s"
                % (skill, SKILL_DIR_PLACEHOLDER, markdown))
            ok = False
        for match in INSTALLED_LINK.finditer(text):
            for link in match.group(1).split():
                if os.path.basename(link) not in CANONICAL_ASSETS:
                    continue
                resolved = link if link.startswith("/") else os.path.join(str(markdown.parent), link)
                if not os.path.isfile(resolved):
                    err("error: installed %s reference %s from %s does not resolve"
                        % (skill, link, markdown))
                    ok = False
    return ok


# ---------------------------------------------------------------------------
# Copy and rewrite
# ---------------------------------------------------------------------------

def inline_canonical_assets(destination, skill, refs_dir, dry_run):
    """Copy a skill's canonical assets into its own references/, so the installed
    bundle is self-contained. Canonicals carry no source frontmatter, so this is
    a plain copy."""
    for asset in _get_skill_assets(skill):
        source = Path(refs_dir) / asset
        if not source.is_file():
            err("error: %s not found; cannot inline for %s" % (source, destination))
            raise InstallError()
        if dry_run:
            print("mkdir -p %s/references" % destination)
            print("cp %s %s/references/%s" % (source, destination, asset))
        else:
            dst_refs = Path(destination) / "references"
            os.makedirs(str(dst_refs), exist_ok=True)
            shutil.copy(str(source), str(dst_refs / asset))


def rewrite_canonical_refs_dir(directory):
    """Rewrite ../../references/<asset> to references/<asset> in SKILL.md. The
    source form climbs from the skill root to its plugin's references/; an
    installed bundle carries its own inlined copies instead, so nothing may
    leave it. Only SKILL.md can carry this prefix - _validate_reference_depth
    forbids any other file in a skill from pathing to another file."""
    substitute(Path(directory) / "SKILL.md", CANONICAL_PREFIX, "references/")


def rewrite_skill_dir_dir(directory, skill_abs):
    """Bake <skill-dir> to the absolute installed skill path.

    <skill-dir> is the placeholder a model fills with the skill root its host
    announced. The installer already knows that path, so baking it spares the
    resolution step on every tier."""
    for markdown in markdown_files(directory):
        substitute(markdown, SKILL_DIR_PLACEHOLDER, str(skill_abs))


def rewrite_namespace_dir(directory, prefix):
    for markdown in markdown_files(directory):
        rewrite_namespace_file(markdown, prefix)


def rewrite_namespace_file(markdown, prefix):
    """andthen:<x> -> <prefix><x>. Shipped content is sigil-free by contract
    (_validate_no_sigil_refs), so this catch-all suffices for every install tier."""
    text = read_text(markdown)
    rewritten = text.replace("andthen:", prefix)
    if rewritten != text:
        write_text(markdown, rewritten)


SKILL_NS_LINE = re.compile(r"^SKILL_NS = ")


def rewrite_skill_namespace_scripts(skill_dir, prefix):
    """Rewrite the SKILL_NS constant in an installed skill's Python scripts.

    Runtime diagnostics name skills the user is told to invoke, and the
    loose-skill channel renames that namespace - without this, a renamed install
    prints instructions for skills it does not have. Anchored to the constant's
    own assignment line so nothing else in a script moves: storage keys matched
    on read (the tracker's plan marker, schema `$id`s, lock filenames) stay
    literal by construction, which is why this is not a file-wide substitution."""
    scripts = Path(skill_dir) / "scripts"
    if not scripts.is_dir():
        return
    files = sorted((p for p in scripts.rglob("*")
                    if p.is_file() and p.suffix == ".py"), key=str)
    for path in files:
        text = read_text(path)
        lines = text.split("\n")
        rewritten = [line.replace("andthen:", prefix) if SKILL_NS_LINE.match(line) else line
                     for line in lines]
        if rewritten != lines:
            write_text(path, "\n".join(rewritten))


def rewrite_skill_openai_metadata(skill_dir, prefix):
    openai_yaml = Path(skill_dir) / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        rewrite_namespace_file(openai_yaml, prefix)


def rewrite_display_brand_dir(skill_dir, brand):
    """Rewrite the brand-cased token "AndThen" -> <display_brand> in the installed
    skill's agents/openai.yaml (display_name, short_description, default_prompt).

    Scope is intentionally narrowed to agents/openai.yaml rather than all *.yaml
    under the skill: the broad form would silently rewrite incidental "AndThen"
    substrings in unrelated yaml (manifests, fixtures, URLs) introduced later."""
    if brand == "AndThen":
        return
    openai_yaml = Path(skill_dir) / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        substitute(openai_yaml, "AndThen", brand)


def strip_build_artifacts(destination):
    """Host metadata and compiled Python are build output of whoever ran the
    source tree, not plugin content: a gitignored __pycache__ left by a test run
    would otherwise ship into every install made from that checkout."""
    for path in Path(destination).rglob("*"):
        if path.is_file() and (path.name == ".DS_Store" or path.suffix == ".pyc"):
            try:
                path.unlink()
            except OSError:
                pass
    for path in sorted(Path(destination).rglob("__pycache__"), key=str, reverse=True):
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass


def copy_dir_contents(source, destination, dry_run):
    if dry_run:
        print("mkdir -p %s" % destination)
        print("cp -R %s/. %s/" % (source, destination))
        return
    os.makedirs(str(destination), exist_ok=True)
    shutil.copytree(str(source), str(destination), symlinks=True, dirs_exist_ok=True)
    strip_build_artifacts(destination)


def stage_skill_dir(source, destination):
    """Build the bundle beside its destination, so a failed install never leaves a
    half-rewritten skill behind. Returns the stage dir, or None on a copy failure."""
    destination = Path(destination)
    try:
        os.makedirs(str(destination.parent), exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix="." + destination.name + ".andthen-stage.",
                                      dir=str(destination.parent)))
    except OSError as exc:
        err("error: %s" % exc)
        return None
    try:
        shutil.copytree(str(source), str(stage), symlinks=True, dirs_exist_ok=True)
    except OSError:
        shutil.rmtree(str(stage), ignore_errors=True)
        return None
    strip_build_artifacts(stage)
    return stage


def replace_owned_skill_dir(stage, destination):
    """Swap a staged bundle in for the installed one, so files dropped from the
    current release do not survive an upgrade. Only a directory this installer
    owns (it has a SKILL.md) is replaced."""
    stage = str(stage)
    destination = str(destination)
    if os.path.islink(destination):
        err("error: refusing to replace symlinked skill destination %s" % destination)
        raise InstallError()
    if os.path.exists(destination) and not (
            os.path.isdir(destination) and os.path.isfile(os.path.join(destination, "SKILL.md"))):
        err("error: refusing to replace unowned skill destination %s"
            " (expected directory with SKILL.md)" % destination)
        raise InstallError()
    backup = "%s.andthen-backup.%d" % (destination, os.getpid())
    if os.path.exists(backup):
        err("error: install backup path already exists: %s" % backup)
        raise InstallError()
    if os.path.isdir(destination):
        os.rename(destination, backup)
    try:
        os.rename(stage, destination)
    except OSError:
        if os.path.isdir(backup):
            os.rename(backup, destination)
        raise InstallError()
    if os.path.isdir(backup):
        shutil.rmtree(backup, ignore_errors=True)


# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------

class StageFailure(Exception):
    """The staged copy failed before any rewrite; the installed bundle is untouched."""


def install_skill(source_skill, skill, destination, refs_dir, opts):
    """Stage, inline, rewrite, verify, then replace one installed skill bundle."""
    if opts.dry_run:
        copy_dir_contents(source_skill, destination, True)
        inline_canonical_assets(destination, skill, refs_dir, True)
        return

    stage = stage_skill_dir(source_skill, destination)
    if stage is None:
        raise StageFailure()
    try:
        # Inlining runs first so the inlined files are namespace-rewritten in the
        # same pass.
        inline_canonical_assets(stage, skill, refs_dir, False)
        rewrite_canonical_refs_dir(stage)
        rewrite_skill_dir_dir(stage, destination)
        rewrite_namespace_dir(stage, opts.prefix)
        rewrite_skill_namespace_scripts(stage, opts.prefix)
        rewrite_skill_openai_metadata(stage, opts.prefix)
        rewrite_display_brand_dir(stage, opts.display_brand)
        if not _check_rewritten_canonical_refs(stage, skill):
            raise InstallError()
        replace_owned_skill_dir(stage, destination)
    except InstallError:
        shutil.rmtree(str(stage), ignore_errors=True)
        raise


def install(opts):
    skills_count = 0
    claude_skills_count = 0

    for skill_dir, skill in _each_source_skill():
        if not _should_install_skill(skill, opts.selected_skills):
            continue

        target_name = skill if skill.startswith(opts.prefix) else opts.prefix + skill

        # ~/.agents/skills install (Codex discovery).
        try:
            install_skill(skill_dir, skill, Path(opts.skills_dir) / target_name,
                          REFERENCES_ROOT, opts)
        except StageFailure:
            err("error: failed to stage skill %s" % skill)
            raise SystemExit(1)
        skills_count += 1

        # Optional: Claude Code user-level skills.
        if opts.install_claude_user:
            try:
                install_skill(skill_dir, skill, Path(opts.claude_skills_dir) / target_name,
                              REFERENCES_ROOT, opts)
            except StageFailure:
                err("error: failed to stage Claude skill %s" % skill)
                raise SystemExit(1)
            claude_skills_count += 1

    verb = "Would install" if opts.dry_run else "Installed"
    print("%s %d skills into %s" % (verb, skills_count, opts.skills_dir))
    if claude_skills_count > 0:
        print("%s %d Claude Code user skills into %s"
              % (verb, claude_skills_count, opts.claude_skills_dir))


def main(argv):
    opts = parse_args(argv)
    validate_prefix(opts.prefix)
    opts.selected_skills = _normalize_selected_skills(opts.selected_skills_raw, opts.prefix)

    opts.skills_dir = _canonicalize_dir(opts.skills_dir)
    if opts.install_claude_user:
        # Canonicalize only when the Claude user-tier install is requested;
        # otherwise the call would pre-create ~/.claude/skills on every install.
        opts.claude_skills_dir = _canonicalize_dir(opts.claude_skills_dir)
        warn_about_plugin_collision(opts)

    # Run path-shape and canonical-asset checks before any copy.
    for check in (_validate_no_retired_tokens, _validate_skill_md_paths,
                  _validate_no_sigil_refs, _validate_reference_depth,
                  _check_canonical_assets, _check_role_template_parity,
                  _check_skill_asset_closure, _check_canonical_mentions):
        if not check():
            return 1

    if opts.validate_only:
        print("Validation passed: plugin content is install-clean.")
        return 0

    install(opts)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except InstallError:
        sys.exit(1)
