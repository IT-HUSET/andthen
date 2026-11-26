# Permissions and sandboxing

Example settings for Claude Code and Codex that keep the agent's shell commands away from your secrets and the network, while it works freely inside the project. Copy what you need. Nothing here is installed by the plugin.

## Three layers

An agent's shell commands run as you. Each layer below catches what the one above misses:

1. **Approval** – the permission mode (Claude Code) or approval policy (Codex) decides what asks you first. It is a prompt, not a boundary: a command you approve can read and write anything your account can.
2. **Rules** – allow, ask, and deny patterns. They match a command as written, so a deny on `curl` misses the same request made from a Python script. The [`block-dangerous-commands.py`](../hooks/README.md#block-dangerous-commandspy) hook is another pattern layer.
3. **OS sandbox** – Seatbelt on macOS, bubblewrap on Linux and WSL2. It limits what every shell command and its child processes can read, write, and connect to, however they were started. It is the only layer of the three that contains a command.

Bypass modes (`--dangerously-skip-permissions`, and Codex's `--yolo` or `danger-full-access`) skip the approval prompts, and Codex's also switch off the sandbox. Use them inside a VM or container that holds no secrets and limits the network, where they spare an unattended run the prompts that would stop it. Claude Code's own sandbox is not enough on its own: it confines shell commands only, and in bypass mode the Edit and Write tools write wherever no deny rule stops them, including `.claude/settings.json`, whose hooks run outside the sandbox. Ask and deny rules still apply in bypass mode. Codex's organization file allows neither `danger-full-access` nor the `never` policy.

Claude Code's auto mode and Codex's `approvals_reviewer = "auto_review"` hand the approval prompt to a model that reviews each action in your place. That is safer than `acceptEdits` or a bypass mode, but it replaces your review rather than adding to it, so keep the sandbox and the rules underneath. Auto mode suits interactive work in Claude Code. The Codex files keep you as the reviewer (`approvals_reviewer = "user"`), because `auto_review` would also answer the network and `git push` prompts the files are there to raise, prompt rules included. Without a sandbox the trade flips. Every command then needs approval, so if you turn Codex's sandbox off, set `approvals_reviewer = "auto_review"`, the counterpart of auto mode, and never Full access.

| | Claude Code | Codex |
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
- **Sandbox on, network off.** Commands write only to the workspace and temp directories, and reach no host. A command that needs the network fails inside the sandbox and is retried outside it: in Claude Code auto mode's classifier reviews the retry, so an agent keeps working unattended, and Codex asks you. `strictAllowlist` keeps the sandbox's host list fixed. To skip the retry for hosts you trust, such as your package registry, add them to `sandbox.network.allowedDomains`. Avoid broad ones like `github.com`, which can carry data out.
- **Secrets hidden from commands and file tools.** `.env`, `.env.*`, and direnv's `.envrc` files at any depth; keys and cloud and cluster credentials (`~/.ssh`, `~/.gnupg`, `~/.aws`, `~/.azure`, `~/.config/gcloud`, `~/.kube`); tool and registry tokens (`~/.config/gh`, git's plain-text credential store in `~/.git-credentials` and `~/.config/git/credentials`, `~/.npmrc`, `~/.pypirc`, `~/.cargo/credentials` and `credentials.toml`, `~/.docker/config.json`, `~/.netrc`); and Chrome, Chromium, Edge, and Firefox profiles, whose cookies sign in to your accounts. The profile entries cover macOS, Linux, Windows (`~/AppData`), and the Windows profiles a WSL2 command can reach under `/mnt/c/Users/*`. The `.env.*` pattern also blocks `.env.example`; drop it if your project keeps a template. In Claude Code's sandbox, a commit signed with a key file under `~/.ssh` or `~/.gnupg` can fail.
- **Tokens dropped from the environment.** Claude Code lists them by name (`GITHUB_TOKEN`, `GH_TOKEN`, `NPM_TOKEN`, and the two API keys). Codex drops every variable whose name contains `KEY`, `SECRET`, or `TOKEN`.
- **Publishing runs unattended in Claude Code.** `git push`, `git fetch`, `git pull`, `gh pr`, `gh issue`, and `gh label` skip the sandbox (`excludedCommands`) and run with your credentials and network, reviewed by auto mode's classifier, so an agent pushes and opens pull requests on its own; the hook still refuses force pushes. Other `gh` commands, such as `gh api` or `gh auth token`, stay sandboxed and need a retry the classifier approves. No ask rule covers them, because a headless run refuses whatever an ask rule matches. Codex asks, because its sandbox keeps `.git` read-only and the network off.
- **Discarding uncommitted work asks first.** In Claude Code, `git reset --hard`, `git checkout -- <path>` and `git checkout .`, a forced `git clean`, and `git stash drop` and `clear` prompt in these usual forms, because the sandbox lets them write in the workspace and auto mode's classifier would otherwise decide them. An ask rule also stops an unattended run, so `git restore` and `git worktree remove --force` stay unprompted: a `git restore` rule would also catch `git restore --staged`, and AndThen's `review` and `spike` run the forced worktree removal. Codex's sandbox refuses all but `git clean`, because they write to the read-only `.git`; `git clean` deletes untracked files there unless you add `prefix_rule(pattern = ["git", "clean"], decision = "prompt")` to `~/.codex/rules/default.rules`, which also prompts for a dry run.
- **Destructive commands refused.** A `PreToolUse` hook runs [`block-dangerous-commands.py`](../hooks/README.md#block-dangerous-commandspy) before every shell command, on both hosts, and refuses `rm -rf`, force pushes, pipe-to-shell, and the rest of its list in every mode. It is the fixed floor under auto mode's classifier, which weighs what you asked for (so "clean up the repo" can justify a delete) and may let a sandboxed command run without review. Its list is a suggested starting set, not a complete one. Copy the script to `~/.claude/hooks/scripts/` first ([hooks setup](../hooks/README.md#installation)); Codex asks you to trust the hook once in `/hooks`.

The organization files enforce part of this on every machine they manage:

- **Claude Code's** enforces all of the above except the hook, refuses to start when the sandbox cannot run, and limits sandboxed commands to the managed host allowlist.
- **Codex's** enforces the secret denies, the `git push` and `git clean` prompts, that a person answers prompts (`allowed_approvals_reviewers`), and, on Windows, a sandbox that enforces the denies. It allows neither `danger-full-access` nor the `never` approval policy, so `--yolo` falls back to an allowed mode. It does not enforce network or environment settings; Codex 0.138+ can pin a whole permission profile with `allowed_permission_profiles` and a managed `default_permissions`.
- **Neither ships the hook**, because a managed hook needs its script at the same root-owned path on every machine. To add it, install the script there, add the personal file's `hooks` entry with that path, and in Claude Code set `allowManagedHooksOnly` if users' own hooks should not run.

## What Claude Code sends to Anthropic

Claude Code's personal file also turns off usage telemetry (`DISABLE_TELEMETRY`, which also stops the "How is Claude doing?" survey), error reports (`DISABLE_ERROR_REPORTING`), and the `/feedback`, `/bug`, and `/share` commands (`DISABLE_FEEDBACK_COMMAND`). `DO_NOT_TRACK=1` has the same effect as `DISABLE_TELEMETRY`, so the file leaves it out. Telemetry events carry no code, file paths, or commands, so this settles what leaves your machine about your usage, not about your code.

Turning telemetry off also stops Claude Code fetching its feature flags, so `/skill-doctor`, `claude import` and `/import`, and `/restart` on Pro, Max, and Ultra stop working. Remote Control still works, from 2.1.283 (2.1.304 in the desktop app), but sessions no longer connect to it on their own, and it is unavailable where your organization requires Trusted Devices. Drop `DISABLE_TELEMETRY` if you need those. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` turns all three off and more, but also stops auto-updates and Remote Control.

## Native Windows

Claude Code has no sandbox on native Windows; it runs commands unsandboxed. Run it inside WSL2 to get the sandbox. The organization file refuses to start without one (`failIfUnavailable`), which moves managed Windows users to WSL2. Natively, under the personal file:

- **Auto mode is the main gate.** The classifier reviews every command that isn't read-only, with no sandbox behind it to contain a mistake. Keep auto mode on and never switch to bypass, because nothing would contain a command.
- **Secret denies cover less.** They stop the Read tool and the file commands Claude Code recognizes in Bash (`cat`, `head`, `tail`, `sed`, `tee`). They do not stop a script or another program, and the docs don't say they cover PowerShell cmdlets such as `Get-Content`.
- **Tokens stay and the network is open.** `sandbox.credentials` and the empty domain allowlist apply only inside the sandbox.
- **The hook still refuses its list** in both shells, with the `Bash|PowerShell` matcher.

Codex has a Windows sandbox, but its `unelevated` implementation ignores denied read paths, so the secret denies do not hold there. Codex falls back to it when the elevated setup isn't approved. The organization file allows only `elevated` (`[windows] allowed_sandbox_implementations`), which still permits the newer MXC sandbox.

## Merging and caveats

- **Claude Code** merges arrays across settings files, so the deny list adds to yours. The sandbox covers Bash and its child processes only. The Read and Edit tools obey the deny rules, but MCP servers and hooks run outside both.
- **Codex** personal file uses permission profiles (beta). A `sandbox_mode` in any loaded config, or the `--sandbox` flag, silently replaces the profile and its secret denies, so remove `sandbox_mode` and `[sandbox_workspace_write]` from your config. Unknown keys are also ignored silently; the `#:schema` line lets an editor flag them.
- **Publishing from AndThen** runs unattended in Claude Code: `ship` and `tracker publish` push and call `gh pr`, `gh issue`, and `gh label`, which both Claude Code files run outside the sandbox. Under the Codex files each of these asks.
- **Unattended runs** (CI, `claude -p`, `codex exec`) are better in a container than on these files. In Claude Code, bypass mode suits the container. A headless run refuses whatever an ask rule matches, even in bypass mode, so drop the ask rules the run must get past, or use `dontAsk` mode with an explicit `permissions.allow` list. In Codex use `approval_policy = "never"` with the sandbox kept on.

## Verified

Checked on 2026-10-15 with Claude Code 2.1.300 and Codex 0.162.1 on macOS.

- **Both personal files:** under the sandbox, reading `.env`, a nested `sub/.env`, `~/.ssh`, or the Chrome profile failed with "Operation not permitted", from `cat` and from a Python script alike. `GITHUB_TOKEN` was unset, `example.com` was unreachable, and `ok.txt` read fine.
- **Codex also:** writing outside the workspace or into `.git` was refused. With an empty config, the same `.env`, Chrome profile, and token came through. The hook refused `rm -rf` and pipe-to-shell when given Codex's `PreToolUse` input directly, not yet in a live Codex session.
- **Claude Code also:** the hook refused `rm -rf`. The Read tool was refused `sub/.env` and read a file beside it. In auto mode an unknown host got "host is not on the allow list".

The rules added since were checked on 2026-11-25 with Claude Code 2.1.332 and Codex 0.171.0 on macOS.

- **Codex personal file**, through `codex sandbox` with a stand-in home folder: `.envrc`, `sub/.envrc`, and every added home-folder path failed to read, while a file beside them read fine. `git reset --hard`, `git checkout --`, `git restore`, and `git stash drop` failed on the read-only `.git`, and `git clean -f` deleted an untracked file. `codex execpolicy check` returned `prompt` for `git clean -fdx` under the `git clean` rule.
- **Claude Code personal file**, headless in bypass mode, which runs every command no rule stops, with only the hook taken out of a test copy: each added ask rule refused its command, `echo first && git clean -fd` included, while `git status`, `cat`, `git clean -n`, and `git restore --staged` ran. A Python script got "Operation not permitted" on `sub/.envrc`, and the Read tool was refused it. The added home-folder paths were not tried against a real home folder. Headless in auto mode, an agent pushed twice to a remote outside the workspace with no prompt: `git push` ran outside the sandbox, and `echo two >> f.txt && git commit -qam two && git push` failed inside it and was retried outside.
- **Not run in either pass:** a `gh` call, `codex/requirements.toml`, which needs a write to `/etc`, the Claude Code prompts, which need an interactive session, a signed commit under the `~/.ssh` and `~/.gnupg` denies, whether Codex's `git clean` rule prompts for a command its sandbox would run, and anything on Windows. These follow the documented shapes, as does the telemetry `env` block, checked against the environment variable and Remote Control docs on 2026-11-24.
