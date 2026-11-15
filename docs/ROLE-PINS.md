# Role Pin Record

The last recalibration's sources, margins, and scored shortlist behind the role templates in `plugin/skills/init/templates/agents/`, chosen by `docs/MODEL-EFFORT-SELECTION-GUIDE.md` § Choosing a role's pin.
The `recalibrate-roles` skill overwrites this file on each run; earlier records are in git history.

## 2026-11-12

### Sources

Verdicts against the guide's admission items and the checks' coverage clause.
This is the first run under the fixed-source rule, so no fixed source has a previous failure.

- **Artificial Analysis** (fixed scorer, Intelligence Index v5.0.1, [leaderboard](https://artificialanalysis.ai/leaderboards/models), per-model pages such as `artificialanalysis.ai/models/claude-opus-5-5-high`): passes all six for both scores.
  Its coding composite passes item 2 by majority weight: FrontierCode-AA 2.0 (60%, private) passes, Terminal-Bench 4.0 (40%, public, rated Flawed by Epoch AI) does not.
  The Intelligence Index passes item 2 by 60% to 40% ([methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)): private AA-Briefcase v1.1 15%, AA-Omniscience v1.1 15%, FrontierCode-AA 2.0 15%, CritPt v2 Hard Subset 10%, AutomationBench-AA 5%; public Terminal-Bench-Science 0.1 15%, Terminal-Bench 4.0 10%, HLE-Diamond 10%, GDP.pdf 5%.
  The pass rests on AA-Omniscience: it also ships a public subset, and AA reports its public and private questions scoring alike (mean difference −0.2 points, [Omniscience](https://artificialanalysis.ai/evaluations/omniscience)); counted public, the private share falls to 45% and the index fails.
- **SWE-rebench** (fixed check, [swe-rebench.com](https://swe-rebench.com)): passes items 1–3, fails the coverage clause.
  Its newest window (2026-05-15 to 2026-07-01) scores only the previous generation.
- **DeepSWE** (fixed check, [deepswe.datacurve.ai](https://deepswe.datacurve.ai/)): passes items 1–3, fails the coverage clause.
  Updated 2026-09-22; of the current lineup it scores only GPT-6 Astra.
- **Vals.ai Vibe Code Bench** (found, [vals.ai](https://www.vals.ai)): fails item 1, task source undisclosed.
  The only independent coding benchmark covering all eight current models; it has no effort rows.
- **Cognition FrontierCode 1.1** (found, [cognition.ai](https://cognition.ai)): fails item 3, because Cognition ships its own coding models.
- **SWE-bench Verified** (found, [swebench.com](https://www.swebench.com)): fails item 2, contaminated.
- **SWE-bench Pro** (found, [scale.com/leaderboard](https://scale.com/leaderboard)): the public split fails item 2 (public repositories); the held-out and commercial splits fail the coverage clause.
- **BenchLM** (found, [benchlm.ai](https://benchlm.ai)): fails item 1, an aggregator with undisclosed weights and 53% vendor-reported results.
- **LiveBench** (found, [livebench.ai](https://livebench.ai)): fails the coverage clause, last confirmed release 2025-04-25.
- **Epoch AI Benchmarking Hub** (found, [epoch.ai/benchmarks](https://epoch.ai/benchmarks)): its one coding benchmark is SWE-bench Verified, so it fails item 2.

No check could compare any pick, so every pin below rests on Artificial Analysis alone.

### Scores and margins

- **Coding score**: AA's coding category, FrontierCode-AA 2.0 at 60% (132 private tasks, merge-graded) plus Terminal-Bench 4.0 at 40%.
- **General score**: the Intelligence Index.
- **Cost**: the measured cost of one full index run at list prices with cache pricing applied, comparable between pairs, not a per-task dollar forecast.
- **Margins**: coding 7, general 3, estimated from task counts (132 FrontierCode-AA tasks dominate the coding composite) because AA publishes no intervals.

### Stage 1 evidence

- **Mid flagship for `implementer` and `reviewer`**: Anthropic calls Opus 5.5 the "strongest daily driver" and the starting point for most coding ([Fable 5.2 launch](https://www.anthropic.com/claude-fable-and-mythos-5-2)); OpenAI points Sol at "complex technical work" ([model selection](https://developers.openai.com/api/docs/guides/model-selection)).
- **Top model reserved for `oracle`**: a practitioner's first week on Fable 5.2 kept Opus as the daily default because Fable needed more supervision and was slower to review (Theo, via a [secondary summary](https://finance.biggo.com/news/a090bf89b921a843)).
- **Small models out of edits**: Anthropic positions Haiku 5.5 as a subagent beside Opus or Sonnet, which stay better for complex agentic coding ([Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5)); Anthropic's guide keeps code edits on the main model ([claude.dev](https://claude.dev/blog/which-claude-model-should-you-build-with/)); Bito's runs confine Luna to "lookups you will verify yourself" ([Bito](https://bito.ai/blog/gpt-6-1-terra-vs-gpt-6-1-sol-vs-gpt-6-luna/)).
- **No `max`**: OpenAI's model-selection guide recommends no max setting; the Vals Index scores Fable 5.2 best at high, above xhigh and max, and Anthropic staff advise reserving xhigh for the hardest problems ([Latent Space](https://latent.space/p/ainews-fable-5-2-retakes-world-1-llm-spot-as-ant-ipo-roadshow-begins/)).

### Shortlist

| Pair | Coding | General | Run cost | Decision |
|---|---|---|---|---|
| Fable high | 53.3 | 61.8 | $7,106 | Claude `oracle`, kept |
| Fable xhigh | 53.2 | 62.2 | $11,742 | best general score, non-max |
| Opus xhigh | 50.1 | 57.4 | $4,766 | Opus's best coding score, non-max |
| Opus high | 44.2 | 51.8 | $2,716 | Claude `implementer`, was Sonnet high |
| Opus medium | 40.9 | 48.2 | $2,031 | Claude `reviewer`, kept; outside the implementer margin |
| Sonnet high | 33.0 | 41.5 | $1,268 | previous Claude `implementer` |
| Haiku high | 22.6 | 29.9 | $121 | Claude `worker`, kept (floor 22.1) |
| Astra xhigh | 48.7 | 55.3 | $3,746 | best general score, non-max |
| Sol xhigh | 44.7 | 52.5 | $718 | Codex `oracle`, kept |
| Sol high | 42.6 | 50.3 | $573 | Codex `implementer`, kept: Sol medium is within the margin but only 32% cheaper |
| Sol medium | 39.2 | 46.3 | $389 | Codex `reviewer`, kept |
| Terra medium | 33.6 | 38.2 | $190 | Codex `worker`, was Luna high (floor 21.3) |
| Terra low | 20.8 | 29.4 | $111 | below the worker floor |
| Luna high | 13.0 | 21.4 | $63 | below the worker floor |

Copilot follows each provider's pick: `implementer` `[claude-opus-5.5, gpt-6.1-sol]` at high, `worker` `[claude-haiku-5.5, gpt-6.1-terra]` at high.
Its `oracle` stays on Opus because GitHub publishes no Copilot CLI ID for Claude Fable 5.2.

### Open question: Claude `oracle` at `medium`

The rule keeps Fable at high: Fable medium's general score is 56.4 ([AA](https://artificialanalysis.ai/models/claude-fable-5-2-medium)), outside the margin of the best pair's 62.2, at $3.80 against $9.08 per index task for high.
A task-specific measurement on 2026-11-12 found no loss at medium on spec review, the shape of `plan`'s `oracle` gate (tables and limits in `docs/adrs/ADR-031-oracle-at-two-gates.md`, Context):

- Plan self-review, 12 runs per arm, blind scorer: Fable medium found 32 of 32 planted gaps and 13 build-changing others, Fable high 32 and 12, at $1.53 against $3.33 per review.
- Plan second opinion, 4 runs per effort, unblinded scorers: medium raised 6 of 6 build-changing gaps the reviewer missed, high 5 of 6, at $1.69 against $2.89 per run.

It was kept at high because two small bundles and eight unblinded runs on one task shape do not outweigh an independent general score, and the hand-over and `decide` jobs it never ran are the ones the depth is for; no mechanism lets one gate run below the role's effort.
Reopen on a larger blinded run across the `oracle`'s jobs; a move to medium also redoes ADR-031's cost lines.
