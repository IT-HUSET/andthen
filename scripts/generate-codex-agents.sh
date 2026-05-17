#!/usr/bin/env bash
#
# Generate Codex agent TOML files from plugin/agents/*.md.
# Claude Code agent markdown is the source of truth.

set -euo pipefail

usage() {
  cat <<'EOF'
Generate Codex agent TOML files from plugin/agents/*.md.

Usage:
  ./scripts/generate-codex-agents.sh --agents-src PATH --out-dir PATH [--prefix PREFIX] [--display-brand BRAND]

Options:
  --agents-src PATH       Source directory of Claude agent .md files (required)
  --out-dir PATH          Destination directory for generated .toml files (required)
  --prefix PREFIX         Prefix for generated names and filenames (letters,
                          numbers, '_' and '-' only; must end with '-';
                          default: andthen-)
  --display-brand BRAND   Human-readable brand name substituted for "AndThen"
                          in generated descriptions and instructions
                          (default: AndThen)
  -h, --help              Show this help text
EOF
}

agents_src=""
out_dir=""
prefix="andthen-"
display_brand="AndThen"

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
    --agents-src)
      require_option_value "$1" "${2-}"
      agents_src="$2"
      shift 2
      ;;
    --out-dir)
      require_option_value "$1" "${2-}"
      out_dir="$2"
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

if [ -z "$agents_src" ] || [ -z "$out_dir" ]; then
  printf 'error: --agents-src and --out-dir are required\n\n' >&2
  usage >&2
  exit 1
fi

if [ ! -d "$agents_src" ]; then
  printf 'error: agents source directory not found: %s\n' "$agents_src" >&2
  exit 1
fi

mkdir -p "$out_dir"

map_model() {
  case "$1" in
    haiku)  printf 'gpt-5.4-mini\tlow' ;;
    sonnet) printf 'gpt-5.4\tmedium' ;;
    opus)   printf 'gpt-5.4\thigh' ;;
    *)      printf 'gpt-5.4\tmedium' ;;
  esac
}

rewrite_namespace_text() {
  _rnt_target="$1"
  sed \
    -e "s|\`/andthen:|\`${_rnt_target}${prefix}|g" \
    -e "s|^/andthen:|${_rnt_target}${prefix}|g" \
    -e "s|\([[:space:]]\)/andthen:|\1${_rnt_target}${prefix}|g" \
    -e "s|andthen:|${prefix}|g"
}

rewrite_brand_text() {
  if [ "$display_brand" = "AndThen" ]; then
    cat
    return 0
  fi
  _rbt_brand_esc=$(printf '%s' "$display_brand" \
    | sed -e 's/\\/\\\\/g' -e 's/|/\\|/g' -e 's/&/\\&/g')
  sed "s|AndThen|${_rbt_brand_esc}|g"
}

rewrite_review_agent_names_text() {
  sed \
    -e "s|\`review-agent-workflow\`|\`${prefix}review-agent-workflow\`|g" \
    -e "s|\`review-architecture\`|\`${prefix}review-architecture\`|g" \
    -e "s|\`review-correctness\`|\`${prefix}review-correctness\`|g" \
    -e "s|\`review-critic\`|\`${prefix}review-critic\`|g" \
    -e "s|\`review-devils-advocate\`|\`${prefix}review-devils-advocate\`|g" \
    -e "s|\`review-product-requirements\`|\`${prefix}review-product-requirements\`|g" \
    -e "s|\`review-project-standards\`|\`${prefix}review-project-standards\`|g" \
    -e "s|\`review-security\`|\`${prefix}review-security\`|g" \
    -e "s|\`review-synthesis-challenger\`|\`${prefix}review-synthesis-challenger\`|g" \
    -e "s|\`review-testing\`|\`${prefix}review-testing\`|g"
}

escape_toml_basic_string() {
  sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

escape_toml_multiline_string() {
  sed 's/"""/"" "/g'
}

rewrite_claude_refs() {
  sed \
    -e 's/`CLAUDE\.md` \/ `AGENTS\.md`/__ANDTHEN_AGENT_DOCS__/g' \
    -e 's/CLAUDE\.md \/ AGENTS\.md/__ANDTHEN_AGENT_DOCS__/g' \
    -e 's/CLAUDE\.md/AGENTS.md \/ CLAUDE.md/g' \
    -e 's/__ANDTHEN_AGENT_DOCS__/AGENTS.md \/ CLAUDE.md/g'
}

count=0

for agent_md in "$agents_src"/*.md; do
  [ -f "$agent_md" ] || continue

  frontmatter=$(awk 'BEGIN{count=0} /^---$/{count++; next} count==1{print} count>=2{exit}' "$agent_md")
  body=$(awk 'BEGIN{count=0} /^---$/{count++; next} count>=2{print}' "$agent_md")

  name=$(printf '%s\n' "$frontmatter" | awk -F': *' '/^name:/{print $2; exit}')
  description=$(printf '%s\n' "$frontmatter" | awk -F': *' '/^description:/{sub(/^description: */, ""); print; exit}')
  model=$(printf '%s\n' "$frontmatter" | awk -F': *' '/^model:/{print $2; exit}')

  if [ -z "$name" ] || [ -z "$description" ]; then
    printf 'error: %s missing frontmatter name or description\n' "$agent_md" >&2
    exit 1
  fi

  mapped=$(map_model "$model")
  codex_model=$(printf '%s' "$mapped" | cut -f1)
  codex_effort=$(printf '%s' "$mapped" | cut -f2)

  body_rewritten=$(printf '%s' "$body" \
    | rewrite_claude_refs \
    | rewrite_namespace_text '$' \
    | rewrite_review_agent_names_text \
    | rewrite_brand_text)
  description_rewritten=$(printf '%s' "$description" \
    | rewrite_claude_refs \
    | rewrite_namespace_text '$' \
    | rewrite_review_agent_names_text \
    | rewrite_brand_text)

  body_escaped=$(printf '%s' "$body_rewritten" | escape_toml_multiline_string)
  description_escaped=$(printf '%s' "$description_rewritten" | escape_toml_basic_string)

  target="$out_dir/${prefix}${name}.toml"

  {
    printf '# Generated from plugin/agents/%s by scripts/generate-codex-agents.sh.\n' "$(basename "$agent_md")"
    printf '# Edit the source markdown instead.\n'
    printf '\n'
    printf 'name = "%s%s"\n' "$prefix" "$name"
    printf 'description = "%s"\n' "$description_escaped"
    printf 'model = "%s"\n' "$codex_model"
    printf 'model_reasoning_effort = "%s"\n' "$codex_effort"
    printf '\n'
    printf 'developer_instructions = """\n'
    printf '%s\n' "$body_escaped"
    printf '"""\n'
  } > "$target"

  count=$((count + 1))
done

printf 'Generated %s Codex agent files in %s\n' "$count" "$out_dir"
