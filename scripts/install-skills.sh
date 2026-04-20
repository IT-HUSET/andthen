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
  - Existing files are overwritten in place, but stale files are not deleted
EOF
}

repo_root=$(
  CDPATH= cd -- "$(dirname -- "$0")/.." && pwd
)

skills_dir="${HOME}/.agents/skills"
codex_agents_dir="${HOME}/.codex/agents"
install_codex_agents=1
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

skills_count=0

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

  copy_dir_contents "$dir" "$skills_dir/$target_name"

  # Namespace rewrites only — skills are otherwise self-contained.
  if [ "$dry_run" -eq 0 ]; then
    find "$skills_dir/$target_name" -name '*.md' -type f | while IFS= read -r md; do
      # Claude Code slash-command invocation (/andthen:X) → Codex sigil form ($andthen-X).
      # Must run before the generic andthen: → andthen- rule so the sigil swap is preserved.
      # Anchored on backtick, whitespace, or line-start so path segments, markdown links,
      # and URLs with a "/andthen:" substring are not mangled.
      sed -i.bak "s|\`/andthen:|\`\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|^/andthen:|\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\([[:space:]]\)/andthen:|\1\$${prefix}|g" "$md"
      rm -f "$md.bak"
      # Plugin namespace (andthen:) → portable prefix (andthen-) for all remaining references
      sed -i.bak "s|andthen:|${prefix}|g" "$md"
      rm -f "$md.bak"
    done
  fi

  skills_count=$((skills_count + 1))
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

printf 'Installed %s skills into %s\n' "$skills_count" "$skills_dir"
[ "$codex_agents_count" -gt 0 ] && printf 'Installed %s Codex agents into %s\n' "$codex_agents_count" "$codex_agents_dir"
[ "$codex_agents_removed" -gt 0 ] && printf 'Removed %s stale Codex agent(s) from previous versions\n' "$codex_agents_removed"
