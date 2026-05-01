#!/usr/bin/env sh

set -eu

usage() {
  cat <<'EOF'
Install AndThen skills into the agent skills directory and install Codex agents.

Usage:
  ./scripts/install-skills.sh [options]

Options:
  --skills-dir PATH         Destination for skill directories (default: ~/.agents/skills)
  --codex-agents-dir PATH   Destination for Codex agent TOML files (default: ~/.codex/agents)
  --no-codex-agents         Skip Codex agent installation
  --claude-user             Also install skills and agents for Claude Code at the
                            user-level defaults (~/.claude/skills and
                            ~/.claude/agents), using the same <prefix> so invocation
                            is /<prefix><name> on both Claude Code and Codex.
                            (Set implicitly by --claude-skills-dir / --claude-agents-dir.)
                            Alternative to the Claude Code plugin. Safe to combine
                            with the plugin only when --prefix differs from the
                            default (andthen-); same prefix would expose duplicate
                            skills.
  --claude-skills-dir PATH  Override the Claude Code skills destination (implies a
                            Claude Code install). Use to target a project-local
                            location like <project>/.claude/skills for downstream
                            toolkits that bundle AndThen with their own --prefix.
  --claude-agents-dir PATH  Override the Claude Code agents destination (implies a
                            Claude Code install). Counterpart to --claude-skills-dir;
                            for a clean project-local install pass both, otherwise
                            the unset half installs at the user-level default.
  --prefix PREFIX           Prefix for exported names (must end with '-';
                            default: andthen-)
  --display-brand BRAND     Human-readable brand name substituted for "AndThen"
                            in installed skill agents/openai.yaml files
                            (display_name, short_description, default_prompt).
                            Default: AndThen (no rewrite). Use for white-label
                            installs where the namespace prefix is not
                            "andthen-" (e.g. --prefix dartclaw- pairs with
                            --display-brand DartClaw).
  --dry-run                 Print planned operations without copying files
  -h, --help                Show this help text

Notes:
  - All skills are exported as directories named <prefix><skill-name>/
  - Skills are fully self-contained at install time: each skill owns its
    references/, templates/, and scripts/ locally. Shared assets at
    plugin/references/ are inlined into each consuming skill's references/
    and ${CLAUDE_PLUGIN_ROOT} paths are rewritten to local-relative form,
    alongside the andthen: → <prefix> namespace rewrite.
  - Codex agents are generated at install time from plugin/agents/*.md
    (Claude Code agent files are the source of truth) and written as
    <prefix><agent-name>.toml into the codex agents directory
  - Claude Code agents installed for Claude Code (via --claude-user or the
    --claude-*-dir overrides) are plain .md copies of plugin/agents/*.md, with
    the frontmatter `name:` prefixed so Task tool resolution
    (subagent_type: "<prefix><agent>") works.
  - Existing files are overwritten in place, but stale files are not deleted.
  - Skipping the Claude Code install on a later run does NOT remove previously
    installed <claude-skills-dir>/<prefix>* / <claude-agents-dir>/<prefix>*.md —
    delete those manually if switching back to the Claude Code plugin as the
    primary path or relocating the install.
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

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skills-dir)
      skills_dir="$2"
      shift 2
      ;;
    --codex-agents-dir)
      codex_agents_dir="$2"
      shift 2
      ;;
    --no-codex-agents)
      install_codex_agents=0
      shift
      ;;
    --claude-user)
      install_claude_user=1
      shift
      ;;
    --claude-skills-dir)
      claude_skills_dir="$2"
      install_claude_user=1
      shift 2
      ;;
    --claude-agents-dir)
      claude_agents_dir="$2"
      install_claude_user=1
      shift 2
      ;;
    --prefix)
      prefix="$2"
      shift 2
      ;;
    --display-brand)
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

if [ "$install_claude_user" -eq 1 ]; then
  # Claude Code plugin cache layout is not a stable public contract. Check the
  # current (cache/<marketplace>/andthen) layout plus a direct cache/andthen
  # fallback. Best-effort only — if Claude Code changes the path entirely, the
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
  # with their own --prefix (e.g. dartclaw-) or that redirect either path via
  # --claude-skills-dir / --claude-agents-dir coexist with the AndThen plugin
  # under disjoint namespaces or scopes and shouldn't see this warning.
  if [ "$_plugin_found" -eq 1 ] \
     && [ "$prefix" = "andthen-" ] \
     && [ "$claude_skills_dir" = "${HOME}/.claude/skills" ] \
     && [ "$claude_agents_dir" = "${HOME}/.claude/agents" ]; then
    printf 'warning: --claude-user enabled with the default prefix and user-tier paths but an andthen Claude Code plugin install appears present under ~/.claude/plugins/. Running both will create duplicate skills under andthen:<name> (plugin) and andthen-<name> (user). Uninstall the plugin (/plugin uninstall andthen) before using --claude-user, pass a distinct --prefix, or target project-local --claude-skills-dir / --claude-agents-dir to coexist.\n' >&2
  fi

  # Asymmetric override: only one of the two --claude-*-dir flags was redirected
  # away from the user-tier default. Almost certainly a mistake — a "project-local"
  # install that splits skills and agents between project and user tiers is rarely
  # what the caller wants. Warn but don't block; legitimate split-target setups
  # remain possible.
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
# Canonical shared assets at plugin/references/ — consumed by multiple skills.
# Inlined into each consuming skill's references/ at install time so the
# installed bundle is self-contained (no ${CLAUDE_PLUGIN_ROOT} at runtime).
# ---------------------------------------------------------------------------

# Names of the canonical shared assets (filenames only).
# Each must exist at plugin/references/<asset>.md and be consumed by ≥2 skills.
_canonical_assets="adversarial-challenge.md automation-mode.md critic-calibration.md data-contract.md design-tree.md execution-discipline.md farley-framework.md fis-authoring-guidelines.md fis-template.md lens-adversarial.md prd-template.md project-state-templates.md review-calibration.md review-report-location.md trust-boundaries.md"

# Map of skill-name → space-separated list of canonical asset names it consumes.
# Only skills that reference ${CLAUDE_PLUGIN_ROOT}/references/<asset> are listed.
_skill_assets_prd="automation-mode.md prd-template.md"
_skill_assets_plan="automation-mode.md fis-authoring-guidelines.md fis-template.md prd-template.md"
_skill_assets_spec="automation-mode.md fis-authoring-guidelines.md fis-template.md"
_skill_assets_exec_spec="automation-mode.md data-contract.md execution-discipline.md"
_skill_assets_exec_plan="automation-mode.md data-contract.md execution-discipline.md"
_skill_assets_ops="data-contract.md"
_skill_assets_review="adversarial-challenge.md critic-calibration.md fis-authoring-guidelines.md lens-adversarial.md review-calibration.md review-report-location.md trust-boundaries.md"
_skill_assets_quick_review="critic-calibration.md lens-adversarial.md"
_skill_assets_architecture="adversarial-challenge.md design-tree.md farley-framework.md review-calibration.md review-report-location.md"
_skill_assets_clarify="design-tree.md"
_skill_assets_testing="farley-framework.md"
_skill_assets_e2e_test="trust-boundaries.md"
_skill_assets_triage="trust-boundaries.md"
_skill_assets_init="project-state-templates.md"
_skill_assets_map_codebase="project-state-templates.md"
_skill_assets_refactor="automation-mode.md"
_skill_assets_remediate_findings="automation-mode.md"

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
    e2e-test) printf '%s' "$_skill_assets_e2e_test" ;;
    triage)   printf '%s' "$_skill_assets_triage" ;;
    init)     printf '%s' "$_skill_assets_init" ;;
    map-codebase) printf '%s' "$_skill_assets_map_codebase" ;;
    refactor) printf '%s' "$_skill_assets_refactor" ;;
    remediate-findings) printf '%s' "$_skill_assets_remediate_findings" ;;
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
  _vprs_list=$(grep -rElZ '\$CLAUDE_PLUGIN_ROOT[^}]' \
    "$repo_root/plugin/skills" \
    "$repo_root/plugin/references" 2>/dev/null | tr '\0' '\n' || true)
  if [ -n "$_vprs_list" ]; then
    printf '%s\n' "$_vprs_list" | while IFS= read -r _vprs_file; do
      [ -z "$_vprs_file" ] && continue
      _vprs_line=$(grep -n '\$CLAUDE_PLUGIN_ROOT[^}]' "$_vprs_file" | head -1)
      printf 'error: %s:%s uses bare $CLAUDE_PLUGIN_ROOT; only the braces form ${CLAUDE_PLUGIN_ROOT} is accepted\n' \
        "$_vprs_file" "$_vprs_line" >&2
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
#     (bare filename, sibling-relative — unambiguous under both file-relative
#     and skill-root-relative semantics).
#   - All other files (skill root, and any other depth-1+ subdir like
#     templates/, scripts/) → references/<asset> (skill-root-relative).
# Today only skill-root and immediate-child references/ files contain such
# references; if a future consumer file lives elsewhere (e.g.
# <skill>/references/sub/foo.md or <skill>/templates/foo.md) and references
# a canonical asset, this rewrite would need a depth-aware computation.
# Called after namespace rewrite so the installed bundle has no plugin-root refs.
# ---------------------------------------------------------------------------
rewrite_plugin_root_file() {
  _rprf_md="$1"
  case "$(dirname "$_rprf_md")" in
    */references)
      sed -i.bak 's|\${CLAUDE_PLUGIN_ROOT}/references/||g' "$_rprf_md"
      ;;
    *)
      sed -i.bak 's|\${CLAUDE_PLUGIN_ROOT}/references/|references/|g' "$_rprf_md"
      ;;
  esac
  rm -f "$_rprf_md.bak"
}

