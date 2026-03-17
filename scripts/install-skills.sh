#!/usr/bin/env sh

set -eu

usage() {
  cat <<'EOF'
Install AndThen skills into the agent skills directory.

Usage:
  ./scripts/install-skills.sh [options]

Options:
  --skills-dir PATH    Destination for skill directories (default: ~/.agents/skills)
  --prefix PREFIX      Prefix for exported names (default: andthen.)
  --dry-run            Print planned operations without copying files
  -h, --help           Show this help text

Notes:
  - All skills are exported as directories named <prefix><skill-name>/
  - Agent Teams skills (exec-plan-team, review-council-team) are excluded
    since they require Claude Code
  - Existing files are overwritten in place, but stale files are not deleted
EOF
}

repo_root=$(
  CDPATH= cd -- "$(dirname -- "$0")/.." && pwd
)

skills_dir="${HOME}/.agents/skills"
prefix="andthen."
dry_run=0

while [ "$#" -gt 0 ]; do
  case "$1" in
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

skills_count=0

for dir in "$repo_root/plugin/skills"/*; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")

  # Agent Teams skills require Claude Code — skip for other agents
  [ "$name" = "exec-plan-team" ] && continue
  [ "$name" = "review-council-team" ] && continue

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

# Copy plugin reference docs as a shared skill so other skills can find them
refs_count=0
if [ -d "$repo_root/plugin/references" ]; then
  refs_dir="$skills_dir/${prefix}references"
  copy_dir_contents "$repo_root/plugin/references" "$refs_dir"
  refs_count=$(find "$repo_root/plugin/references" -maxdepth 1 -type f | wc -l | tr -d ' ')
fi

printf 'Installed %s skills into %s\n' "$skills_count" "$skills_dir"
[ "$refs_count" -gt 0 ] && printf 'Installed %s reference docs into %s\n' "$refs_count" "$refs_dir"
