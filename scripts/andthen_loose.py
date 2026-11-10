"""Loose-skill channel: copy AndThen skills into an agent skills directory as
`andthen-<name>`, for hosts and setups that cannot take the plugin.

`scripts/andthen.py install --loose` drives this module, and
`scripts/validate-plugin.py` imports its shared content checks.

Stdlib only, Python 3.9+: the installer runs wherever the plugin is cloned,
before anything is installed.

Skills come from plugin/skills, each exported as a directory named
andthen-<skill-name>/ and fully self-contained: shared assets at
plugin/references/ are inlined into each consuming skill's references/, and
../../references/ paths and the andthen: namespace are rewritten to local form.
Existing owned skill directories are replaced from a validated staged bundle, so
files removed from the current release do not survive an upgrade.
"""

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))

SKILLS_ROOT = REPO_ROOT / "plugin" / "skills"
REFERENCES_ROOT = REPO_ROOT / "plugin" / "references"

# Fixed since ADR-030: a custom prefix served one white-label downstream.
PREFIX = "andthen-"

# ---------------------------------------------------------------------------
# Canonical install-inlined assets at plugin/references/ - consumed by one or
# more skills. Inlined into each consuming skill's references/ at install time
# so the installed bundle is self-contained (no path leaves the skill root).
#
# The table spelling is `name="a.md b.md"`, unchanged from the shell version:
# the error messages and the docs name these variables, and a skill author
# editing them finds the same shape.
# ---------------------------------------------------------------------------

# Names of the canonical shared assets (filenames only). A reference's `.json`
# schema is a canonical of its own: it ships beside the reference and is read
# with it, so it travels into every consuming bundle the same way.
# Each must exist at plugin/references/<asset> and be listed by every consuming skill.
_canonical_assets="design-tree.md fis-contract.md fis-mutability.md intent-and-rules-context.md lens-adversarial.md plan-schema.md plan.schema.json project-document-templates.md review-calibration.md self-review.md unattended-runs.md verification-evidence.md"

# Per-skill declarations: `_skill_assets_<skill with - as _>` names the canonical
# assets that skill consumes. Only skills that reference ../../references/<asset>
# are listed, and the declaration must equal what the skill's own files reference
# - _check_skill_asset_closure proves both directions before any copy.
_skill_assets_plan="fis-contract.md plan-schema.md plan.schema.json self-review.md unattended-runs.md"
_skill_assets_exec_plan="fis-contract.md fis-mutability.md plan-schema.md unattended-runs.md verification-evidence.md"
_skill_assets_review="fis-contract.md fis-mutability.md intent-and-rules-context.md lens-adversarial.md plan-schema.md review-calibration.md unattended-runs.md verification-evidence.md"
_skill_assets_architecture="review-calibration.md unattended-runs.md"
_skill_assets_domain="review-calibration.md unattended-runs.md"
_skill_assets_decide="design-tree.md review-calibration.md unattended-runs.md"
_skill_assets_clarify="design-tree.md self-review.md"
_skill_assets_testing="unattended-runs.md verification-evidence.md"
_skill_assets_triage="unattended-runs.md verification-evidence.md"
_skill_assets_init="project-document-templates.md"
# describe merges what map-codebase and ubiquitous-language each consumed.
_skill_assets_describe="project-document-templates.md"
_skill_assets_implement_fix="fis-mutability.md plan-schema.md review-calibration.md unattended-runs.md verification-evidence.md"
_skill_assets_ship="plan-schema.md unattended-runs.md verification-evidence.md"
_skill_assets_now_what="plan-schema.md"
_skill_assets_ui_ux_design="unattended-runs.md"
_skill_assets_simplify_code="unattended-runs.md verification-evidence.md"
_skill_assets_tracker="unattended-runs.md"

CANONICAL_ASSETS = _canonical_assets.split()

CANONICAL_PREFIX = "../../references/"


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
# Skill selection
# ---------------------------------------------------------------------------

def _available_skills():
    return ",".join(sorted(child.name for child in SKILLS_ROOT.iterdir() if child.is_dir()))


def _normalize_selected_skills(raw):
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
        if name.startswith(PREFIX):
            name = name[len(PREFIX):]

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


# ---------------------------------------------------------------------------
# Destination canonicalization
#
# A relative --skills-dir resolves against the launch directory, so it is made
# absolute once and every staged, checked, and reported path agrees.
# ---------------------------------------------------------------------------

