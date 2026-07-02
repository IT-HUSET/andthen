#!/usr/bin/env bash

# pipefail surfaces early-pipeline failures (e.g. find errors before sort) that
# would otherwise be swallowed because the pipeline's exit status defaults to
# the last command's. With pipefail, an unreadable directory inside `find ...
# | sort` aborts the script under `set -e` instead of silently producing an
# empty list. Requires bash; the shebang switched from `sh` for this reason.
set -euo pipefail

usage() {
  cat <<'EOF'
Install AndThen skills into an agent skills directory and install review agents.

Usage:
  ./scripts/install-skills.sh [options]

Options:
  --skills-dir PATH         Destination for skill directories (default: ~/.agents/skills)
  --codex-agents-dir PATH   Destination for Codex agent TOML files (default: ~/.codex/agents)
  --no-codex-agents         Skip Codex agent installation
  --claude                  Also install skills for Claude Code at the user-level
                            defaults (~/.claude/skills and ~/.claude/agents),
                            using the same <prefix> so invocation is
                            /<prefix><name>.
                            (Set implicitly by --claude-skills-dir or
                            --claude-agents-dir.)
                            Alternative to the Claude Code plugin. Safe to combine
                            with the plugin only when --prefix differs from the
                            default (andthen-); same prefix would expose duplicate
                            skills.
  --claude-skills-dir PATH  Override the Claude Code skills destination (implies a
                            Claude Code install). Use to target a project-local
                            location like <project>/.claude/skills for downstream
                            toolkits that bundle AndThen with their own --prefix.
  --claude-agents-dir PATH  Override the Claude Code agents destination (implies a
                            Claude Code install). For a clean project-local install
                            pass both --claude-skills-dir and --claude-agents-dir.
  --skills LIST             Comma-separated source skill names to install
                            (default: all). Example: clarify,prd,review.
                            Names may be unprefixed or use the current exported
                            prefix (e.g. andthen-prd with the default prefix).
  --prefix PREFIX           Prefix for exported names (letters, numbers, '_',
                            and '-' only; must end with '-'; default: andthen-)
  --display-brand BRAND     Human-readable brand name substituted for "AndThen"
                            in installed skill agents/openai.yaml files and
                            generated/copied agent prompts.
                            Default: AndThen (no rewrite). Use for white-label
                            installs where the namespace prefix is not
                            "andthen-" (e.g. --prefix dartclaw- pairs with
                            --display-brand DartClaw).
  --dry-run                 Print planned operations without copying files
  -h, --help                Show this help text

Notes:
  - All skills are exported as directories named <prefix><skill-name>/
  - Codex agents are generated at install time from plugin/agents/*.md
    (Claude Code agent files are the source of truth) and written as
    <prefix><agent-name>.toml into --codex-agents-dir.
  - Claude Code agents installed through --claude / --claude-user or
    --claude-agents-dir are plain .md copies of plugin/agents/*.md, with
    the frontmatter `name:` prefixed to match the installed filename.
  - When --skills is set, only those source skills are exported. Missing names
    fail before any install work starts.
  - Skills are fully self-contained at install time: each skill owns its
    references/, templates/, and scripts/ locally. Shared assets at
    plugin/references/ are inlined into each consuming skill's references/
    and ${CLAUDE_PLUGIN_ROOT} paths are rewritten to local-relative form,
    alongside the andthen: → <prefix> namespace rewrite.
  - Existing skill and agent files are overwritten in place, but stale files
    are not deleted.
  - Skipping the Claude Code install on a later run does NOT remove previously
    installed <claude-skills-dir>/<prefix>* or
    <claude-agents-dir>/<prefix>*.md –
    delete those manually if switching back to the Claude Code plugin as the
    primary path or relocating the install.
  - Removing, renaming, or deselecting agents does NOT remove previously
    generated <codex-agents-dir>/<prefix>*.toml or
    <claude-agents-dir>/<prefix>*.md – delete stale generated agents manually
    if you need the visible agent set to exactly match plugin/agents/.
EOF
}

repo_root=$(
  CDPATH= cd -- "$(dirname -- "$0")/.." && pwd
)

skills_dir="${HOME}/.agents/skills"
codex_agents_dir="${HOME}/.codex/agents"
claude_skills_dir="${HOME}/.claude/skills"
claude_agents_dir="${HOME}/.claude/agents"
install_codex_agents=1
install_claude_user=0
prefix="andthen-"
display_brand="AndThen"
dry_run=0
selected_skills_raw=""
selected_skills=""

require_option_value() {
  _rov_option="$1"
  _rov_value="${2-}"
  if [ -z "$_rov_value" ]; then
    printf 'error: %s requires a value\n' "$_rov_option" >&2
    exit 1
  fi
}

validate_prefix() {
  case "$prefix" in
    *-)
      ;;
    *)
      printf 'error: --prefix must end with `-` (got %s)\n' "$prefix" >&2
      exit 1
      ;;
  esac
  case "$prefix" in
    *[!a-zA-Z0-9_-]*)
      printf 'error: --prefix may only contain letters, numbers, `_`, and `-` (got %s)\n' "$prefix" >&2
      exit 1
      ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skills-dir)
      require_option_value "$1" "${2-}"
      skills_dir="$2"
      shift 2
      ;;
    --codex-agents-dir)
      require_option_value "$1" "${2-}"
      codex_agents_dir="$2"
      shift 2
      ;;
    --no-codex-agents)
      install_codex_agents=0
      shift
      ;;
    --claude|--claude-user)
      install_claude_user=1
      shift
      ;;
    --claude-skills-dir)
      require_option_value "$1" "${2-}"
      claude_skills_dir="$2"
      install_claude_user=1
      shift 2
      ;;
    --claude-agents-dir)
      require_option_value "$1" "${2-}"
      claude_agents_dir="$2"
      install_claude_user=1
      shift 2
      ;;
    --skills)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        printf 'error: --skills requires a comma-separated list of skill names\n' >&2
        exit 1
      fi
      selected_skills_raw="$2"
      shift 2
      ;;
    --prefix)
      require_option_value "$1" "${2-}"
      prefix="$2"
      shift 2
      ;;
    --display-brand)
      require_option_value "$1" "${2-}"
      display_brand="$2"
      if [ -z "$display_brand" ]; then
        printf 'error: --display-brand requires a non-empty value\n' >&2
        exit 1
      fi
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

validate_prefix

_available_skills() {
  find "$repo_root/plugin/skills" -mindepth 1 -maxdepth 1 -type d \
    -exec basename {} \; | LC_ALL=C sort | paste -sd, -
}

_normalize_selected_skills() {
  _nss_raw="$1"
  selected_skills=""
  [ -z "$_nss_raw" ] && return 0
  case "$_nss_raw" in
    ,*|*,|*,,*)
      printf 'error: --skills contains an empty skill name in %s\n' "$_nss_raw" >&2
      return 1
      ;;
  esac

  IFS=',' read -r -a _nss_items <<< "$_nss_raw"
  for _nss_token in "${_nss_items[@]}"; do
    # Source skill names never contain whitespace; trimming lets users write
    # "clarify, prd" without carrying the space into validation.
    _nss_name=$(printf '%s' "$_nss_token" | tr -d '[:space:]')
    if [ -z "$_nss_name" ]; then
      printf 'error: --skills contains an empty skill name in %s\n' "$_nss_raw" >&2
      return 1
    fi

    case "$_nss_name" in
      /andthen:*) _nss_name="${_nss_name#/andthen:}" ;;
      andthen:*)  _nss_name="${_nss_name#andthen:}" ;;
    esac
    case "$_nss_name" in
      "$prefix"*) _nss_name="${_nss_name#"$prefix"}" ;;
      andthen-*)  _nss_name="${_nss_name#andthen-}" ;;
    esac

    if [ -z "$_nss_name" ]; then
      printf 'error: --skills contains an empty skill name in %s\n' "$_nss_raw" >&2
      return 1
    fi
    case "$_nss_name" in
      *[!a-zA-Z0-9_-]*)
        printf 'error: invalid skill name in --skills: %s\n' "$_nss_name" >&2
        printf 'available skills: %s\n' "$(_available_skills)" >&2
        return 1
        ;;
    esac

    if [ ! -d "$repo_root/plugin/skills/$_nss_name" ]; then
      printf 'error: unknown skill in --skills: %s\n' "$_nss_name" >&2
      printf 'available skills: %s\n' "$(_available_skills)" >&2
      return 1
    fi

    case " $selected_skills " in
      *" $_nss_name "*) ;;
      *) selected_skills="${selected_skills}${selected_skills:+ }$_nss_name" ;;
    esac
  done
}

_should_install_skill() {
  _sis_name="$1"
  [ -z "$selected_skills" ] && return 0
  case " $selected_skills " in
    *" $_sis_name "*) return 0 ;;
    *) return 1 ;;
  esac
}

_normalize_selected_skills "$selected_skills_raw" || exit 1

# Canonicalize install destinations to absolute paths. The Codex-tier
# ${CLAUDE_SKILL_DIR} rewrite bakes this path into installed .md files, so
# a relative --skills-dir would produce broken bash invocations at runtime
# (the agent's cwd at invocation time is not guaranteed to be the directory
# install-skills.sh ran from). The default values are already absolute
# (${HOME}/...); this only matters when the user passes a destination flag with
# a relative argument.
_canonicalize_dir() {
  _cd_path="$1"
  # Empty input would silently fall through: bash treats `cd ""` as a no-op
  # that keeps cwd, so `pwd` returns the script's working directory and the
  # install proceeds to write into whatever directory it was launched from
  # (typically the repo root). Reject up-front so the failure is loud.
  if [ -z "$_cd_path" ]; then
    printf 'error: cannot canonicalize empty path (got empty destination argument)\n' >&2
    return 1
  fi
  case "$_cd_path" in
    /*) printf '%s' "$_cd_path" ;;
    *)
      # Resolve relative paths against the current working directory. If
      # the path doesn't exist yet, mkdir -p creates it so `cd` can
      # succeed; install would create it later anyway. Capture mkdir's
      # stderr so a failure here surfaces the underlying cause (permission
      # denied, ENOTDIR on a parent that's a file, etc.) rather than
      # collapsing into a generic "mkdir/cd failed" message.
      _cd_mkdir_err=$(mkdir -p "$_cd_path" 2>&1)
      _cd_mkdir_status=$?
      _cd_resolved=$( CDPATH= cd -- "$_cd_path" 2>/dev/null && pwd )
      if [ -z "$_cd_resolved" ]; then
        # Fail loud rather than fall through to the original (relative)
        # path. The Codex-tier ${CLAUDE_SKILL_DIR} rewrite bakes this path
        # into installed .md files, so a relative result here would silently
        # produce broken bash invocations at runtime – the exact failure
        # the comment block above this function says it is preventing.
        if [ "$_cd_mkdir_status" -ne 0 ] && [ -n "$_cd_mkdir_err" ]; then
          printf 'error: cannot canonicalize directory %s (mkdir failed: %s)\n' "$_cd_path" "$_cd_mkdir_err" >&2
        else
          printf 'error: cannot canonicalize directory %s (mkdir/cd failed)\n' "$_cd_path" >&2
        fi
        return 1
      fi
      printf '%s' "$_cd_resolved"
      ;;
  esac
}
skills_dir=$(_canonicalize_dir "$skills_dir") || exit 1

if [ "$install_codex_agents" -eq 1 ]; then
  codex_agents_dir=$(_canonicalize_dir "$codex_agents_dir") || exit 1
fi

if [ "$install_claude_user" -eq 1 ]; then
  # Canonicalize only when the Claude user-tier install is requested. Otherwise
  # the calls would pre-create ~/.claude/skills and ~/.claude/agents (via mkdir -p inside
  # _canonicalize_dir) on every install, even for plugin-only / Codex-only
  # invocations that never write there.
  claude_skills_dir=$(_canonicalize_dir "$claude_skills_dir") || exit 1
  claude_agents_dir=$(_canonicalize_dir "$claude_agents_dir") || exit 1

  # Claude Code plugin cache layout is not a stable public contract. Check the
  # current (cache/<marketplace>/andthen) layout plus a direct cache/andthen
  # fallback. Best-effort only – if Claude Code changes the path entirely, the
  # warning silently stops firing and the user can still see the plugin via
  # /plugin list.
  _plugin_found=0
  for candidate in "${HOME}/.claude/plugins/cache"/*"/andthen" "${HOME}/.claude/plugins/cache/andthen"; do
    [ -d "$candidate" ] || continue
    _plugin_found=1
    break
  done
  # Only warn when prefixes would actually collide AND both install paths are
  # going to the user-tier defaults. Downstream tools that wrap this installer
  # with their own --prefix (e.g. dartclaw-) or redirect --claude-*-dir
  # coexist with the AndThen plugin under disjoint namespaces or scopes and
  # shouldn't see this warning.
  if [ "$_plugin_found" -eq 1 ] \
     && [ "$prefix" = "andthen-" ] \
     && [ "$claude_skills_dir" = "${HOME}/.claude/skills" ] \
     && [ "$claude_agents_dir" = "${HOME}/.claude/agents" ]; then
    printf 'warning: Claude user-tier install enabled with the default prefix and user-tier paths but an andthen Claude Code plugin install appears present under ~/.claude/plugins/. Running both will create duplicate skills under andthen:<name> (plugin) and andthen-<name> (user). Uninstall the plugin (/plugin uninstall andthen) before using the user-tier install, pass a distinct --prefix, or target project-local --claude-skills-dir / --claude-agents-dir to coexist.\n' >&2
  fi

  _claude_skills_default=0
  _claude_agents_default=0
  [ "$claude_skills_dir" = "${HOME}/.claude/skills" ] && _claude_skills_default=1
  [ "$claude_agents_dir" = "${HOME}/.claude/agents" ] && _claude_agents_default=1
  if [ "$_claude_skills_default" -ne "$_claude_agents_default" ]; then
    printf 'warning: --claude-skills-dir and --claude-agents-dir are split between project and user tier (skills=%s, agents=%s). For a clean project-local install pass both; for a user-tier install pass neither.\n' \
      "$claude_skills_dir" "$claude_agents_dir" >&2
  fi
fi

# ---------------------------------------------------------------------------
# Canonical install-inlined assets at plugin/references/ – consumed by one or more skills.
# Inlined into each consuming skill's references/ at install time so the
# installed bundle is self-contained (no ${CLAUDE_PLUGIN_ROOT} at runtime).
# ---------------------------------------------------------------------------

# Names of the canonical shared assets (filenames only).
# Each must exist at plugin/references/<asset>.md and be listed by every consuming skill.
_canonical_assets="automation-mode.md critic-calibration.md data-contract.md design-tree.md execution-discipline.md execution-named-blocks.md farley-framework.md findings-filter-templates.md fis-authoring-guidelines.md fis-template.md github-publish.md intent-and-rules-context.md lens-adversarial.md plan-issue-shape.md plan-schema.md prd-template.md project-state-templates.md reconciliation-ledger.md review-calibration.md review-report-location.md trust-boundaries.md"

# Map of skill-name → space-separated list of canonical asset names it consumes.
# Only skills that reference ${CLAUDE_PLUGIN_ROOT}/references/<asset> are listed.
_skill_assets_prd="automation-mode.md data-contract.md execution-discipline.md github-publish.md plan-issue-shape.md plan-schema.md prd-template.md"
_skill_assets_plan="automation-mode.md data-contract.md execution-discipline.md fis-authoring-guidelines.md github-publish.md plan-issue-shape.md plan-schema.md"
_skill_assets_spec="automation-mode.md data-contract.md execution-discipline.md execution-named-blocks.md fis-authoring-guidelines.md fis-template.md plan-issue-shape.md plan-schema.md"
_skill_assets_exec_spec="automation-mode.md data-contract.md execution-discipline.md execution-named-blocks.md github-publish.md plan-issue-shape.md plan-schema.md reconciliation-ledger.md"
_skill_assets_exec_plan="automation-mode.md data-contract.md execution-discipline.md github-publish.md plan-issue-shape.md plan-schema.md reconciliation-ledger.md"
_skill_assets_ops="data-contract.md fis-authoring-guidelines.md plan-issue-shape.md plan-schema.md project-state-templates.md reconciliation-ledger.md"
_skill_assets_review="critic-calibration.md data-contract.md findings-filter-templates.md fis-authoring-guidelines.md intent-and-rules-context.md lens-adversarial.md plan-issue-shape.md plan-schema.md reconciliation-ledger.md review-calibration.md review-report-location.md trust-boundaries.md"
_skill_assets_quick_review="critic-calibration.md intent-and-rules-context.md lens-adversarial.md reconciliation-ledger.md review-calibration.md"
_skill_assets_architecture="design-tree.md farley-framework.md findings-filter-templates.md project-state-templates.md review-calibration.md review-report-location.md"
_skill_assets_clarify="data-contract.md design-tree.md github-publish.md plan-issue-shape.md plan-schema.md"
_skill_assets_testing="farley-framework.md"
_skill_assets_quick_implement="automation-mode.md execution-discipline.md execution-named-blocks.md"
_skill_assets_e2e_test="trust-boundaries.md"
_skill_assets_triage="automation-mode.md data-contract.md execution-discipline.md execution-named-blocks.md github-publish.md plan-issue-shape.md plan-schema.md trust-boundaries.md"
_skill_assets_init="project-state-templates.md"
_skill_assets_map_codebase="project-state-templates.md"
_skill_assets_simplify_code="automation-mode.md execution-discipline.md intent-and-rules-context.md"
_skill_assets_refactor="automation-mode.md execution-discipline.md"
_skill_assets_remediate_findings="automation-mode.md execution-discipline.md intent-and-rules-context.md reconciliation-ledger.md"
_skill_assets_preflight="automation-mode.md execution-discipline.md execution-named-blocks.md"

_skills_with_canonical_assets="prd plan spec exec-spec exec-plan ops review quick-review architecture clarify testing quick-implement e2e-test triage init map-codebase simplify-code refactor remediate-findings preflight"

# Resolve the list of canonical assets for a given skill base name.
# Prints a space-separated list of asset filenames.
_get_skill_assets() {
  _gsa_name="$1"
  case "$_gsa_name" in
    prd)      printf '%s' "$_skill_assets_prd" ;;
    plan)     printf '%s' "$_skill_assets_plan" ;;
    spec)     printf '%s' "$_skill_assets_spec" ;;
    exec-spec) printf '%s' "$_skill_assets_exec_spec" ;;
    exec-plan) printf '%s' "$_skill_assets_exec_plan" ;;
    ops)      printf '%s' "$_skill_assets_ops" ;;
    review)   printf '%s' "$_skill_assets_review" ;;
    quick-review) printf '%s' "$_skill_assets_quick_review" ;;
    architecture) printf '%s' "$_skill_assets_architecture" ;;
    clarify)  printf '%s' "$_skill_assets_clarify" ;;
    testing)  printf '%s' "$_skill_assets_testing" ;;
    quick-implement) printf '%s' "$_skill_assets_quick_implement" ;;
    e2e-test) printf '%s' "$_skill_assets_e2e_test" ;;
    triage)   printf '%s' "$_skill_assets_triage" ;;
    init)     printf '%s' "$_skill_assets_init" ;;
    map-codebase) printf '%s' "$_skill_assets_map_codebase" ;;
    simplify-code) printf '%s' "$_skill_assets_simplify_code" ;;
    refactor) printf '%s' "$_skill_assets_refactor" ;;
    remediate-findings) printf '%s' "$_skill_assets_remediate_findings" ;;
    preflight) printf '%s' "$_skill_assets_preflight" ;;
    *)        printf '' ;;
  esac
}

# ---------------------------------------------------------------------------
# Strict-syntax validation: reject bare $CLAUDE_PLUGIN_ROOT (no braces) in
# plugin/skills/ and plugin/references/ before any copy. Only the braces
# form ${CLAUDE_PLUGIN_ROOT} is accepted.
# ---------------------------------------------------------------------------
_validate_plugin_root_syntax() {
  _vprs_found=0
  # Match the bare form: $CLAUDE_PLUGIN_ROOT followed by anything other than `{`.
  # `[^{]` is required (not `[^}]`) to also catch end-of-line / end-of-file
  # occurrences – `[^}]` requires *some* character to follow and silently
  # passes a bare token at EOL, which would violate the strict-braces rule.
  _vprs_list=$(grep -rElZ '\$CLAUDE_PLUGIN_ROOT([^{]|$)' \
    "$repo_root/plugin/skills" \
    "$repo_root/plugin/references" 2>/dev/null | tr '\0' '\n' || true)
  if [ -n "$_vprs_list" ]; then
    printf '%s\n' "$_vprs_list" | while IFS= read -r _vprs_file; do
      [ -z "$_vprs_file" ] && continue
      # grep -m1 (not `| head -1`): under pipefail, head exiting early would
      # SIGPIPE grep and trip the pipeline's exit status.
      _vprs_line=$(grep -m1 -nE '\$CLAUDE_PLUGIN_ROOT([^{]|$)' "$_vprs_file")
      printf 'error: %s:%s uses bare $CLAUDE_PLUGIN_ROOT; only the braces form ${CLAUDE_PLUGIN_ROOT} is accepted\n' \
        "$_vprs_file" "$_vprs_line" >&2
    done
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# Strict-syntax validation: reject bare $CLAUDE_SKILL_DIR (no braces). Only
# the braces form ${CLAUDE_SKILL_DIR} is accepted, mirroring the
# ${CLAUDE_PLUGIN_ROOT} rule. This is the Anthropic-documented substitution
# for skill-bundled resources (scripts/, templates/, references/) – see
# code.claude.com/docs/en/skills.md "Available string substitutions".
# ---------------------------------------------------------------------------
_validate_skill_dir_syntax() {
  # See _validate_plugin_root_syntax above – `([^{]|$)` (not `[^}]`) catches
  # bare tokens at end-of-line / end-of-file.
  _vsds_list=$(grep -rElZ '\$CLAUDE_SKILL_DIR([^{]|$)' \
    "$repo_root/plugin/skills" \
    "$repo_root/plugin/references" 2>/dev/null | tr '\0' '\n' || true)
  if [ -n "$_vsds_list" ]; then
    printf '%s\n' "$_vsds_list" | while IFS= read -r _vsds_file; do
      [ -z "$_vsds_file" ] && continue
      # See _validate_plugin_root_syntax: grep -m1, not `| head -1`.
      _vsds_line=$(grep -m1 -nE '\$CLAUDE_SKILL_DIR([^{]|$)' "$_vsds_file")
      printf 'error: %s:%s uses bare $CLAUDE_SKILL_DIR; only the braces form ${CLAUDE_SKILL_DIR} is accepted\n' \
        "$_vsds_file" "$_vsds_line" >&2
    done
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# Canonical-asset existence check: verify all canonical assets exist before
# any copy starts. Missing canonical exits non-zero with a clear error.
# ---------------------------------------------------------------------------
_check_canonical_assets() {
  _cca_refs_dir="$repo_root/plugin/references"
  for _cca_asset in $_canonical_assets; do
    if [ ! -f "$_cca_refs_dir/$_cca_asset" ]; then
      printf 'error: %s/%s not found; cannot inline for consuming skills\n' \
        "$_cca_refs_dir" "$_cca_asset" >&2
      return 1
    fi
  done
  return 0
}

_asset_list_contains() {
  _alc_needle="$1"
  shift
  for _alc_asset in "$@"; do
    [ "$_alc_asset" = "$_alc_needle" ] && return 0
  done
  return 1
}

# Verify each declared skill asset list includes canonical dependencies named
# by the canonical files it already inlines. This keeps installed bundles
# self-contained when shared references point at other shared references.
_check_skill_asset_closure() {
  _csac_missing=0
  for _csac_skill in $_skills_with_canonical_assets; do
    _csac_assets=$(_get_skill_assets "$_csac_skill")
    [ -z "$_csac_assets" ] && continue
    for _csac_asset in $_csac_assets; do
      _csac_src="$repo_root/plugin/references/$_csac_asset"
      _csac_refs=$({ \
          grep -ohE '\$\{CLAUDE_PLUGIN_ROOT\}/references/[A-Za-z0-9._-]+\.md' "$_csac_src" 2>/dev/null || true; \
          grep -ohE '\]\([A-Za-z0-9._-]+\.md(#[^)]+)?\)' "$_csac_src" 2>/dev/null || true; \
        } \
        | sed -E 's|.*references/||; s|^\]\(([A-Za-z0-9._-]+\.md).*$|\1|' \
        | LC_ALL=C sort -u || true)
      [ -z "$_csac_refs" ] && continue
      for _csac_dep in $_csac_refs; do
        case " $_canonical_assets " in
          *" $_csac_dep "*) ;;
          *) continue ;;
        esac
        if ! _asset_list_contains "$_csac_dep" $_csac_assets; then
          printf 'error: %s inlines %s, which references %s, but %s is not in _skill_assets_%s\n' \
            "$_csac_skill" "$_csac_asset" "$_csac_dep" "$_csac_dep" "$(printf '%s' "$_csac_skill" | tr '-' '_')" >&2
          _csac_missing=1
        fi
      done
    done
  done
  [ "$_csac_missing" -eq 0 ]
}

# ---------------------------------------------------------------------------
# inline_canonical_assets: copy canonical assets into a skill's references/.
# Each consuming skill gets its relevant canonical assets as local files.
# Canonicals carry no source: frontmatter, so this is a pure cp (no stripping).
# Args: $1 = installed skill dir, $2 = skill base name (e.g. "prd")
# ---------------------------------------------------------------------------
inline_canonical_assets() {
  _ica_dst="$1"
  _ica_skill_name="$2"
  _ica_assets=$(_get_skill_assets "$_ica_skill_name")
  [ -z "$_ica_assets" ] && return 0
  for _ica_asset in $_ica_assets; do
    _ica_src="$repo_root/plugin/references/$_ica_asset"
    if [ ! -f "$_ica_src" ]; then
      printf 'error: %s not found; cannot inline for %s\n' "$_ica_src" "$_ica_dst" >&2
      return 1
    fi
    if [ "$dry_run" -eq 1 ]; then
      printf 'mkdir -p %s/references\n' "$_ica_dst"
      printf 'cp %s %s/references/%s\n' "$_ica_src" "$_ica_dst" "$_ica_asset"
    else
      mkdir -p "$_ica_dst/references"
      cp "$_ica_src" "$_ica_dst/references/$_ica_asset"
    fi
  done
}

# ---------------------------------------------------------------------------
# rewrite_plugin_root_file: rewrite ${CLAUDE_PLUGIN_ROOT}/references/<asset>
# to a local path that resolves correctly from the consumer file's location.
#   - Files in <skill>/references/ (immediate children) → <asset>
#     (bare filename, sibling-relative – unambiguous under both file-relative
#     and skill-root-relative semantics).
#   - Files below <skill>/references/<subdir>/ → ../<asset>, ../../<asset>, etc.
#   - Skill-root files → references/<asset>
#   - Other subdirectories → ../references/<asset>, ../../references/<asset>, etc.
# Called after namespace rewrite so the installed bundle has no plugin-root refs.
# ---------------------------------------------------------------------------
rewrite_plugin_root_file() {
  _rprf_md="$1"
  _rprf_skill_dir="$2"
  _rprf_dir=$(dirname "$_rprf_md")

  if [ "$_rprf_dir" = "$_rprf_skill_dir/references" ]; then
    _rprf_replacement=""
  elif [[ "$_rprf_dir" == "$_rprf_skill_dir/references/"* ]]; then
    _rprf_rel=${_rprf_dir#"$_rprf_skill_dir/references"/}
    _rprf_prefix=""
    while :; do
      _rprf_prefix="../$_rprf_prefix"
      case "$_rprf_rel" in
        */*) _rprf_rel=${_rprf_rel#*/} ;;
        *) break ;;
      esac
    done
    _rprf_replacement="$_rprf_prefix"
  elif [ "$_rprf_dir" = "$_rprf_skill_dir" ]; then
    _rprf_replacement="references/"
  else
    case "$_rprf_dir" in
      "$_rprf_skill_dir"/*)
        _rprf_rel=${_rprf_dir#"$_rprf_skill_dir"/}
        _rprf_prefix=""
        while :; do
          _rprf_prefix="../$_rprf_prefix"
          case "$_rprf_rel" in
            */*) _rprf_rel=${_rprf_rel#*/} ;;
            *) break ;;
          esac
        done
        _rprf_replacement="${_rprf_prefix}references/"
        ;;
      *)
        _rprf_replacement="references/"
        ;;
    esac
  fi

  _rprf_replacement_esc=$(printf '%s' "$_rprf_replacement" | sed -e 's/[\\&|]/\\&/g')
  case "$_rprf_replacement" in
    "")
      sed -i.bak 's|\${CLAUDE_PLUGIN_ROOT}/references/||g' "$_rprf_md"
      ;;
    *)
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/references/|$_rprf_replacement_esc|g" "$_rprf_md"
      ;;
  esac
  rm -f "$_rprf_md.bak"
}

