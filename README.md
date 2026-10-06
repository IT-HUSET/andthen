<p align="center">
  <img src="assets/logo.png" alt="AndThen" width="500">
</p>

<p align="center">
  <i>Lightweight agentic software engineering for AI coding agents, spec-driven when the work needs a spec.</i>
</p>

> "I have a feature idea" → *and then?* → **clarify** → *and then?* → **plan** → *and then?* → **exec-plan** → *and then?* → **review** → **ship it.**

AndThen is a set of skills for AI coding agents (Claude Code, Codex CLI, and others) that covers the whole engineering job: requirements, design, implementation, testing, review, and debugging. Its main workflow is spec-driven: for anything bigger than a small fix, the agent writes a spec first and then builds against it. The spec says what to build, how to prove it works, and when it is done.

What AndThen enforces, so you don't have to:

- **Nothing is done on the agent's word.** A story is marked done only with a quoted line from the check that proved it, written by the session that ran the check.
- **The code is reviewed by an agent that didn't write it.** Every story gets a review from a fresh subagent that checks it against its spec.
- **Specs don't go stale.** The plan and its specs belong to one branch and are deleted before the merge. The requirements document (`prd.md`) is what stays, or its issue when you keep requirements in the tracker.
- **Process is sized to the work.** A change you can state in one sentence skips the specs entirely (`implement-fix`).

It is one plugin, `andthen`, with 20 skills and no runtime of its own to install. There is no CLI to install and no tool directory to commit: skills find your specs and docs through an index in `CLAUDE.md` / `AGENTS.md`.

<p align="center">
  <!-- pre-release: the raw link targets develop; point it at IT-HUSET/andthen/raw/main when 1.0 merges -->
  <a href="https://github.com/IT-HUSET/andthen/raw/develop/assets/skills-overview.svg"><img src="assets/skills-overview.svg" alt="AndThen skills and workflow – the idea-to-merge chain (optional clarify, decide and ui-ux-design, then plan, exec-plan, review, implement-fix and ship) with where you take part: the interviews of clarify, decide and plan, three numbered gates (PRD, ADRs, PR), and two optional reads (the FIS files, the review report), the hand-off artifacts (intent.md or a short note, prd.md, ADRs, plan.json with a FIS per story), the twelve standalone skills, and the four opt-in subagent roles"></a>
  <br><sub>Click the figure for the interactive version: hover a skill, artifact, or role to see what it does.</sub>
</p>


## Quick start

```bash
# Claude Code
/plugin marketplace add IT-HUSET/andthen@develop
/plugin install andthen@andthen
/andthen:init                      # set up your project
/andthen:now-what                  # ...and let it route you from there

# Codex CLI
codex plugin marketplace add IT-HUSET/andthen@develop
codex plugin add andthen@andthen
```

On Codex, ask for a skill by name: *Run the `andthen:init` skill*. This works on every host. The `/andthen:<name>` commands on this page are Claude Code's.