rewrite_plugin_root_dir() {
  _rprd_dir="$1"
  _rprd_list=$(find "$_rprd_dir" -name '*.md' -type f)
  [ -z "$_rprd_list" ] && return 0
  printf '%s\n' "$_rprd_list" | while IFS= read -r _rprd_md; do
    rewrite_plugin_root_file "$_rprd_md"
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
  # `dir` variable — POSIX sh has no function-local scope.
  _rwns_dir="$1"
  _rwns_target="$2"
  # Resolve the file list up-front so `set -e` catches find errors. In a
  # `find | while` pipeline the pipeline's exit status is `while`'s, so find
  # failures (e.g. unreadable directory) would be silently swallowed.
  _rwns_list=$(find "$_rwns_dir" -name '*.md' -type f)
  [ -z "$_rwns_list" ] && return 0
  printf '%s\n' "$_rwns_list" | while IFS= read -r md; do
    rewrite_namespace_file "$md" "$_rwns_target"
  done
}

# Rewrite the brand-cased token "AndThen" → <display_brand> in the installed
# skill's agents/openai.yaml (display_name, short_description, default_prompt).
# No-op when the brand is the default.
#
# Scope is intentionally narrowed to agents/openai.yaml rather than all *.yaml
# under the skill: the broad form would silently rewrite incidental "AndThen"
# substrings in unrelated yaml (manifests, fixtures, URLs like
# github.com/AndThen/...) introduced later. Field-level scoping inside the
# file is left to sed's substring match — acceptable because the file format
# is small and fully ours.
#
# The brand is escaped for sed-replacement context (\, the chosen delimiter |,
# and & — which would otherwise expand to the matched text). The empty-brand
# case is rejected at arg-parse, so this helper does not need to guard it.
rewrite_display_brand_dir() {
  _rdb_dir="$1"
  _rdb_brand="$2"
  [ "$_rdb_brand" = "AndThen" ] && return 0
  _rdb_yaml="$_rdb_dir/agents/openai.yaml"
  [ -f "$_rdb_yaml" ] || return 0
  _rdb_brand_esc=$(printf '%s' "$_rdb_brand" \
    | sed -e 's/\\/\\\\/g' -e 's/|/\\|/g' -e 's/&/\\&/g')
  sed -i.bak "s|AndThen|${_rdb_brand_esc}|g" "$_rdb_yaml"
  rm -f "$_rdb_yaml.bak"
}