rewrite_plugin_root_dir() {
  _rprd_dir="$1"
  # LC_ALL=C sort: filesystem `find` order is non-deterministic across
  # machines; sort makes reinstalls byte-stable.
  _rprd_list=$(find "$_rprd_dir" -name '*.md' -type f | LC_ALL=C sort)
  [ -z "$_rprd_list" ] && return 0
  printf '%s\n' "$_rprd_list" | while IFS= read -r _rprd_md; do
    rewrite_plugin_root_file "$_rprd_md" "$_rprd_dir"
  done
}

# ---------------------------------------------------------------------------
# rewrite_skill_dir_file: rewrite ${CLAUDE_SKILL_DIR} to a fixed absolute
# path baked in at install time. Used for the non-Claude-Code (Codex) tier
# where Claude Code's ${CLAUDE_SKILL_DIR} string substitution is unavailable.
#
# Claude Code's docs (code.claude.com/docs/en/skills.md, "Available string
# substitutions") define ${CLAUDE_SKILL_DIR} as the path to the skill's own
# directory, "regardless of the current working directory". For ~/.claude/
# skills/ installs, Claude Code substitutes the variable natively at runtime,
# so no rewrite is needed. For ~/.agents/skills/ (Codex), there is no such
# substitution; the agentskills.io spec relies on bare skill-root-relative
# paths plus agent-side resolution from the catalog. Baking the absolute
# path is more robust than relying on agent-side inference, and the install
# location is already known at install time.
#
# Args: $1 = consumer .md file, $2 = absolute path to the installed skill dir
# ---------------------------------------------------------------------------
rewrite_skill_dir_file() {
  _rsdf_md="$1"
  _rsdf_skill_abs="$2"
  # Escape sed-replacement specials (\, |, &) in the absolute path. Paths
  # under $HOME rarely contain these but the helper is generic.
  _rsdf_repl=$(printf '%s' "$_rsdf_skill_abs" \
    | sed -e 's/\\/\\\\/g' -e 's/|/\\|/g' -e 's/&/\\&/g')
  sed -i.bak "s|\${CLAUDE_SKILL_DIR}|${_rsdf_repl}|g" "$_rsdf_md"
  rm -f "$_rsdf_md.bak"
}

