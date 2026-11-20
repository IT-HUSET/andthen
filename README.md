<p align="center">
  <img src="assets/logo.png" alt="AndThen" width="500">
</p>

<p align="center">
  <i>Lightweight and flexible agentic software engineering for AI coding agents, spec-driven when the work needs a spec.</i>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#the-workflow">Workflow</a> ·
  <a href="#core-skills">Skills</a> ·
  <a href="COOKBOOK.md">Cookbook</a> ·
  <a href="plugin/README.md">Skill reference</a>
</p>

> "I have a feature idea" → *and then?* → **clarify** → *and then?* → **plan** → *and then?* → **exec-plan** → *and then?* → **review** → **ship it.**

AndThen is a set of skills for AI coding agents (Claude Code, ChatGPT/Codex, GitHub Copilot, and others) that covers the whole agentic software engineering process: requirements, architecture, design, implementation, testing, review, and debugging. Its main workflow is spec-driven: for anything bigger than a small fix, the agent writes a spec first and then builds against it. The spec says what to build, how to prove it works, and when it is done.

An agent writes code faster than you can read it, and you still answer for what merges. AndThen aims to keep you in charge:

- **Control** – the calls that matter stay yours. A plan runs one story per session, so you can adjust the next one before it runs, and `ship` pushes only after your yes.
- **Ownership** – the intent and the decisions are yours. `clarify` writes the requirements only once you confirm what it understood, and `decide` records each choice that is costly to reverse as an architecture decision record (ADR) you accept. Both documents outlive the branch.
- **Trust** – nothing is done on the agent's word. A subagent that didn't write the code reviews every story against its spec, and a story is marked done only with a quoted line from the check that proved it.
- **Transparency** – you can see what was done and why. Each story ends in a report, and the PR states the intent, each outcome with its proof, where to read closely, and how to undo the change. Each story report and the PR list what the run decided without asking.

The process is sized to the work: a change you can state in one sentence skips the specs (`implement-fix`), and a plan's specs are deleted before the merge unless you keep them. [Where you take part](#where-you-take-part) lists each point where the work waits for you.

It is one plugin with 21 skills and nothing else to install: no CLI, no runtime, no tool directory to commit. Skills find your specs and docs through an index in `CLAUDE.md` / `AGENTS.md`. The skills are prompts, and a [live eval harness](evals/README.md) runs cases for about half of them on Claude Code, with a smoke set on Codex.

<p align="center">
  <a href="https://github.com/IT-HUSET/andthen/raw/main/assets/skills-overview.svg"><img src="assets/skills-overview.svg" alt="AndThen skills and workflow – the idea-to-merge chain (optional clarify, decide and ui-ux-design, then plan, exec-plan, review, implement-fix and ship) with where you take part: the interviews of clarify, decide and plan, three numbered gates (PRD, ADRs, PR), and three reads (the FIS files, each story's report, the review report), the hand-off artifacts (intent.md or a short note, prd.md, ADRs, plan.json with a FIS per story), the thirteen standalone skills, and the four opt-in subagent roles"></a>
  <br><sub>Click the figure for the interactive version: hover a skill, artifact, or role to see what it does.</sub>
</p>


## Quick start

Install the plugin:

```bash
# Claude Code
/plugin marketplace add IT-HUSET/andthen
/plugin install andthen@andthen

# ChatGPT/Codex
codex plugin marketplace add IT-HUSET/andthen
codex plugin add andthen@andthen

# GitHub Copilot
copilot plugin marketplace add IT-HUSET/andthen
copilot plugin install andthen@andthen
```

The `/andthen:<name>` commands on this page are Claude Code's and Copilot's. On ChatGPT/Codex, ask for a skill by name: *Run the `andthen:init` skill*. This works on every host.

Then set up your project once and build a first feature. Run each command in a fresh session (`/clear` in Claude Code). Each step after `init` ends by printing the full next command to paste:

```bash
# once per project: sets up the document index
/andthen:init

# writes the spec (the FIS) and its one-story plan.json
/andthen:plan "users can export their data"

# builds the story, runs its checks, has it reviewed
/andthen:exec-plan docs/specs/data-export/s01-data-export.md

# reviews the whole change and applies its fixes
/andthen:review --fix docs/specs/data-export/plan.json

# shows you the PR, then opens it after your yes
/andthen:ship docs/specs/data-export/plan.json
```