def _canonicalize_dir(path, dry_run=False):
    # An empty destination would otherwise resolve to the launch directory
    # (typically the repo root) and install there. Reject it loudly.
    if not path:
        err("error: cannot canonicalize empty path (got empty destination argument)")
        raise InstallError()
    if os.path.isabs(path):
        return path
    if dry_run:  # a dry run writes nothing, not even the directory
        return os.path.normpath(os.path.join(os.getcwd(), path))
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


# ---------------------------------------------------------------------------
# Content checks shared with scripts/validate-plugin.py. The install runs the
# two that decide whether a bundle comes out whole; the rest run in CI's
# validator, which every tree an end user installs from passed (ADR-030).
# ---------------------------------------------------------------------------

def _each_source_skill():
    """(skill dir, skill name) for every skill in the plugin dir."""
    for skill_dir in sorted(SKILLS_ROOT.iterdir(), key=lambda p: p.name):
        if skill_dir.is_dir() and not skill_dir.name.startswith("."):
            yield skill_dir, skill_dir.name


def _check_canonical_assets():
    """Every canonical exists before any copy starts."""
    for asset in CANONICAL_ASSETS:
        if not (REFERENCES_ROOT / asset).is_file():
            err("error: %s/%s not found; cannot inline for consuming skills"
                % (REFERENCES_ROOT, asset))
            return False
    return True


CANONICAL_LOAD = re.compile(r"\.\./\.\./references/[A-Za-z0-9._-]+\.(?:md|json)")


def _direct_canonical_refs(path):
    """The canonicals a path loads: a load is a ../../references/ path in any of
    its markdown files, link or code span alike. A bare backticked filename loads
    nothing - it is a mention, checked by the validator's _check_canonical_mentions."""
    found = set()
    for markdown in markdown_files(path):
        for match in CANONICAL_LOAD.finditer(read_text(markdown)):
            found.add(match.group(0).rsplit("/", 1)[1])
    return sorted(found)


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
    leave it. Only SKILL.md can carry this prefix - the validator's
    _validate_reference_depth forbids any other file in a skill from pathing to
    another file."""
    substitute(Path(directory) / "SKILL.md", CANONICAL_PREFIX, "references/")


def rewrite_namespace_dir(directory):
    for markdown in markdown_files(directory):
        rewrite_namespace_file(markdown)


def rewrite_namespace_file(markdown):
    """andthen:<x> -> andthen-<x>. Shipped content is sigil-free by contract
    (CI's validator, _validate_no_sigil_refs), so this catch-all suffices."""
    text = read_text(markdown)
    rewritten = text.replace("andthen:", PREFIX)
    if rewritten != text:
        write_text(markdown, rewritten)


def rewrite_skill_openai_metadata(skill_dir):
    openai_yaml = Path(skill_dir) / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        rewrite_namespace_file(openai_yaml)


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

def install_skill(source_skill, skill, destination, dry_run):
    """Stage, inline, rewrite, verify, then replace one installed skill bundle."""
    if dry_run:
        copy_dir_contents(source_skill, destination, True)
        inline_canonical_assets(destination, skill, REFERENCES_ROOT, True)
        return

    stage = stage_skill_dir(source_skill, destination)
    if stage is None:
        err("error: failed to stage skill %s" % skill)
        raise InstallError()
    try:
        # Inlining runs first so the inlined files are namespace-rewritten in the
        # same pass.
        inline_canonical_assets(stage, skill, REFERENCES_ROOT, False)
        rewrite_canonical_refs_dir(stage)
        rewrite_namespace_dir(stage)
        rewrite_skill_openai_metadata(stage)
        if not _check_rewritten_canonical_refs(stage, skill):
            raise InstallError()
        replace_owned_skill_dir(stage, destination)
    except InstallError:
        shutil.rmtree(str(stage), ignore_errors=True)
        raise


def default_skills_dir():
    return os.path.join(os.path.expanduser("~"), ".agents", "skills")


def install(skills_dir, selected_raw="", dry_run=False):
    """Install the selected skills (default all) into skills_dir. Returns
    (skill count, absolute destination); raises InstallError with its message
    already printed."""
    selected = _normalize_selected_skills(selected_raw)
    skills_dir = _canonicalize_dir(skills_dir, dry_run)
    for check in (_check_canonical_assets, _check_skill_asset_closure):
        if not check():
            raise InstallError()

    count = 0
    for skill_dir, skill in _each_source_skill():
        if selected and skill not in selected:
            continue
        install_skill(skill_dir, skill, Path(skills_dir) / (PREFIX + skill), dry_run)
        count += 1
    return count, skills_dir