rewrite_skill_dir_dir() {
  _rsdd_dir="$1"
  _rsdd_skill_abs="$2"
  _rsdd_list=$(find "$_rsdd_dir" -name '*.md' -type f | LC_ALL=C sort)
  [ -z "$_rsdd_list" ] && return 0
  printf '%s\n' "$_rsdd_list" | while IFS= read -r _rsdd_md; do
    rewrite_skill_dir_file "$_rsdd_md" "$_rsdd_skill_abs"
  done
}

copy_dir_contents() {
  src="$1"
  dst="$2"

  if [ "$dry_run" -eq 1 ]; then
    printf 'mkdir -p %s\n' "$dst"
    printf 'cp -R %s/. %s/\n' "$src" "$dst"
    return
  fi

  mkdir -p "$dst"
  cp -R "$src"/. "$dst"/
  # Remove macOS metadata files from exported bundles
  find "$dst" -name '.DS_Store' -delete 2>/dev/null || true
}

# Apply namespace rewrite to a single markdown file.
#   slash_target="$" → Codex sigil form: /andthen:<x> → $<prefix><x>
#   slash_target="/" → Claude user slash-command form: /andthen:<x> → /<prefix><x>
# Anchored on backtick, whitespace, or line-start so that path segments,
# markdown links, and URLs with "/andthen:" substrings are not mangled.
# The slash rule must run before the catch-all so the sigil swap is preserved.
rewrite_namespace_file() {
  md="$1"
  slash_target="$2"
  sed -i.bak "s|\`/andthen:|\`${slash_target}${prefix}|g" "$md"
  rm -f "$md.bak"
  sed -i.bak "s|^/andthen:|${slash_target}${prefix}|g" "$md"
  rm -f "$md.bak"
  sed -i.bak "s|\([[:space:]]\)/andthen:|\1${slash_target}${prefix}|g" "$md"
  rm -f "$md.bak"
  sed -i.bak "s|andthen:|${prefix}|g" "$md"
  rm -f "$md.bak"
}

