#!/usr/bin/env sh

set -eu

usage() {
  cat <<'EOF'
Install AndThen commands and skills into Codex-compatible prompt and skill directories.

Usage:
  ./scripts/install-codex.sh [options]

Options:
  --prompts-dir PATH   Destination for prompt files (default: ~/.codex/prompts)
  --skills-dir PATH    Destination for skill directories (default: ~/.codex/skills)
  --prefix PREFIX      Prefix for exported names (default: andthen-)
  --dry-run            Print planned operations without copying files
  -h, --help           Show this help text

Notes:
  - Core commands and extras are exported as prompt files named <prefix><command>.md
  - Skills are exported as directories named <prefix><skill-name>/
  - Existing files are overwritten in place, but stale files are not deleted
EOF
}

repo_root=$(
  CDPATH= cd -- "$(dirname -- "$0")/.." && pwd
)

prompts_dir="${HOME}/.codex/prompts"
skills_dir="${HOME}/.codex/skills"
prefix="andthen-"
dry_run=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --prompts-dir)
      prompts_dir="$2"
      shift 2
      ;;
    --skills-dir)
      skills_dir="$2"
      shift 2
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

copy_file() {
  src="$1"
  dst="$2"

  if [ "$dry_run" -eq 1 ]; then
    printf 'cp %s %s\n' "$src" "$dst"
    return
  fi

  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
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
}

commands_count=0
skills_count=0

for source_dir in "$repo_root/plugin/commands" "$repo_root/plugin/commands/extras"; do
  for file in "$source_dir"/*.md; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    copy_file "$file" "$prompts_dir/$prefix$name"
    commands_count=$((commands_count + 1))
  done
done

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
  skills_count=$((skills_count + 1))
done

printf 'Installed %s commands into %s\n' "$commands_count" "$prompts_dir"
printf 'Installed %s skills into %s\n' "$skills_count" "$skills_dir"