<!-- pre-release: at 1.0, drop "@develop" from both marketplace lines above and the note's first sentence -->
> [!NOTE]
> **1.0 is a breaking release, in release candidates on the `develop` branch** (`main` still serves 0.40.x). Have 0.x installed? [Remove it first](#10-release-candidate-from-the-develop-branch). Retired 0.x skills and flags have no aliases, and 0.x specs must be rewritten with `plan` before they run: [MIGRATING-FROM-0.x.md](MIGRATING-FROM-0.x.md) walks you through it. AndThen is experimental, and skills still change shape between minor versions.


## The workflow

Five terms you will see throughout:

- **PRD** (`prd.md`) – the requirements document `clarify` writes: the problem, who has it, and what counts as solved.
- **Story** – one slice of the work, small enough for one agent session to build and prove.
- **FIS** (Feature Implementation Specification) – the spec for one story: what to build, the tests that prove it, and the tasks. `plan` writes one per story.
- **Plan** (`plan.json`) – the list of stories, their order, and each one's status, kept beside the FIS files.
- **Fresh session** – a new conversation (`/clear` in Claude Code). Each step reads the files the previous step wrote, so it starts on a clean context.

The path through the workflow:

```
[clarify] → [decide] → [ui-ux-design] → plan → exec-plan → review --fix → ship
```

1. **`clarify`** (optional) interviews you and writes the PRD. Skip it when the requirements already exist, in your head, an issue, or a document. A rule of thumb: if you can't list three concrete acceptance criteria, you have an idea, not requirements.
2. **`decide`** (optional) settles a technical choice that reaches beyond this work or is costly to reverse, and records it as an architecture decision record (ADR). **`ui-ux-design`** (optional) designs new screens first when you choose that.
3. **`plan`** writes the specs. It decides whether the work is one story or several.
4. **`exec-plan`** builds the stories. For each one it writes the code and tests, runs every check, has a fresh subagent review it, and commits.
5. **`review --fix`** reviews the finished work as a whole and applies the findings it marks `Fix`. Findings marked `Note` are left for you to decide. A clean review ends on a `Next (fresh session):` line for `ship`.
6. **`ship`** lands what each story's `Implementation Observations` hold worth keeping, deletes `plan.json` and the FIS files, commits, and shows the PR title and body (a merge request on GitLab). It pushes and opens it after your one yes. The PR body states the change's intent, outcomes, and proof, in your PR template when you have one. With `prd.md`, it is where the stories' intent outlives the FIS files, however you merge.

Every step ends by printing the full next command to paste, including its target and required arguments. Not sure where you are? `/andthen:now-what` reads your project state and sends you to the right skill.

### From a one-line request

`plan` treats a request typed inline as one story:

```bash
/andthen:plan "users can export their data"                    # writes the FIS and its one-story plan.json
/andthen:exec-plan docs/specs/data-export/s01-data-export.md   # fresh session: builds and reviews the story
/andthen:review --fix docs/specs/data-export/plan.json   # fresh session: the Next line exec-plan printed
/andthen:ship docs/specs/data-export/plan.json           # fresh session: the Next line review printed
```

### From a PRD

`plan` splits a written source (a PRD, a requirements file, an issue) into as many stories as it needs, often just one. `exec-plan` then takes the whole plan directory:

```bash
/andthen:clarify "users should be able to export their data"   # interviews you, writes docs/specs/data-export/prd.md
/andthen:plan docs/specs/data-export/                          # fresh session: plan.json and one FIS per story
/andthen:exec-plan docs/specs/data-export/                     # fresh session: builds every story, one subagent each
/andthen:review --fix docs/specs/data-export/plan.json   # fresh session: the Next line exec-plan printed
/andthen:ship docs/specs/data-export/plan.json           # fresh session: the Next line review printed
```

Each review mode (lens) checks one thing: `code` the code itself, `gap` whether it matches its source and specs, `security` its vulnerabilities, and `outcome` whether the feature solves the problem the PRD describes. `review` picks the lenses the plan supports, so paste the line `exec-plan` printed.

### Where you take part

You answer when `clarify` and `decide` interview you and when `plan` asks its preflight questions; otherwise the workflow runs on its own. Three points need your sign-off, because what they hold outlives the branch:

- **After `clarify`** – read `prd.md`. Every story is cut from it, and it is the one planning file that survives the merge, unless your requirements live in the tracker.
- **After `decide`**, when it ran – read the ADRs. Every later skill treats them as settled.
- **At the PR** – review it as you would any PR. `ship` lands the observations worth keeping and prints its recommendations for the rest, so read those and settle the review's open `Note` findings, which are decisions left to you, before you say yes to its push-and-PR question.

Two more reads pay off when you have the time: the FIS files after `plan`, with what you decided and what the run assumed listed above the next command, and the review report.

### Smaller work

Two skills change code without a spec:

```bash
/andthen:implement-fix "return 404 instead of 500 for an unknown export job id"   # a change you can state in one sentence
/andthen:triage "tests fail on main since yesterday"                             # something is broken and you don't know why
```

The [Cookbook](COOKBOOK.md) has a recipe for each situation, starting with [choosing a path](COOKBOOK.md#choosing-a-path), and follows [one feature end to end](COOKBOOK.md#the-worked-example-workspace-invitations).


## Core skills

The eight skills most work starts from:

| Skill | What it does |
|---|---|
| `init` | Sets up a project: the document index in `CLAUDE.md` / `AGENTS.md`, the project's test commands, and offers for the optional extras |
| `now-what` | Reads your project state and routes you to the right skill |
| `clarify` | Interviews you about an idea and writes the PRD; `--brief` stops at a shorter `intent.md` you can share first |
| `decide` | Settles technical choices with you and records them as ADRs |
| `plan` | Decides whether the work is one story or several, and writes one FIS per story plus the `plan.json` that tracks them |
| `exec-plan` | Builds one FIS, or every story in a plan, each proven by its checks and reviewed by a fresh subagent |
| `review` | Reviews code, spec conformance, security, or the outcome against the PRD; also reviews PRs |
| `handoff` | Writes a document a fresh session can resume from when a session has to end mid-work |

The other twelve are `implement-fix`, `ship`, `triage`, `testing`, `architecture`, `describe`, `ui-ux-design`, `visual-validation`, `visualize`, `tracker`, `spike`, and `simplify-code`. The [skill reference](plugin/README.md#skills) covers all 20 skills, with every flag and mode.


## Installation

The [quick start](#quick-start) covers both plugin hosts.

<!-- pre-release: delete this section when 1.0 is public -->
### 1.0 release candidate from the develop branch

`IT-HUSET/andthen@develop` follows the release candidates (turn on auto-update under [Host options](#host-options)); `IT-HUSET/andthen@v1.0.0-rc.<N>` pins candidate N. The 0.x and 1.0 marketplaces are both named `andthen`, so remove the old one first. On Claude Code, removing the marketplace also uninstalls its plugin.

```bash
# Claude Code
/plugin marketplace remove andthen             # drops 0.x and its plugin
/plugin marketplace add IT-HUSET/andthen@develop
/plugin install andthen@andthen

# Codex CLI
codex plugin remove andthen@andthen
codex plugin marketplace remove andthen
codex plugin marketplace add IT-HUSET/andthen@develop
codex plugin add andthen@andthen
```

From a checkout of the branch, `python3 scripts/andthen-plugins.py --path .` does all of this on both hosts and checks the installed version. To go back to 0.x, run the same commands with `IT-HUSET/andthen` in place of `IT-HUSET/andthen@develop`.

### Host options

- **Claude Code** – `/plugin install andthen@andthen --scope project` installs for the current project only; the default is your user. Turn on auto-update in `/plugin` → **Marketplaces** → `andthen` → **Enable auto-update**.
- **Codex CLI** – if you used `install-skills.sh` before, delete the old `~/.agents/skills/andthen-*` directories first, or Codex lists every skill twice.

### Other agents (Aider, Cursor, Gemini CLI, opencode)

The installer copies the skills into your agent's skills directory under `andthen-` names, each bundle self-contained. Invoke them with `$andthen-<skill>` in Codex and other agents that read `~/.agents/skills`.

```bash
./scripts/install-skills.sh                                # all skills (default: ~/.agents/skills)
./scripts/install-skills.sh --dry-run                      # preview what it will do
./scripts/install-skills.sh --skills clarify,plan,review   # a subset
./scripts/install-skills.sh --skills-dir <path>            # custom skills directory
./scripts/install-skills.sh --claude-user                  # also install for Claude Code at the user tier
```

A reinstall replaces the skills it installed before but leaves retired ones in place. `--prefix` installs under another name, which is how a toolkit [bundles AndThen](plugin/README.md#bundling-into-a-downstream-toolkit) into its own namespace.


## Project setup

```bash
/andthen:init
```

`init` works on new projects, half-set-up ones, and existing codebases. In an existing repository it asks nothing; in an empty one it asks what the project is. It writes:

- the **Project Document Index** in `CLAUDE.md` / `AGENTS.md`, which tells every skill where your specs and docs live (with both hosts, `AGENTS.md` holds it and `CLAUDE.md` imports it);
- when the project has a manifest (`package.json`, `pyproject.toml`, and the like), a **Key Dev Commands** document with its fast and full test commands;
- two `.gitignore` entries.

Every other document is created by the first skill that needs it. The closing summary offers the optional extras one line each: role agents that pin a model per kind of work, critical rules for your instruction file, a map of an existing codebase (`describe`), and a testing strategy. The [skill reference](plugin/README.md#foundational-rules-and-conversation-style) covers the rules and the optional `concise-critical` conversation style.

To set up by hand instead, start from [`CLAUDE.template.md`](plugin/skills/init/templates/CLAUDE.template.md).


## More

- [`COOKBOOK.md`](COOKBOOK.md) – what to type for each situation, how the workflow fits together, [working in a team](COOKBOOK.md#working-in-a-team), [coming from Spec Kit, Kiro, BMAD, or GSD](COOKBOOK.md#coming-from-spec-kit-kiro-bmad-or-gsd), and a worked example.
- [`plugin/README.md`](plugin/README.md) – the skill reference: every flag, mode, and edge case.
- [`MIGRATING-FROM-0.x.md`](MIGRATING-FROM-0.x.md) – upgrading a 0.x project: what changed, the steps, and a prompt that does them.
- [`docs/PRODUCT.md`](docs/PRODUCT.md) – goals, non-goals, and how AndThen weighs verification against ceremony.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) – how the plugin is built, for contributors.
- [`docs/MODEL-EFFORT-SELECTION-GUIDE.md`](docs/MODEL-EFFORT-SELECTION-GUIDE.md) – choosing models and thinking effort.
- [`hooks/README.md`](hooks/README.md) – four optional Claude Code hooks: block destructive shell commands, desktop or ElevenLabs voice notifications, and a context-size hint, also for Codex, that has the agent suggest a fresh session once a conversation grows long.
- Works well with: [Agent Browser](https://github.com/vercel-labs/agent-browser), and from the [official marketplace](https://github.com/anthropics/claude-plugins-official) `playground` and `claude-md-management`, and [`semgrep`](https://github.com/semgrep/mcp-marketplace) (external, recommended there).


## Evolved From

AndThen evolved from [cc-workflows](https://github.com/tolo/claude_code_common) – a general-purpose AI coding agent toolkit.


## Inspired by _(name)_

[![Dude, Where's My Car?](https://img.youtube.com/vi/oqwzuiSy9y0/0.jpg)](https://www.youtube.com/watch?v=oqwzuiSy9y0)

and then

[![Mullvad](https://img.youtube.com/vi/fPzvUW8qaWY/0.jpg)](https://www.youtube.com/watch?v=fPzvUW8qaWY)


## Actually inspired by

Too many to list, but special shoutout to:
- [Peter Steinberger](https://github.com/steipete)
- [Cole Medin](https://github.com/coleam00) – the split into an outer loop per feature and an inner loop per story, and the habit of saying at each hand-off whether to continue or start fresh
- [IndieDevDan](https://github.com/disler)
- [Matt Maher](https://github.com/bladnman)
- [Mario Zechner](https://github.com/badlogic)
- [Matt Pocock](https://github.com/mattpocock)


## License

MIT