rewrite_namespace_dir() {
  # Use locally-unique names so this does not clobber the outer for-loop's
  # `dir` variable – POSIX sh has no function-local scope.
  _rwns_dir="$1"
  _rwns_target="$2"
  # Resolve the file list up-front so `set -e` catches find errors. In a
  # `find | while` pipeline the pipeline's exit status is `while`'s, so find
  # failures (e.g. unreadable directory) would be silently swallowed.
  # LC_ALL=C sort makes the iteration byte-stable across machines.
  _rwns_list=$(find "$_rwns_dir" -name '*.md' -type f | LC_ALL=C sort)
  [ -z "$_rwns_list" ] && return 0
  printf '%s\n' "$_rwns_list" | while IFS= read -r md; do
    rewrite_namespace_file "$md" "$_rwns_target"
  done
}

rewrite_review_agent_names_file() {
  _rranf_md="$1"
  _rranf_include_documentation_lookup="${2:-1}"
  # Plugin-tier agent source names are intentionally unprefixed. Installed
  # Codex / Claude user-tier agents are generated or copied with the selected
  # install prefix, so installed prompts must name those prefixed agents.
  if [ "$_rranf_include_documentation_lookup" -eq 1 ]; then
    sed -i.bak "s|\`documentation-lookup\`|\`${prefix}documentation-lookup\`|g" "$_rranf_md"
    rm -f "$_rranf_md.bak"
  fi
  # `research` doubles as a UI/UX mode name and an English word, so it cannot use
  # the bare-token rewrite above. Scope it to the two-token agent reference form.
  sed -i.bak "s|\`research\` agent|\`${prefix}research\` agent|g" "$_rranf_md"
  rm -f "$_rranf_md.bak"
  for _rranf_agent in \
    review-agent-workflow \
    review-architecture \
    review-correctness \
    review-critic \
    review-devils-advocate \
    review-product-requirements \
    review-project-standards \
    review-security \
    review-synthesis-challenger \
    review-testing
  do
    sed -i.bak "s|\`${_rranf_agent}\`|\`${prefix}${_rranf_agent}\`|g" "$_rranf_md"
    rm -f "$_rranf_md.bak"
  done
}

