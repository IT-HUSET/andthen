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
  - Shared references, helper scripts, and shared templates are exported
    alongside skills
  - Codex agents are installed as <prefix><agent-name>.toml and rewritten to
    point at the installed shared references path
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

resolve_path() {
  case "$1" in
    /*)
      printf '%s\n' "$1"
      ;;
    "~")
      printf '%s\n' "$HOME"
      ;;
    "~/"*)
      printf '%s/%s\n' "$HOME" "${1#~/}"
      ;;
    *)
      printf '%s/%s\n' "$(pwd -P)" "$1"
      ;;
  esac
}

escape_sed_value() {
  printf '%s' "$1" | sed 's/[&|\\]/\\&/g'
}

replace_in_file() {
  file="$1"
  pattern="$2"
  escaped_value=$(escape_sed_value "$3")

  sed -i.bak "s|$pattern|$escaped_value|g" "$file"
  rm -f "$file.bak"
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

copy_file() {
  src="$1"
  dst="$2"

  if [ "$dry_run" -eq 1 ]; then
    printf 'mkdir -p %s\n' "$(dirname "$dst")"
    printf 'cp %s %s\n' "$src" "$dst"
    return
  fi

  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
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

  # Rewrite paths and skill references for the target environment
  if [ "$dry_run" -eq 0 ]; then
    find "$skills_dir/$target_name" -name '*.md' -type f | while IFS= read -r md; do
      # Repo-relative reference paths → installed sibling paths
      sed -i.bak "s|plugin/references/|../${prefix}references/|g" "$md"
      rm -f "$md.bak"
      # Claude Code slash-command invocation (/andthen:X) → Codex sigil form ($andthen-X)
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
      # Plugin-root paths → installed sibling paths
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/scripts/|../${prefix}scripts/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/references/|../${prefix}references/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/skills/|../${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/../templates/|../${prefix}templates/|g" "$md"
      rm -f "$md.bak"
      # Markdown link targets must be rewritten separately from link text
      sed -i.bak "s|](../../references/|](../${prefix}references/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|](../../skills/|](../${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|templates/project-state-templates\\.md|../${prefix}templates/project-state-templates.md|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|templates/CLAUDE\\.template\\.md|../${prefix}templates/CLAUDE.template.md|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|../${prefix}../${prefix}templates/|../${prefix}templates/|g" "$md"
      rm -f "$md.bak"
    done
  fi

  skills_count=$((skills_count + 1))
done

# Copy plugin reference docs as a shared directory so other skills can find them
refs_count=0
if [ -d "$repo_root/plugin/references" ]; then
  refs_dir="$skills_dir/${prefix}references"
  copy_dir_contents "$repo_root/plugin/references" "$refs_dir"
  refs_count=$(find "$repo_root/plugin/references" -maxdepth 1 -type f | wc -l | tr -d ' ')

  # Apply the same path and namespace rewrites to reference docs
  if [ "$dry_run" -eq 0 ]; then
    find "$refs_dir" -name '*.md' -type f | while IFS= read -r md; do
      # Claude Code slash-command invocation (/andthen:X) → Codex sigil form ($andthen-X)
      # Anchored (see skills loop above for rationale).
      sed -i.bak "s|\`/andthen:|\`\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|^/andthen:|\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\([[:space:]]\)/andthen:|\1\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|andthen:|${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/references/|../${prefix}references/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/scripts/|../${prefix}scripts/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/skills/|../${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/../templates/|../${prefix}templates/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|](../../references/|](../${prefix}references/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|](../../skills/|](../${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|templates/project-state-templates\\.md|../${prefix}templates/project-state-templates.md|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|templates/CLAUDE\\.template\\.md|../${prefix}templates/CLAUDE.template.md|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|../${prefix}../${prefix}templates/|../${prefix}templates/|g" "$md"
      rm -f "$md.bak"
    done
  fi
fi

# Copy shared repo-level templates for skills that reference them
templates_count=0
if [ -d "$repo_root/templates" ]; then
  templates_dir="$skills_dir/${prefix}templates"
  copy_dir_contents "$repo_root/templates" "$templates_dir"
  templates_count=$(find "$repo_root/templates" -maxdepth 1 -type f | wc -l | tr -d ' ')

  if [ "$dry_run" -eq 0 ]; then
    find "$templates_dir" -name '*.md' -type f | while IFS= read -r md; do
      # Claude Code slash-command invocation (/andthen:X) → Codex sigil form ($andthen-X)
      # Anchored (see skills loop above for rationale).
      sed -i.bak "s|\`/andthen:|\`\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|^/andthen:|\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\([[:space:]]\)/andthen:|\1\$${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|andthen:|${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/scripts/|../${prefix}scripts/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/references/|../${prefix}references/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/skills/|../${prefix}|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}/../templates/|../${prefix}templates/|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|templates/project-state-templates\\.md|../${prefix}templates/project-state-templates.md|g" "$md"
      rm -f "$md.bak"
      sed -i.bak "s|templates/CLAUDE\\.template\\.md|../${prefix}templates/CLAUDE.template.md|g" "$md"
      rm -f "$md.bak"
    done
  fi
fi

# Copy shared helper scripts so exported skills can use them
scripts_count=0
if [ -d "$repo_root/plugin/scripts" ]; then
  scripts_dir="$skills_dir/${prefix}scripts"
  copy_dir_contents "$repo_root/plugin/scripts" "$scripts_dir"
  scripts_count=$(find "$repo_root/plugin/scripts" -maxdepth 1 -type f -name '*.sh' | wc -l | tr -d ' ')
fi

codex_agents_count=0
if [ "$install_codex_agents" -eq 1 ] && [ -d "$repo_root/codex/agents" ]; then
  resolved_refs_dir=$(resolve_path "$skills_dir/${prefix}references")

  for agent in "$repo_root/codex/agents"/*.toml; do
    [ -f "$agent" ] || continue

    name=$(basename "$agent")
    case "$name" in
      andthen-*)
        target_name="${prefix}${name#andthen-}"
        ;;
      *)
        target_name="$name"
        ;;
    esac

    target_path="$codex_agents_dir/$target_name"
    copy_file "$agent" "$target_path"

    if [ "$dry_run" -eq 0 ]; then
      replace_in_file "$target_path" 'name = "andthen-' "name = \"${prefix}"
      replace_in_file "$target_path" '~/.agents/skills/andthen-references/' "$resolved_refs_dir/"
    fi

    codex_agents_count=$((codex_agents_count + 1))
  done
fi

printf 'Installed %s skills into %s\n' "$skills_count" "$skills_dir"
[ "$refs_count" -gt 0 ] && printf 'Installed %s reference docs into %s\n' "$refs_count" "$refs_dir"
[ "$templates_count" -gt 0 ] && printf 'Installed %s shared templates into %s\n' "$templates_count" "$templates_dir"
[ "$scripts_count" -gt 0 ] && printf 'Installed %s helper scripts into %s\n' "$scripts_count" "$scripts_dir"
[ "$codex_agents_count" -gt 0 ] && printf 'Installed %s Codex agents into %s\n' "$codex_agents_count" "$codex_agents_dir"
