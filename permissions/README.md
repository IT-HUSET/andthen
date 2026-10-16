# Permissions and sandboxing

Example settings for Claude Code and Codex CLI that keep the agent's shell commands away from your secrets and the network, while it works freely inside the project. Copy what you need. Nothing here is installed by the plugin.

## Three layers

An agent's shell commands run as you. Each layer below catches what the one above misses:

1. **Approval** – the permission mode (Claude Code) or approval policy (Codex) decides what asks you first. It is a prompt, not a boundary: a command you approve can read and write anything your account can.
2. **Rules** – allow, ask, and deny patterns. They match a command as written, so a deny on `curl` misses the same request made from a Python script. The [`block-dangerous-commands.py`](../hooks/README.md#block-dangerous-commandspy) hook is another pattern layer.
3. **OS sandbox** – Seatbelt on macOS, bubblewrap on Linux and WSL2. It limits what every shell command and its child processes can read, write, and connect to, however they were started. It is the only layer of the three that contains a command.

Bypass modes (`--dangerously-skip-permissions`, and Codex's `--yolo` or `danger-full-access`) skip the approval prompts, and Codex's also switch off the sandbox. Don't use them, least of all where there is no sandbox. Nothing in these files needs them: Claude Code's personal file refuses bypass, and Codex's organization file allows neither `danger-full-access` nor the `never` policy.

Claude Code's auto mode and Codex's `approvals_reviewer = "auto_review"` hand the approval prompt to a model that reviews each action in your place. That is safer than `acceptEdits` or a bypass mode, but it replaces your review rather than adding to it, so keep the sandbox and the rules underneath. Auto mode suits interactive work in Claude Code. The Codex files keep you as the reviewer (`approvals_reviewer = "user"`), because `auto_review` would also answer the network and `git push` prompts the files are there to raise, prompt rules included. Without a sandbox the trade flips. Every command then needs approval, so if you turn Codex's sandbox off, set `approvals_reviewer = "auto_review"`, the counterpart of auto mode, and never Full access.

| | Claude Code | Codex CLI |
|---|---|---|
| Starting mode | `auto` from 2.1.283: a classifier reviews each action | `Auto`: workspace writes, asks when the sandbox blocks a command |
| Sandbox | **off** until enabled; none on native Windows | on |
| Network from commands | open | off |
| Commands can read `~/.ssh`, `.env` | yes | yes |

## The files

| File | Copy to | Effect |
|---|---|---|
| [`claude/settings.json`](claude/settings.json) | `~/.claude/settings.json` (merge) | Personal baseline |
| [`claude/managed-settings.json`](claude/managed-settings.json) | `/Library/Application Support/ClaudeCode/` (macOS), `/etc/claude-code/` (Linux) | Organization-enforced; users cannot override it |
| [`codex/config.toml`](codex/config.toml) | `~/.codex/config.toml` (merge) | Personal baseline |
| [`codex/requirements.toml`](codex/requirements.toml) | `/etc/codex/requirements.toml` | Organization-enforced; users cannot override it |

The two personal files set the same defaults:

- **The approval mode, explicitly.** Claude Code starts in auto mode (`defaultMode`), and falls back to Manual where auto is unavailable, such as on an unsupported model. Claude Code honours `auto` only from user or managed settings, not from a project's `.claude/settings.json`. Codex asks when the sandbox blocks a command (`approval_policy = "on-request"`).
- **Sandbox on, network off.** Commands write only to the workspace and temp directories, and reach no host. A command that needs the network fails inside the sandbox, and the agent asks you before running it outside, in every mode. In Claude Code that takes `strictAllowlist` plus an ask rule on `dangerouslyDisableSandbox`, because auto mode would otherwise let its classifier approve the host or the retry. To skip the prompt for hosts you trust, such as your package registry, add them to `sandbox.network.allowedDomains`. Avoid broad ones like `github.com`, which can carry data out.
- **Secrets hidden from commands and file tools.** `.env` and `.env.*` files at any depth; cloud and cluster credentials (`~/.ssh`, `~/.aws`, `~/.azure`, `~/.config/gcloud`, `~/.kube`); tool tokens (`~/.config/gh`, `~/.npmrc`, `~/.netrc`); and Chrome, Chromium, Edge, and Firefox profiles, whose cookies sign in to your accounts. The profile entries cover macOS, Linux, Windows (`~/AppData`), and the Windows profiles a WSL2 command can reach under `/mnt/c/Users/*`. The `.env.*` pattern also blocks `.env.example`; drop it if your project keeps a template.
- **Tokens dropped from the environment.** Claude Code lists them by name (`GITHUB_TOKEN`, `GH_TOKEN`, `NPM_TOKEN`, and the two API keys). Codex drops every variable whose name contains `KEY`, `SECRET`, or `TOKEN`.
- **Publishing asks first.** `git push` always prompts. Codex needs no rule for this, because its sandbox keeps `.git` read-only and the network off.
- **No bypass in Claude Code.** `disableBypassPermissionsMode` refuses `--dangerously-skip-permissions`.
- **Destructive commands refused.** A `PreToolUse` hook runs [`block-dangerous-commands.py`](../hooks/README.md#block-dangerous-commandspy) before every shell command, on both hosts, and refuses `rm -rf`, pipe-to-shell, and the rest of its list in every mode. It is the fixed floor under auto mode's classifier, which weighs what you asked for (so "clean up the repo" can justify a delete) and may let a sandboxed command run without review. Its list is a suggested starting set, not a complete one. Copy the script to `~/.claude/hooks/scripts/` first ([hooks setup](../hooks/README.md#installation)); Codex asks you to trust the hook once in `/hooks`.

The organization files enforce part of this on every machine they manage:

- **Claude Code's** enforces all of the above except the hook, refuses to start when the sandbox cannot run, and blocks every host outside the managed allowlist. Only `git push` and `gh` run outside the sandbox, and they always ask.
- **Codex's** enforces the secret denies and the `git push` prompt, that a person answers prompts (`allowed_approvals_reviewers`), and, on Windows, a sandbox that enforces the denies. It allows neither `danger-full-access` nor the `never` approval policy, so `--yolo` falls back to an allowed mode. It does not enforce network or environment settings; Codex 0.138+ can pin a whole permission profile with `allowed_permission_profiles` and a managed `default_permissions`.
- **Neither ships the hook**, because a managed hook needs its script at the same root-owned path on every machine. To add it, install the script there, add the personal file's `hooks` entry with that path, and in Claude Code set `allowManagedHooksOnly` if users' own hooks should not run.

## Native Windows

Claude Code has no sandbox on native Windows; it runs commands unsandboxed. Run it inside WSL2 to get the sandbox. The organization file refuses to start without one (`failIfUnavailable`), which moves managed Windows users to WSL2. Natively, under the personal file:

- **Auto mode is the main gate.** The classifier reviews every command that isn't read-only, with no sandbox behind it to contain a mistake. Keep auto mode on and never switch to bypass, which the file refuses anyway.
- **Secret denies cover less.** They stop the Read tool and the file commands Claude Code recognizes in Bash (`cat`, `head`, `tail`, `sed`, `tee`). They do not stop a script or another program, and the docs don't say they cover PowerShell cmdlets such as `Get-Content`.
- **Tokens stay and the network is open.** `sandbox.credentials` and the empty domain allowlist apply only inside the sandbox.
- **The hook still refuses its list** in both shells, with the `Bash|PowerShell` matcher.

Codex has a Windows sandbox, but its `unelevated` implementation ignores denied read paths, so the secret denies do not hold there. Codex falls back to it when the elevated setup isn't approved. The organization file allows only `elevated` (`[windows] allowed_sandbox_implementations`), which still permits the newer MXC sandbox.

## Merging and caveats

- **Claude Code** merges arrays across settings files, so the deny list adds to yours. The sandbox covers Bash and its child processes only. The Read and Edit tools obey the deny rules, but MCP servers and hooks run outside both.
- **Codex** personal file uses permission profiles (beta). A `sandbox_mode` in any loaded config, or the `--sandbox` flag, silently replaces the profile and its secret denies, so remove `sandbox_mode` and `[sandbox_workspace_write]` from your config. Unknown keys are also ignored silently; the `#:schema` line lets an editor flag them.
- **Publishing from AndThen** prompts more. `ship` pushes and opens the PR with `gh`, and `tracker publish` writes issues with `gh`. Under the personal files each of these asks before leaving the sandbox; under Claude Code's organization file each `gh` call asks.
- **Unattended runs** (CI, `claude -p`, `codex exec`) are better in a container than on these files. In Claude Code use `dontAsk` mode with an explicit `permissions.allow` list. In Codex use `approval_policy = "never"` with the sandbox kept on.

## Verified

Checked on 2026-10-15 with Claude Code 2.1.300 and Codex CLI 0.162.1 on macOS.

- **Both personal files:** under the sandbox, reading `.env`, a nested `sub/.env`, `~/.ssh`, or the Chrome profile failed with "Operation not permitted", from `cat` and from a Python script alike. `GITHUB_TOKEN` was unset, `example.com` was unreachable, and `ok.txt` read fine.
- **Codex also:** writing outside the workspace or into `.git` was refused. With an empty config, the same `.env`, Chrome profile, and token came through. The hook refused `rm -rf` and pipe-to-shell when given Codex's `PreToolUse` input directly, not yet in a live Codex session.
- **Claude Code also:** the hook refused `rm -rf`. The Read tool was refused `sub/.env` and read a file beside it. In auto mode an unknown host got "host is not on the allow list", and a retry outside the sandbox did not run in headless mode, where an ask becomes a refusal. With the organization file loaded, a blocked request could not leave the sandbox.
- **Not run:** `codex/requirements.toml`, which needs a write to `/etc`, the Claude Code prompts, which need an interactive session, and anything on Windows. These follow the documented shapes.
