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
  --claude-user             Also install skills and agents as Claude Code user-level
                            files (~/.claude/skills and ~/.claude/agents), using the
                            same <prefix> so invocation is /andthen-<name> on both
                            Claude Code and Codex. Alternative to the Claude Code
                            plugin — do not enable while the plugin is also installed.
  --prefix PREFIX           Prefix for exported names (default: andthen-)
  --dry-run                 Print planned operations without copying files
  -h, --help                Show this help text

Notes:
  - All skills are exported as directories named <prefix><skill-name>/
  - Skills are fully self-contained: each skill owns its references/, templates/,
    and scripts/ locally, so only namespace rewriting (andthen: → <prefix>) is
    applied at install time. No cross-skill or plugin-root paths remain.
  - Codex agents are generated at install time from plugin/agents/*.md
    (Claude Code agent files are the source of truth) and written as
    <prefix><agent-name>.toml into the codex agents directory
  - Claude Code user agents (with --claude-user) are plain .md copies of
    plugin/agents/*.md, with the frontmatter `name:` prefixed so Task tool
    resolution (subagent_type: "<prefix><agent>") works.
  - Existing files are overwritten in place, but stale files are not deleted.
  - Disabling --claude-user on a later run does NOT remove previously installed
    ~/.claude/skills/<prefix>* / ~/.claude/agents/<prefix>*.md — delete those
    manually if switching back to the Claude Code plugin as the primary path.
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
    --prefix)
      prefix="$2"
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
  if [ "$_plugin_found" -eq 1 ]; then
    printf 'warning: --claude-user enabled but an andthen Claude Code plugin install appears present under ~/.claude/plugins/. Running both will create duplicate skills under andthen:<name> (plugin) and andthen-<name> (user). Uninstall the plugin (/plugin uninstall andthen) before using --claude-user.\n' >&2
  fi
fi

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
  if [ "$dry_run" -eq 0 ]; then
    rewrite_namespace_dir "$skills_dir/$target_name" '$'
  fi
  skills_count=$((skills_count + 1))

  # Optional: Claude Code user-level skills — rewrite with / slash-command form.
  if [ "$install_claude_user" -eq 1 ]; then
    copy_dir_contents "$dir" "$claude_skills_dir/$target_name"
    if [ "$dry_run" -eq 0 ]; then
      rewrite_namespace_dir "$claude_skills_dir/$target_name" '/'
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