rewrite_review_agent_names_dir() {
  _rrand_dir="$1"
  _rrand_list=$(find "$_rrand_dir" -name '*.md' -type f | LC_ALL=C sort)
  [ -z "$_rrand_list" ] && return 0
  printf '%s\n' "$_rrand_list" | while IFS= read -r _rrand_md; do
    rewrite_review_agent_names_file "$_rrand_md"
  done
}

rewrite_skill_openai_metadata() {
  _rsom_dir="$1"
  _rsom_target_prefix="$2"
  _rsom_yaml="$_rsom_dir/agents/openai.yaml"
  [ -f "$_rsom_yaml" ] || return 0
  rewrite_namespace_file "$_rsom_yaml" "$_rsom_target_prefix"
  rewrite_review_agent_names_file "$_rsom_yaml"
}

# Rewrite the brand-cased token "AndThen" → <display_brand> in the installed
# skill's agents/openai.yaml (display_name, short_description, default_prompt).
# No-op when the brand is the default.
#
# Scope is intentionally narrowed to agents/openai.yaml rather than all *.yaml
# under the skill: the broad form would silently rewrite incidental "AndThen"
# substrings in unrelated yaml (manifests, fixtures, URLs like
# github.com/AndThen/...) introduced later. Field-level scoping inside the
# file is left to sed's substring match – acceptable because the file format
# is small and fully ours.
#
# The brand is escaped for sed-replacement context (\, the chosen delimiter |,
# and & – which would otherwise expand to the matched text). The empty-brand
# case is rejected at arg-parse, so this helper does not need to guard it.
rewrite_display_brand_dir() {
  _rdb_dir="$1"
  _rdb_brand="$2"
  _rdb_yaml="$_rdb_dir/agents/openai.yaml"
  [ -f "$_rdb_yaml" ] || return 0
  rewrite_display_brand_file "$_rdb_yaml" "$_rdb_brand"
}