Not sure where to start, or where you are? `/andthen:now-what` reads your project state and sends you to the right skill.

> [!NOTE]
> AndThen is experimental, and skills still change shape between minor versions. **Coming from 0.x?** 1.0 was a breaking release: [update the plugin](#upgrading-from-0x), then follow [MIGRATING-FROM-0.x.md](MIGRATING-FROM-0.x.md), because retired skills and flags have no aliases and 0.x specs must be rewritten with `plan` before they run.


## The workflow

```
[clarify] → [decide] → [ui-ux-design] → plan → exec-plan → review --fix → ship
```

Steps in brackets are optional. Five terms you will see throughout:

- **PRD** (`prd.md`) – the requirements document `clarify` writes: the problem, who has it, and what counts as solved.
- **Story** – one slice of the work, small enough for one agent session to build and prove.
- **FIS** (Feature Implementation Specification) – the spec for one story: what to build, the tests that prove it, and the tasks. `plan` writes one per story.
- **Plan** (`plan.json`) – the list of stories, their order, and each one's status, kept beside the FIS files.
- **Fresh session** – a new conversation (`/clear` in Claude Code). Each step reads the files the previous step wrote, so it starts on a clean context.

What each step does:

1. **`clarify`** (optional) interviews you and writes the PRD. Skip it when the requirements already exist, in your head, an issue, or a document. A rule of thumb: if you can't list three concrete acceptance criteria, you have an idea, not requirements.
2. **`decide`** (optional) settles a technical choice that reaches beyond this work or is costly to reverse, and records it as an architecture decision record (ADR). **`ui-ux-design`** (optional) designs new screens first when you choose that.
3. **`plan`** writes the specs. It decides whether the work is one story or several.
4. **`exec-plan`** builds the stories, one per fresh session. For each one it writes the code and tests, runs every check, has a fresh subagent review it, commits, and then simplifies the result. What a story learns goes into the stories still to run.
5. **`review --fix`** reviews the finished work as a whole and applies the findings it marks `Fix`. Findings marked `Note` are left for you to decide. It picks the review modes (lenses) that apply: `code`, `gap` (does it match its source and specs), `security` when the change calls for it, and `outcome` (does the feature solve the problem the PRD describes) when there is a PRD. A clean review ends on a `Next (fresh session):` line for `ship`.
6. **`ship`** lands what each story's `Implementation Observations` hold worth keeping, commits, and shows the PR title and body (a merge request on GitLab).
   It pushes and opens it after your one yes, and that question also asks whether to delete `plan.json` and the FIS files; `ship --auto` publishes without asking.
   The PR body states the change's intent, outcomes, and proof, so with `prd.md` the stories' intent outlives the deleted FIS files.

The [quick start](#quick-start) is this path for a request typed inline, which `plan` treats as one story.

### From a PRD

`plan` splits a written source (a PRD, a requirements file, an issue) into as many stories as it needs, often just one. `exec-plan` then takes one story per session. Each step runs in a fresh session and prints the next command:

```bash
# interviews you and writes docs/specs/data-export/prd.md
/andthen:clarify "users should be able to export their data"

# writes plan.json and one FIS per story
/andthen:plan docs/specs/data-export/

# one story per session
/andthen:exec-plan docs/specs/data-export/s01-export-request.md
/andthen:exec-plan docs/specs/data-export/s02-export-download.md

# reviews the finished stories as a whole, then ships them
/andthen:review --fix docs/specs/data-export/plan.json
/andthen:ship docs/specs/data-export/plan.json
```

To build every story without stopping, from CI or in parallel worktrees, run `exec-plan` on the plan directory instead (`--auto`, `--worktree`). It gives each story a fresh subagent and runs the full checks once at the end instead of after every story.

### Where you take part

You answer when `clarify` and `decide` interview you and when `plan` asks its preflight questions. Between stories you read the report of the one that just ran and any FIS it changed for the stories ahead, and adjust the next story before it runs ([revising a spec](COOKBOOK.md#revising-a-spec-or-re-planning)). Three points need your sign-off, because what they hold outlives the branch:

- **After `clarify`** – read `prd.md`. Every story is cut from it, and it is the one planning file that survives the merge, unless your requirements live in the tracker.
- **After `decide`**, when it ran – read the ADRs. Every later skill treats them as settled.
- **At the PR** – review it as you would any PR.
  In an attended run, `ship` lands the observations worth keeping and prints its recommendations for the rest, so read those and settle the review's open `Note` findings before you say yes to its push-and-PR question.

Two more reads pay off when you have the time: the review report, and after `plan` the FIS of any story you would build differently. `plan` states each story's approach above the next command, with what you decided and what the run assumed, so you can tell which FIS that is without opening them all.

### Smaller work

Two skills change code without a spec:

```bash
# a change you can state in one sentence
/andthen:implement-fix "return 404 instead of 500 for an unknown export job id"

# something is broken and you don't know why
/andthen:triage "tests fail on main since yesterday"
```

The [Cookbook](COOKBOOK.md) has a recipe for each situation, starting with [choosing a path](COOKBOOK.md#choosing-a-path), and follows [one feature end to end](COOKBOOK.md#the-worked-example-workspace-invitations).


## Core skills

The nine skills most work starts from:

| Skill | What it does |
|---|---|
| `init` | Sets up a project: the document index in `CLAUDE.md` / `AGENTS.md`, the project's test commands, and offers for the optional extras |
| `now-what` | Reads your project state and routes you to the right skill |
| `clarify` | Interviews you about an idea and writes the PRD; `--brief` stops at a shorter `intent.md` you can share first |
| `domain` | Models the domain with you as the expert: subdomains and bounded contexts in a Domain Map, the glossary of shared terms, and event storming |
| `decide` | Settles technical choices with you and records them as ADRs |
| `plan` | Decides whether the work is one story or several, and writes one FIS per story plus the `plan.json` that tracks them |
| `exec-plan` | Builds one FIS, or every story in a plan, each proven by its checks and reviewed by a fresh subagent |
| `review` | Reviews code, spec conformance, security, or the outcome against the PRD; also reviews PRs |
| `handoff` | Writes a document a fresh session can resume from when a session has to end mid-work |

The other twelve are `implement-fix`, `ship`, `triage`, `testing`, `architecture`, `describe`, `ui-ux-design`, `visual-validation`, `visualize`, `tracker`, `spike`, and `simplify-code`. The [skill reference](plugin/README.md#skills) covers all 21 skills, with every flag and mode.


## Project setup

`/andthen:init` works on new projects, half-set-up ones, and existing codebases. In an existing repository it asks nothing; in an empty one it asks what the project is. It writes:

- the **Project Document Index** in `CLAUDE.md` / `AGENTS.md`, which tells every skill where your specs and docs live (with both hosts, `AGENTS.md` holds it and `CLAUDE.md` imports it);
- when the project has a manifest (`package.json`, `pyproject.toml`, and the like), a **Key Dev Commands** document with its fast and full test commands;
- two `.gitignore` entries.

Every other document is created by the first skill that needs it. The closing summary offers the optional extras one line each: role agents that pin a model per kind of work, critical rules for your instruction file, a map of an existing codebase (`describe`), and a testing strategy. The [skill reference](plugin/README.md#foundational-rules-and-conversation-style) covers the rules and the optional `concise-critical` conversation style.

To set up by hand instead, start from [`CLAUDE.template.md`](plugin/skills/init/templates/CLAUDE.template.md).


## Permissions, sandboxing, and hooks

`exec-plan` runs for a long time without you watching, so it is worth limiting what the agent's shell commands can reach. They run as you. Approval prompts and allow/deny rules decide what asks you first, but a command you approve can still read `~/.ssh` or send data anywhere. An OS sandbox closes that gap. Every command and its child processes can write only inside the workspace, has no network, and cannot read the files you deny. Codex turns its sandbox on by default; Claude Code does not.

- [`permissions/`](permissions/README.md) – example settings for both hosts. The sandbox is on and the network off. Commands cannot see `.env` files, cloud credentials, browser profiles, or token variables. `git push` asks first, the destructive-command hook below runs before every command, and Claude Code's bypass flag is refused. Organization-enforced variants are included.
- [`hooks/`](hooks/README.md) – four optional hooks: a guard against destructive shell commands, desktop or voice notifications, and a context-size hint that tells you when to start a fresh session. The guard matches patterns, so it adds a layer and does not replace the sandbox.

Run `--dangerously-skip-permissions` or `--yolo` only inside a container or VM that holds none of your credentials.


## Installation

The [quick start](#quick-start) installs the latest release from `main` on all three plugin hosts. To pin a release, add its tag: `IT-HUSET/andthen@v1.0.0` on Claude Code and Codex, and `https://github.com/IT-HUSET/andthen.git#v1.0.0` on Copilot, which takes a URL fragment instead of `@`.

Versions are tagged on `develop` for testing by real users before the same commit reaches `main`.
`IT-HUSET/andthen@develop` follows that testing branch (Copilot: `#develop`); a tag such as `@v1.2.0` pins one version, which may still be in testing.
To follow only versions promoted to `main`, remove the marketplace and add it again as `IT-HUSET/andthen`.

### Host options

- **Claude Code** – `/plugin install andthen@andthen --scope project` installs for the current project only; the default is your user. Turn on auto-update in `/plugin` → **Marketplaces** → `andthen` → **Enable auto-update**.
- **ChatGPT/Codex** – if you copied the skills into `~/.agents/skills` before (a loose install), delete the old `andthen-*` directories first, or Codex lists every skill twice.
- **GitHub Copilot** – a project or personal skill with the same name as an AndThen skill (`review`, `plan`) silently replaces it; rename yours or list it in `disabledSkills`. Role agents and the conversation style come from `init`, as on the other hosts. Copilot support is load-checked in CI, not covered by the evals.

### From a checkout, or in a container

`scripts/andthen.py install` installs the plugin on every host whose CLI is on `PATH`, from the tree it sits in, reads the installed version back, and exits non-zero on any mismatch. It removes an `andthen` marketplace added from GitHub and adds the local tree in its place, so host upgrades stop following GitHub until you add `IT-HUSET/andthen` again as in the [quick start](#quick-start). `--dry-run` prints the plan and writes nothing.

```bash
# the plugin, from this checkout
python3 scripts/andthen.py install

# plus user-level role agents and critical rules
python3 scripts/andthen.py install --roles --rules

# With no checkout, such as an image build, it downloads the latest release first
curl -fsSL https://raw.githubusercontent.com/IT-HUSET/andthen/main/scripts/andthen.py \
  | python3 - install --roles --rules
```

`--ref v<version>` pins a release, a checkout included. The download lands in `${XDG_DATA_HOME:-~/.local/share}/andthen/<version>` and stays, because Copilot loads it live. A role file or rules block that differs from AndThen's is refused (`--replace-roles` overwrites a role file), and `--trust <path>` marks a project trusted in Codex.

In a container, install when the image is built, not on every start, and pass `--trust` with the project's path so Codex applies its config. A volume mounted over the home folder (`~/.claude`, `~/.codex`, `~/.copilot`, `~/.local/share`) hides what the build placed there; then run the install at start instead, where a second run changes nothing. Placement does not prove the sandbox's plan offers the models the role agents pin, so run one short prompt per host.

### Other agents (Cursor, Gemini CLI, opencode, Amp)

`--loose` copies the skills into your agent's skills directory under `andthen-` names, each bundle self-contained. Invoke them with `$andthen-<skill>` in Codex and other agents that read `~/.agents/skills`.

```bash
# all skills into ~/.agents/skills
python3 scripts/andthen.py install --loose

# preview what it will do
python3 scripts/andthen.py install --loose --dry-run

# a subset
python3 scripts/andthen.py install --loose --skills clarify,plan,review

# custom skills directory
python3 scripts/andthen.py install --loose --skills-dir <path>
```

Without `--skills-dir` it refuses while the AndThen Codex plugin is installed, because Codex reads `~/.agents/skills` too. A reinstall replaces the skills it installed before but leaves retired ones in place.

### Upgrading from 0.x

1.0 ships from the same marketplace as 0.x: `andthen`, added from `IT-HUSET/andthen`. Refresh the marketplace and update the plugin:

```bash
# Claude Code (auto-update, when on, does this at startup)
/plugin marketplace update andthen
/plugin update andthen@andthen                 # restart to apply

# ChatGPT/Codex
codex plugin marketplace upgrade andthen
codex plugin add andthen@andthen

# GitHub Copilot
copilot plugin marketplace update andthen
copilot plugin update andthen@andthen
```

A marketplace added with a tag, such as `IT-HUSET/andthen@v0.40.4`, stays on that tag: remove it and add it again as in the [quick start](#quick-start). Hosts upgrade with their own commands, and `scripts/andthen.py` is for a [checkout or a container](#from-a-checkout-or-in-a-container); it re-registers the `andthen` marketplace from a local tree, so afterwards these commands no longer follow GitHub.

Updating replaces the skills, not your 0.x specs, which need rewriting before they run: [MIGRATING-FROM-0.x.md](MIGRATING-FROM-0.x.md) covers that and the retired skill names.

### Staying on 0.x

0.40.4 is the last 0.x release, tagged `v0.40.4`. It gets no further changes, and its own [README](https://github.com/IT-HUSET/andthen/blob/v0.40.4/README.md) documents it. To install it, or to go back to it from 1.0, remove the marketplace and add it again with the tag pinned:

- **Claude Code and Codex:** `IT-HUSET/andthen@v0.40.4` in place of `IT-HUSET/andthen`.
- **Copilot:** `https://github.com/IT-HUSET/andthen.git#v0.40.4` in place of `IT-HUSET/andthen`.
- **Loose skills:** check out the tag (`git checkout v0.40.4`) and run the installer that tag's own README names.


## More

- [`COOKBOOK.md`](COOKBOOK.md) – what to type for each situation, how the workflow fits together, [working in a team](COOKBOOK.md#working-in-a-team), [coming from Spec Kit, Kiro, BMAD, or GSD](COOKBOOK.md#coming-from-spec-kit-kiro-bmad-or-gsd), and a worked example.
- [`plugin/README.md`](plugin/README.md) – the skill reference: every flag, mode, and edge case.
- [`MIGRATING-FROM-0.x.md`](MIGRATING-FROM-0.x.md) – upgrading a 0.x project: what changed, the steps, and a prompt that does them.
- [`docs/PRODUCT.md`](docs/PRODUCT.md) – goals, non-goals, and how AndThen weighs verification against ceremony.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) – how the plugin is built, for contributors.
- [`docs/MODEL-EFFORT-SELECTION-GUIDE.md`](docs/MODEL-EFFORT-SELECTION-GUIDE.md) – choosing models and thinking effort.


## Works well with

AndThen has much in common with other skill libraries for agentic engineering and spec-driven development, especially those that cover the whole lifecycle without a rigid process or proprietary conventions. It covers the main workflow on its own and works well beside complementary libraries and tools:

- [Matt Pocock's Skills For Real Engineers](https://github.com/mattpocock/skills/)
- [pstack by @poteto](https://github.com/cursor/plugins/tree/main/pstack)
- Anthropic's [official plugin marketplace](https://github.com/anthropics/claude-plugins-official): `frontend-design` (visual direction when building UI), `skill-creator` (write and eval your own skills), `claude-md-management` (audit CLAUDE.md files and capture session learnings in them), `playground`, and [`semgrep`](https://github.com/semgrep/mcp-marketplace) (external, recommended there).
- [Agent Browser](https://github.com/vercel-labs/agent-browser), a browser automation CLI for agents.


## Inspired by _(name)_

[![Dude, Where's My Car?](https://img.youtube.com/vi/oqwzuiSy9y0/0.jpg)](https://www.youtube.com/watch?v=oqwzuiSy9y0)

and then

[![Mullvad](https://img.youtube.com/vi/fPzvUW8qaWY/0.jpg)](https://www.youtube.com/watch?v=fPzvUW8qaWY)


## Actually inspired by

Too many to list, but special shoutout to:
- [Peter Steinberger](https://github.com/steipete)
- [Cole Medin](https://github.com/coleam00)
- [IndieDevDan](https://github.com/disler)
- [Matt Pocock](https://github.com/mattpocock)
- [Addy Osmani](https://github.com/addyosmani)
- [Mario Zechner](https://github.com/badlogic)
- [Matt Maher](https://github.com/bladnman)


## License

[MIT](LICENSE).
