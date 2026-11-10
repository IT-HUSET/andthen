# ADR-030: One setup script installs AndThen and places its role agents and rules

## Status
Accepted. Recorded 2026-11-10.

Supersedes in part the Still Current note that `init` wires the rules and role agents in prose, not a script, through that note's own reopen condition (`docs/decisions/project-documents.md`): unattended setup moves to a script, attended setup keeps the prose. Supersedes ADR-018's consequence "Loose-skill installs keep their shape": the loose channel loses its white-label flags and its Claude Code target. `docs/PRODUCT.md`'s Runtime fact holds, because nothing new ships in `plugin/`.

## Context

**Unattended environments get neither the role agents nor the rules.** Devcontainers, agent sandbox VMs, and CI need AndThen set up deterministically: the plugin at a pinned version, and the role agents and critical rules where each host reads them. Only the `init` skill places roles and rules, through the interactive offers in `init/references/offers.md`, so an environment with nobody at the keyboard has none.

**Two scripts split the install, and nothing says which does what.**

- `scripts/andthen-plugins.py` (238 lines) drives each host's plugin commands, pinned with `--ref`, and reads the installed version back.
- `scripts/install-skills.py` (934 lines, plus the `install-skills.sh` shim) is the loose-skill installer. It also carries white-label flags, a Claude Code user-tier target, and `--validate-only`, the content check CI and the fast test tier run.

The README presents the second as the installer and names the first only for upgrades. On 2026-11-10 the maintainer and the agent both took the loose-skill installer for the one that places role agents.

**White-label installs served one downstream project, which has moved on.** DartClaw 0.28.0 calls the installer nowhere outside its tests and requires the AndThen 1.0 plugin.

**The prose-wiring decision anticipated this.** Its reopen condition reads "Reopens if an unattended `init` needs a machine-checkable wiring result." The cost that retired `wire.py` sat in its drift-report verb and its merges into existing user files. A fresh home has nothing to merge, and an exit code is a machine-checkable result.

## Decision

**One script, `scripts/andthen.py`, installs AndThen on every host and, when asked, places the role agents and critical rules at user level, writing only what needs no merge. `init` stays the attended path and owns every other case.**

- **One entry point, two modules.** `install` sets up the plugin on each host whose CLI is on `PATH`. `--loose` instead copies skills into `~/.agents/skills` or a named directory, always as `andthen-<name>`. The plugin and loose-skill code stay separate importable modules.
- **One source per run: a repo tree.** The script runs from the tree it sits in; with none (piped through curl) or with `--ref`, it downloads that ref's tree to `${XDG_DATA_HOME:-~/.local/share}/andthen/<version>` and runs that tree's own script. Each host installs the plugin from the tree as a local marketplace, and the role agents, rules, and loose skills come from it too, so all are one version byte for byte. A checkout is such a tree, and the container one-liner is `curl -fsSL https://raw.githubusercontent.com/IT-HUSET/andthen/main/scripts/andthen.py | python3 - install --roles --rules`; `--ref v<version>` pins it.
  - **Premise: `main` is the latest release.** The one-liner and the default ref follow `main`. `main` moves only by a release (`AGENTS.md` § Git Remotes), and `--ref v<version>` pins one exactly.