rewrite_display_brand_file() {
  _rdb_file="$1"
  _rdb_brand="$2"
  [ "$_rdb_brand" = "AndThen" ] && return 0
  _rdb_brand_esc=$(printf '%s' "$_rdb_brand" \
    | sed -e 's/\\/\\\\/g' -e 's/|/\\|/g' -e 's/&/\\&/g')
  sed -i.bak "s|AndThen|${_rdb_brand_esc}|g" "$_rdb_file"
  rm -f "$_rdb_file.bak"
}

install_claude_agent() {
  _ica_src="$1"
  _ica_dst="$2"

  if [ "$dry_run" -eq 1 ]; then
    printf 'mkdir -p %s\n' "$(dirname "$_ica_dst")"
    printf 'cp %s %s\n' "$_ica_src" "$_ica_dst"
    printf '# then prefix frontmatter name, rewrite namespace refs, and apply display brand\n'
    return 0
  fi

  mkdir -p "$(dirname "$_ica_dst")"
  cp "$_ica_src" "$_ica_dst"

  if awk -v p="$prefix" '
    NR == 1 && $0 == "---" { in_fm = 1; print; next }
    in_fm && $0 == "---" { in_fm = 0; print; next }
    in_fm && !done && /^name: / {
      sub(/^name: /, "name: " p)
      done = 1
    }
    { print }
    END { exit done ? 0 : 1 }
  ' "$_ica_dst" > "$_ica_dst.tmp"; then
    mv "$_ica_dst.tmp" "$_ica_dst"
  else
    rm -f "$_ica_dst.tmp" "$_ica_dst"
    printf 'error: %s has no frontmatter `name:` line; cannot install as Claude Code user agent.\n' "$_ica_src" >&2
    return 1
  fi

  rewrite_namespace_file "$_ica_dst" "/"
  # Agent prompts may describe plugin-tier invariants. Keep `documentation-lookup`
  # unprefixed there; frontmatter already makes the installed agent callable.
  rewrite_review_agent_names_file "$_ica_dst" 0
  rewrite_display_brand_file "$_ica_dst" "$display_brand"
}

