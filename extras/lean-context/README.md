# Lean context

Three example Claude Code settings files that remove tools from every request: `trim` drops the two largest tools almost nobody calls, `focused` also drops workflows, timed wake-ups and the CLI's claude.ai connectors, and `minimal` also drops the built-in browser and question cards. Pick one and copy it into a project. Nothing here is installed by the plugin.

## What a session starts with

Before your first message, Claude Code sends its tool definitions, a listing of every installed skill, your instruction files, and a list of deferred tool names. Measured on one developer machine with about 100 skills installed:

| Surface | First request |
|---|--:|
| Desktop app, Code tab | 95,725 tokens |
| CLI (`claude` or `claude -p`) | 40,386 tokens |
| CLI subagent (`worker`, general-purpose) | 34,000 tokens |

The desktop app costs more because it adds its own tools. The Artifact tool alone is about 18,000 tokens, and it was called in 12 of 7,068 transcripts between July and November. Desktop subagents get the same tools, so a desktop subagent starts at about 62,700 tokens.

## The three files

Each file is complete on its own; a stricter one includes everything the lighter ones remove. Every entry removes more than 1,000 tokens per request. Use counts are from the same machine's transcripts, July to November.

| File | Removes (tokens per request) | Desktop first request | You lose |
|---|---|--:|---|
| [`settings.trim.json`](claude/settings.trim.json) | Artifact (~11,600; 12 transcripts used it), the iOS Simulator (~2,200; 8, all in iOS apps) | 86,898 → ~62,800 | Publishing pages to claude.ai, running an iOS app |
| [`settings.focused.json`](claude/settings.focused.json) | The trim set, plus Workflow (~1,700; 5), ScheduleWakeup (~1,500; 40, AndThen eval runs among them), and the claude.ai connectors on the CLI (~1,900) | ~58,400 | Dynamic workflows (`ultracode`), `/loop` without an interval, claude.ai connectors in the CLI |
| [`settings.minimal.json`](claude/settings.minimal.json) | The focused set, plus the built-in browser (~6,500; 35 of 231 desktop sessions) and AskUserQuestion (~1,450) | ~50,500 | Previewing local pages, question cards (questions arrive as text) |

All figures are billed input tokens of the first request for a one-word prompt on Claude Code 2.1.330, in an empty git repository holding only the tier file, so the baseline sits below the 95,725 of a real project. The per-entry costs are medians across 615 desktop sessions. The tier figures are estimates: runs measured when the files also held the small entries listed below, minus those entries' measured costs. On the CLI only `focused` and `minimal` make a difference, about 3,900 tokens (38,428 → about 34,500 in this repository), because Artifact, the iOS Simulator and the built-in browser exist only in the desktop app.

Put the file in a project's `.claude/settings.local.json`, or `.claude/settings.json` to share it with the team, or pass it for one session with `claude --settings <path>`. Put it at the repository root: a session started in a subfolder of a git repository still reads it there, but outside a git repository only the start folder's `.claude/` is read. In an iOS project, delete the `mcp__Claude_Code_iOS_Simulator` line.

## How the keys behave

- **A deny on a tool or server name removes its definitions and deferred names from the request**, not just the call, and this holds for the desktop app's own servers too. It does not reliably remove the server's instruction block: Claude in Chrome's block went with its deny, but computer use's (about 2,300 tokens) stayed in every tier, and so did Context7's on the CLI. To drop such a block, turn the server off itself: computer use in the app's settings, a configured server with `/mcp` or by removing it from `.mcp.json`. The desktop system prompt's sections on the iOS Simulator and the browsers (about 1,800 tokens) also stay when their tools are denied.
- **Small entries are left out, because most servers' tools are deferred and a deny removes only their names.** Measured per request: SendUserFile ~1,000, ReportFindings ~700, ReadNotifications ~650, the Claude Docs connector ~600, Claude in Chrome ~450, ListAgents ~370, the terminal panel tools ~350, the bundled skills' listing ~1,300 (nothing while the listing sits at its cap, see below), and computer use, scheduled tasks and the connector registry a few hundred each. Deny one by its tool or server name when you never use it. The desktop app names some claude.ai connectors by an ID (the Docs connector is `mcp__1a59c906-04da-521d-bda7-7f71b9f9e01c`), so find the name in the MCP tools list of `/context`. `disableClaudeAiConnectors` reaches the CLI only.
- **A project file can turn Artifact off but never on.**
- **Don't lower the skill budget.** The listing is capped at 1% of the context window and sits at the cap when many plugins are installed. At `skillListingBudgetFraction: 0.004`, 10 of AndThen's 21 skills lost their descriptions, so a request no longer matched them. Removing whole plugins helps only a little for the same reason: the remaining skills get their cut descriptions back.
- **The compaction window is a separate lever.** This overhead is sent with every request, and neither `/clear` nor compaction removes it. An earlier window (`CLAUDE_CODE_AUTO_COMPACT_WINDOW`, or `autoCompactWindow` under `modelSettings`) trades detail an autonomous run may still need for a smaller context, and no measurement here says where that pays.

## Reading `/context`

The total counts what is sent. The rows `MCP tools (deferred)` and `System tools (deferred)` list full definitions that load only when a tool is searched for; until then only their names are sent, and the total leaves those rows out. The `System tools` row may also miss the Artifact tool: in one session the categories added up to about 80,000 tokens against 95,725 billed.

## Not in any file

These depend on what you have installed and use:

- **Plugins you don't use in this project:** `"enabledPlugins": { "<plugin>@<marketplace>": false }`. Run `/skill-doctor` to see skills that are never invoked.
- **One skill you don't use:** `"skillOverrides": { "<skill>": "off" }`, or `"name-only"` to keep only its name. This does not work for plugin skills.
- **Project MCP servers you don't call:** remove them from `.mcp.json`, or switch them off per project with `/mcp`. A `dart` server listed in 148 desktop sessions was never called.
- **Instruction files from other projects:** `claudeMdExcludes` with absolute-path globs, such as a parent folder's `CLAUDE.md`.
- **Subagents:** the deny rules reach subagents too, but a desktop subagent also gets the task-list tools (about 2,800 tokens) and the session tools (about 1,300), and used them in under 4% of runs. Only a role agent with a `tools:` list leaves them out. On the CLI, a worker with only file and shell tools started at 15,481 tokens instead of 34,024, because without the Skill tool it also gets no skill listing.

Two desktop costs have no switch: the system prompt's sections on starting other sessions (about 4,400 tokens) and on the task list (about 1,600, plus 2,800 of tools).

## Measure your own

`/context` shows the categories of the current session. For an exact count per part, point the CLI at a local logging proxy that forwards each request to `api.anthropic.com` and writes its body to disk (`ANTHROPIC_BASE_URL=http://localhost:8787 claude`); the response's `usage` gives the billed tokens. The desktop app ignores that variable, but its session transcript in `~/.claude/projects/` stores the request's tools and system prompt.