- **Role agents and rules are opt-in, user level only.** They go into the host homes (`$CLAUDE_CONFIG_DIR`, `$CODEX_HOME`, `$COPILOT_HOME`, defaulting to `~/.claude`, `~/.codex`, `~/.copilot`), never into the checkout, because a file written there is untracked and an agent working in it may commit it. A repo's own copies stay `init`'s, committed at project level.
  - **A role file** is whole and named by AndThen. Missing, it is written. Byte-identical to its template, it is accepted. Different, it is refused, unless `--replace-roles` is given, which overwrites it.
  - **The rules unit is the bounded block**, `# Critical Rules and Guardrails` to the next heading that is not the guideline's own, as `offers.md` defines it, inside the host's user instruction file (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`). File missing: written as the block. File present without the block: the block is appended and nothing else changes. Block identical: accepted. Block different: refused and never overwritten, because the file is the user's. The comparison ignores line-ending and trailing-whitespace differences.
  - **A refusal names the path and the `init` offer that resolves it**, so it reads differently from a version mismatch.
- **Install proves its own result.** Per host it reads the plugin version back from the installed copy and compares each placed file or block with its template. Any refusal or mismatch exits non-zero, so a Dockerfile or CI step fails on it. There is no separate check command.
- **Codex trust only on request.** `--trust <path>` adds `[projects."<resolved absolute path>"]` with `trust_level = "trusted"` to the user `config.toml`, and refuses when the path already carries another level. It is the one place the script edits a host config file by hand, because Codex has no command for it. It is never a default: trusting a path makes the project's own `.codex/` config, hooks, rules, and committed role agents apply, and in a sandbox running over code nobody vetted that gate is the protection.
- **Loose installs refuse to duplicate.** `--loose` without a named directory refuses when the AndThen Codex plugin is installed, because Codex reads `~/.agents/skills` too and would list every skill twice.
- **The content check is its own script**, `scripts/validate-plugin.py`. It keeps every check `--validate-only` runs today, the three-host role-template parity check included, and shares the loose-skill module where checks overlap. A loose install runs only the two checks a copy cannot survive without, canonical-asset existence and asset closure, because every tree an end user installs from passed CI and a maintainer runs the fast tier.
- **White-label support and the loose Claude Code target go**: `--display-brand`, custom `--prefix`, `--claude-skills-dir`, and `--claude-user`. Claude Code takes the plugin, from a checkout through `--plugin-dir` or `CLAUDE_CODE_PLUGIN_DIRS`.
- **The old commands go in the same release**: `install-skills.sh`, `install-skills.py`, and `andthen-plugins.py`, under a CHANGELOG Removed note.
- **The output style stays out.** It is personal configuration (`offers.md`), and an unattended environment has no conversation to style.

## Consequences

**Easier**
- One command and one help text set AndThen up, and an image build fails loudly when the setup is incomplete.
- An image shared across repos carries the roles and rules at user level; an image per repo gets them from the committed project files.
- The CI content check is named for what it is.

**Harder**
- A breaking change in 1.x. Automation calling the old names against `main` or `develop` breaks on upgrade. Users who run a tag's own script, as the README tells 0.x users to, meet the change only when they move tags. DartClaw's tests and docs still name `install-skills` and need updating.
- The script gains placement and a hand-edit of Codex's `config.toml`, code that `init`'s prose avoided.
- A persisted home with an edited role file fails on rebuild until `--replace-roles` or `init` resolves it, and a differing rules block always needs `init`.
- The tree the script ran from must stay where it is, because Copilot loads a local marketplace live from it rather than copying it, so a download is kept under `${XDG_DATA_HOME:-~/.local/share}/andthen/<version>`.
- Accepted loss: an organisation whose managed Claude Code settings block the AndThen marketplace and sideloading, but allow `~/.claude/skills`, has no install path. It can copy the skills itself.

**Unchanged**
- `init` owns attended setup, project-level placement, and every merge into a file that differs.
- The scripts are repo tooling and nothing ships in `plugin/`.
- Role agents stay opt-in.

**Reversal**: two-way door for the code, since a forwarding shim or a restored flag is a few lines; one-way for anyone who has rewired automation to the new command.

## Alternatives Considered
1. **One merged file** – rejected: about 1,200 lines mixing host-CLI driving with file rewriting.
2. **Keep and extend `andthen-plugins.py`**, or name it `scripts/setup.py` – rejected: "plugins" undersells a script that also installs loose skills, roles, and rules, and `setup.py` reads as a Python packaging script.
3. **Roles only, rules from committed files or `init`** – rejected: an image shared across repos would get no user-level rules.
4. **Project-level placement too** – rejected: untracked files in the checkout an agent may commit, and nearly every repo already has the `AGENTS.md` the rule would refuse.
5. **The whole instruction file, byte-identical, as the rules check** – rejected after review: user instruction files hold personal content and Copilot's also holds the style block, so it would refuse in the environments it exists for.
6. **Refuse an instruction file that lacks the block** – rejected: every persisted home would need `init` once, and appending destroys nothing.
7. **Always refuse, or always replace, a differing role file** – rejected: the first fails every persisted-home rebuild after a template change (this branch's Fable 5.2 pin for `oracle` would be the first), and the second drops local edits silently.
8. **A separate read-only `check` command** – rejected: install's exit code is the machine-checkable result, and a drift report was the expensive half of `wire.py`.
9. **Always trust the checkout, or leave trust to the recipe** – rejected: the first trusts silently on dev machines and on unvetted code, and the second leaves the step a sandbox gets wrong first to copy and paste.
10. **The content check as a setup subcommand, or kept as an install flag** – rejected: a maintainer-only check in the user-facing help, or hidden inside an installer.
11. **Remove `--display-brand` only, or keep every white-label flag** – rejected: no known user remains.
12. **Forwarding shims for one release, or until 2.0** – rejected by the maintainer for a clean tree, accepting the break for automation on branch heads.
13. **How a container gets a tree.** Chosen: the piped form (`curl …/andthen.py | python3 - install --roles --rules`), whose bootstrap downloads the ref's tree and hands over to that tree's own script, so the second module and every template come from one version. Rejected: templates from the plugin copy a host installed (reads a host-internal cache layout); the tarball one-liner (`curl …/tar.gz/v<version> | tar -xz -C /opt && python3 /opt/andthen-<version>/scripts/andthen.py …`: two steps, and the user manages the tree's location); and a GitHub-install mode (`rc`, `stable`, `--ref` installing the plugin from GitHub: two meanings of `--ref`, a refusal of `--roles` and `--rules` because their templates would come from another version, and nothing host-native commands don't give, auto-update included).
14. **Claude Code's container seed (`CLAUDE_CODE_PLUGIN_SEED_DIR`) as the install mechanism** – considered, not chosen: it serves Claude Code only, Codex and Copilot have no equivalent, and it places no roles or rules. The script must not fight it.
15. **Floor option – extend what exists**: keep both scripts, rewrite the README and Architecture install sections, and document copy steps in a Cookbook container recipe – rejected: a reader still has to know which of two commands to run, and roles and rules stay copy and paste in every image. The Decision buys one command whose exit code proves the setup.

## Implementation Notes

- **Landed in `257ab5f4`** with every caller moved; `rg 'install-skills|andthen-plugins'` now hits only historical text.
- **Module names** are importable (`andthen_loose`, no hyphen), and tests call `sys.executable`, never bash, so they run on Windows.
- **The script's own code runs on Python 3.9**, the `python3` a stock macOS ships, so it reads Codex's `config.toml` without `tomllib`; the tests may assume CI's 3.12 floor. Since 2026-11-10 no CI row runs Python 3.9, because `ubuntu-latest` (Ubuntu 26.04) no longer offers it and the project pins no older image, so the floor is kept by review and the 3.9 workarounds in `andthen.py`, not by a check.
- **Version read-back on Claude Code** reads `installPath` and `version` from `installed_plugins.json` rather than a computed path. A host with a pre-seeded, read-only marketplace (`CLAUDE_CODE_PLUGIN_SEED_DIR`) skips the remove-and-reinstall and checks the seed's `cache/<marketplace>/<plugin>/<version>/` copy instead, since a seed carries no `installed_plugins.json`.
- **A seeded install proves presence, not loading.** Claude Code loads a seed's plugins only where `enabledPlugins` names them, in managed settings or the project's `.claude/settings.json`, and server-managed settings never reach the disk, so the script cannot read the enablement and does not fail on it. It prints the requirement; the load proof is `claude -p --output-format stream-json --verbose`, whose `init` event lists the loaded plugins.
- **Prove the unattended path in a clean container.** Proven on 2026-11-10 in `node:22-bookworm` with no sign-in (Claude Code 2.1.322, Codex 0.167.0, Copilot CLI 1.0.108): all three marketplace adds and installs, placement, an idempotent second run, and the refusals. Unconfirmed: whether `codex exec` in an untrusted directory prompts or fails, which needs a signed-in run.
- **Container guidance** is three sentences in `README.md` § "From a checkout, or in a container", not a Cookbook recipe: install at image build, `--trust`, the home-volume trap, a per-host prompt.
- **Bootstrap pitfalls.** Piped, `__file__` is `<stdin>` and a sibling module cannot be imported, so `andthen_loose` is imported inside the loose path, after the tree check. The hand-over is `subprocess.call`, not `os.execv`, which loses the exit code on Windows. Extraction passes `filter="data"` where `tarfile.data_filter` exists, because stock macOS Python 3.9 lacks it and 3.12+ warns without it. The top-level directory is the one entry in the tarball, never computed: GitHub names it `andthen-1.0.1` for `v1.0.1` and `andthen-main` for `main`. An `ssl` failure prints a hint to set `SSL_CERT_FILE` to the CA bundle curl trusts. Codeload serves a branch name containing a slash (`actions/checkout`'s `releases/v1` returns 200). An old copy that cannot be replaced, such as one a running host holds open on Windows, fails with a message to close the hosts.

## Project Compliance

- **Runtime: "prompts and assets only; no shipped script"** (`docs/PRODUCT.md`). Both scripts live in `scripts/`, never `plugin/`.
- **Decision Rule.** It names the failures it prevents, an unattended environment without roles or rules and two commands nobody could tell apart, and it extends what exists: both scripts' code moves in, while `wire.py`'s merges and drift report stay gone.
- **Lean.** One entry point and one content check replace two scripts and a shim, and the white-label code goes.
- **The prose-wiring note's reopen condition** is met for unattended setup only; attended setup keeps the prose.

## Reopens

- If the append-or-refuse rules handling refuses on a recorded unattended run that a merge would have served.
- If a host gains a supported command to trust a path or place agents, which replaces the hand-edit.
- If `main` stops being the latest release, the one-liner's default ref moves to a release tag.
- If automation outside the known callers breaks on the removal and a shim would have served it.

## References

- This session's interview with the maintainer and two oracle reviews, 2026-11-10.
- `docs/decisions/project-documents.md` (the prose-wiring reopen condition), `plugin/skills/init/references/offers.md`, ADR-018, ADR-022.
- `scripts/andthen-plugins.py`, `scripts/install-skills.py`, `.github/workflows/validate-plugin.yml`.
- DartClaw 0.28.0 (`dartclaw-public`): no installer call outside tests; its CHANGELOG requires the AndThen 1.0 plugin.
- Codex config reference (`projects.<path>.trust_level`); Claude Code's plugin-loading and seed-container docs.