# Run strict-syntax and canonical-asset checks before any copy.
_validate_plugin_root_syntax || exit 1
_validate_skill_dir_syntax || exit 1
_check_canonical_assets || exit 1
_check_skill_asset_closure || exit 1

skills_count=0
claude_skills_count=0

for dir in "$repo_root/plugin/skills"/*; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  _should_install_skill "$name" || continue

  case "$name" in
    "$prefix"*)
      target_name="$name"
      ;;
    *)
      target_name="$prefix$name"
      ;;
  esac

  # ~/.agents/skills install (Codex discovery) – rewrite with $ sigil form.
  # ${CLAUDE_SKILL_DIR} has no Codex equivalent, so it is replaced with the
  # absolute install path of this skill at install time.
  copy_dir_contents "$dir" "$skills_dir/$target_name"
  # Inline canonical assets for this skill, then rewrite ${CLAUDE_PLUGIN_ROOT} refs
  # to local-relative form. inline_canonical_assets runs before rewrite_namespace_dir
  # so the inlined files also get namespace-rewritten in the same pass.
  if [ "$dry_run" -eq 0 ]; then
    inline_canonical_assets "$skills_dir/$target_name" "$name"
    rewrite_plugin_root_dir "$skills_dir/$target_name"
    rewrite_skill_dir_dir "$skills_dir/$target_name" "$skills_dir/$target_name"
    rewrite_namespace_dir "$skills_dir/$target_name" '$'
    rewrite_review_agent_names_dir "$skills_dir/$target_name"
    rewrite_skill_openai_metadata "$skills_dir/$target_name" '$'
    rewrite_display_brand_dir "$skills_dir/$target_name" "$display_brand"
  else
    inline_canonical_assets "$skills_dir/$target_name" "$name"
  fi
  skills_count=$((skills_count + 1))

  # Optional: Claude Code user-level skills – rewrite with / slash-command form.
  # ${CLAUDE_SKILL_DIR} is left intact: Claude Code substitutes it natively at
  # runtime for both plugin-tier and ~/.claude/skills/ user-tier installs.
  if [ "$install_claude_user" -eq 1 ]; then
    copy_dir_contents "$dir" "$claude_skills_dir/$target_name"
    if [ "$dry_run" -eq 0 ]; then
      inline_canonical_assets "$claude_skills_dir/$target_name" "$name"
      rewrite_plugin_root_dir "$claude_skills_dir/$target_name"
      rewrite_namespace_dir "$claude_skills_dir/$target_name" '/'
      rewrite_review_agent_names_dir "$claude_skills_dir/$target_name"
      rewrite_skill_openai_metadata "$claude_skills_dir/$target_name" '/'
      rewrite_display_brand_dir "$claude_skills_dir/$target_name" "$display_brand"
    else
      inline_canonical_assets "$claude_skills_dir/$target_name" "$name"
    fi
    claude_skills_count=$((claude_skills_count + 1))
  fi
done

codex_agents_count=0
if [ "$install_codex_agents" -eq 1 ] && [ -d "$repo_root/plugin/agents" ]; then
  codex_agents_count=$(find "$repo_root/plugin/agents" -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')
  if [ "$dry_run" -eq 1 ]; then
    printf '%s/scripts/generate-codex-agents.sh --agents-src %s/plugin/agents --out-dir %s --prefix %s --display-brand %s\n' \
      "$repo_root" "$repo_root" "$codex_agents_dir" "$prefix" "$display_brand"
  else
    "$repo_root/scripts/generate-codex-agents.sh" \
      --agents-src "$repo_root/plugin/agents" \
      --out-dir "$codex_agents_dir" \
      --prefix "$prefix" \
      --display-brand "$display_brand" >/dev/null
  fi
fi

claude_agents_count=0
if [ "$install_claude_user" -eq 1 ] && [ -d "$repo_root/plugin/agents" ]; then
  for agent in "$repo_root/plugin/agents"/*.md; do
    [ -f "$agent" ] || continue
    agent_name=$(basename "$agent" .md)
    install_claude_agent "$agent" "$claude_agents_dir/${prefix}${agent_name}.md"
    claude_agents_count=$((claude_agents_count + 1))
  done
fi

verb='Installed'
[ "$dry_run" -eq 1 ] && verb='Would install'
printf '%s %s skills into %s\n' "$verb" "$skills_count" "$skills_dir"
if [ "$codex_agents_count" -gt 0 ]; then
  printf '%s %s Codex agents into %s\n' "$verb" "$codex_agents_count" "$codex_agents_dir"
fi
if [ "$claude_skills_count" -gt 0 ]; then
  printf '%s %s Claude Code user skills into %s\n' "$verb" "$claude_skills_count" "$claude_skills_dir"
fi
if [ "$claude_agents_count" -gt 0 ]; then
  printf '%s %s Claude Code user agents into %s\n' "$verb" "$claude_agents_count" "$claude_agents_dir"
fi
exit 0