# Install a Claude Code user-level agent from a plugin/agents/<name>.md source.
# Claude Code resolves agents by their frontmatter `name:` when the Task tool
# looks up subagent_type, so the name must be prefixed to match the filename.
install_claude_agent() {
  src="$1"        # plugin/agents/<name>.md
  dst="$2"        # <claude_agents_dir>/<prefix><name>.md

  if [ "$dry_run" -eq 1 ]; then
    printf 'mkdir -p %s\n' "$(dirname "$dst")"
    printf 'cp %s %s\n' "$src" "$dst"
    printf '# then prefix frontmatter name: and rewrite namespace refs\n'
    return
  fi

  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"

  # Rewrite only the frontmatter `name:` line (first block, first match).
  # awk END-block exit-status signals whether a name: line was found; we fail
  # loudly if not, rather than silently installing an agent whose filename
  # and frontmatter `name:` disagree (Task tool resolution would fail later).
  if awk -v p="$prefix" '
    NR == 1 && $0 == "---" { in_fm = 1; print; next }
    in_fm && $0 == "---"   { in_fm = 0; print; next }
    in_fm && !done && /^name: / {
      sub(/^name: /, "name: " p)
      done = 1
    }
    { print }
    END { exit done ? 0 : 1 }
  ' "$dst" > "$dst.tmp"; then
    mv "$dst.tmp" "$dst"
  else
    rm -f "$dst.tmp" "$dst"
    printf 'error: %s has no frontmatter `name:` line; cannot install as Claude Code user agent.\n' "$src" >&2
    return 1
  fi

  rewrite_namespace_file "$dst" "/"
}

# Run strict-syntax and canonical-asset checks before any copy.
_validate_plugin_root_syntax || exit 1
_check_canonical_assets || exit 1

skills_count=0
claude_skills_count=0

for dir in "$repo_root/plugin/skills"/*; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")

  case "$name" in
    "$prefix"*)
      target_name="$name"
      ;;
    *)
      target_name="$prefix$name"
      ;;
  esac

  # ~/.agents/skills install (Codex discovery) — rewrite with $ sigil form.
  copy_dir_contents "$dir" "$skills_dir/$target_name"
  # Inline canonical assets for this skill, then rewrite ${CLAUDE_PLUGIN_ROOT} refs
  # to local-relative form. inline_canonical_assets runs before rewrite_namespace_dir
  # so the inlined files also get namespace-rewritten in the same pass.
  if [ "$dry_run" -eq 0 ]; then
    inline_canonical_assets "$skills_dir/$target_name" "$name"
    rewrite_plugin_root_dir "$skills_dir/$target_name"
    rewrite_namespace_dir "$skills_dir/$target_name" '$'
    rewrite_display_brand_dir "$skills_dir/$target_name" "$display_brand"
  else
    inline_canonical_assets "$skills_dir/$target_name" "$name"
  fi
  skills_count=$((skills_count + 1))

  # Optional: Claude Code user-level skills — rewrite with / slash-command form.
  if [ "$install_claude_user" -eq 1 ]; then
    copy_dir_contents "$dir" "$claude_skills_dir/$target_name"
    if [ "$dry_run" -eq 0 ]; then
      inline_canonical_assets "$claude_skills_dir/$target_name" "$name"
      rewrite_plugin_root_dir "$claude_skills_dir/$target_name"
      rewrite_namespace_dir "$claude_skills_dir/$target_name" '/'
      rewrite_display_brand_dir "$claude_skills_dir/$target_name" "$display_brand"
    else
      inline_canonical_assets "$claude_skills_dir/$target_name" "$name"
    fi
    claude_skills_count=$((claude_skills_count + 1))
  fi
done

codex_agents_count=0
codex_agents_removed=0
# Codex agents removed in 0.13 (converted to skills). Remove stale installs on upgrade.
stale_codex_agents="solution-architect build-troubleshooter ui-ux-designer qa-test-engineer"

if [ "$install_codex_agents" -eq 1 ] && [ -d "$repo_root/plugin/agents" ]; then
  if [ "$dry_run" -eq 1 ]; then
    for stale in $stale_codex_agents; do
      stale_path="$codex_agents_dir/${prefix}${stale}.toml"
      [ -f "$stale_path" ] && printf 'rm %s\n' "$stale_path"
    done
    printf '%s/scripts/generate-codex-agents.sh --agents-src %s/plugin/agents --out-dir %s --prefix %s\n' \
      "$repo_root" "$repo_root" "$codex_agents_dir" "$prefix"
    codex_agents_count=$(find "$repo_root/plugin/agents" -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')
  else
    for stale in $stale_codex_agents; do
      stale_path="$codex_agents_dir/${prefix}${stale}.toml"
      if [ -f "$stale_path" ]; then
        rm -f "$stale_path"
        codex_agents_removed=$((codex_agents_removed + 1))
      fi
    done
    "$repo_root/scripts/generate-codex-agents.sh" \
      --agents-src "$repo_root/plugin/agents" \
      --out-dir "$codex_agents_dir" \
      --prefix "$prefix" >/dev/null
    codex_agents_count=$(find "$codex_agents_dir" -maxdepth 1 -type f -name "${prefix}*.toml" | wc -l | tr -d ' ')
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

printf 'Installed %s skills into %s\n' "$skills_count" "$skills_dir"
[ "$codex_agents_count" -gt 0 ] && printf 'Installed %s Codex agents into %s\n' "$codex_agents_count" "$codex_agents_dir"
[ "$codex_agents_removed" -gt 0 ] && printf 'Removed %s stale Codex agent(s) from previous versions\n' "$codex_agents_removed"
[ "$claude_skills_count" -gt 0 ] && printf 'Installed %s Claude Code user skills into %s\n' "$claude_skills_count" "$claude_skills_dir"
[ "$claude_agents_count" -gt 0 ] && printf 'Installed %s Claude Code user agents into %s\n' "$claude_agents_count" "$claude_agents_dir"
