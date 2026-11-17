# Role Pin Record

The last recalibration's sources, margins, and scored shortlist behind the role templates in `plugin/skills/init/templates/agents/`, chosen by `docs/MODEL-EFFORT-SELECTION-GUIDE.md` § Choosing a role's pin.
The `recalibrate-roles` skill overwrites this file on each run; earlier records are in git history.

## 2026-11-17

Run on OpenAI shipping GPT-6.2 Astra and GPT-6.2 Sol that day.
Every row below was read that day; the Claude rows equal the 2026-11-12 record.

### Sources

Verdicts against the guide's admission items and the checks' coverage clause.

- **Artificial Analysis** (fixed scorer, Intelligence Index v5.0.1, [leaderboard](https://artificialanalysis.ai/leaderboards/models), one page per model family such as `artificialanalysis.ai/models/gpt-6-2-astra`, which carries every effort row): passes all six for both scores.
  Its coding composite passes item 2 by majority weight: FrontierCode-AA 2.0 (60%, private) passes, Terminal-Bench 4.0 (40%, public, rated Flawed by Epoch AI) does not.
  The Intelligence Index passes item 2 by 60% to 40% ([methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)): private AA-Briefcase v1.1 15%, AA-Omniscience v1.1 15%, FrontierCode-AA 2.0 15%, CritPt v2 Hard Subset 10%, AutomationBench-AA 5%; public Terminal-Bench-Science 0.1 15%, Terminal-Bench 4.0 10%, HLE-Diamond 10%, GDP.pdf 5%.
  The pass rests on AA-Omniscience: it also ships a public subset, and AA reports its public and private questions scoring alike (mean difference −0.2 points, [Omniscience](https://artificialanalysis.ai/evaluations/omniscience)); counted public, the private share falls to 45% and the index fails.
  The weights were read on 2026-11-12 and the index version is unchanged.
- **SWE-rebench** (fixed check, [swe-rebench.com](https://swe-rebench.com)): passes items 1–3, fails the coverage clause for the second run in a row.
  Its newest window (2026-05-15 to 2026-07-01) scores only the previous generation.
- **DeepSWE** (fixed check, [deepswe.datacurve.ai](https://deepswe.datacurve.ai/)): passes items 1–3, fails the coverage clause for the second run in a row.
  Updated 2026-09-22; of the compared models it scores only GPT-6 Astra.
- **AA Coding Agent Index** (found, [artificialanalysis.ai/agents/coding](https://artificialanalysis.ai/agents/coding)): fails the coverage clause, because it scores one effort (max, in the Codex harness) and no pin uses max.
  AA's launch thread reports GPT-6.2 Sol 3 points below GPT-6.1 Sol there and GPT-6.2 Astra flat with GPT-6 Astra ([post](https://x.com/ArtificialAnlys/status/2122750637041693183), read from a search snippet, not the post).
- No other coding benchmark published or refreshed since 2026-11-12 was found; the found sources that record failed were not re-tested.

Both fixed checks have now failed two runs running, but no found source passed, so the guide's replacement condition does not hold.
No check could compare any pick, so every pin below rests on Artificial Analysis alone.

### Scores and margins

- **Coding score**: AA's coding category, FrontierCode-AA 2.0 at 60% (132 private tasks, merge-graded) plus Terminal-Bench 4.0 at 40%.
- **General score**: the Intelligence Index.
- **Cost**: the measured cost of one full index run at list prices with cache pricing applied, comparable between pairs, not a per-task dollar forecast.
- **Margins**: coding 7, general 3, estimated from task counts (132 FrontierCode-AA tasks dominate the coding composite) because AA publishes no intervals.

### Stage 1 evidence

- **Mid flagship for `implementer` and `reviewer`**: Anthropic calls Opus 5.5 the "strongest daily driver" and the starting point for most coding ([Fable 5.2 launch](https://www.anthropic.com/claude-fable-and-mythos-5-2)); OpenAI calls GPT-6.2 Sol its "efficient, versatile model for everyday work" beside Astra "for your hardest projects" ([GPT-6.2 launch](https://openai.com/index/introducing-gpt-6-2-astra-sol/)) and gives Sol "fixing bugs and adding features in an existing codebase" ([model selection](https://developers.openai.com/api/docs/guides/model-selection)).
  That guide no longer lists GPT-6.1 Sol, so GPT-6.2 Sol is the eligible model.
- **Top model reserved for `oracle`**: a practitioner's first week on Fable 5.2 kept Opus as the daily default because Fable needed more supervision and was slower to review (Theo, via a [secondary summary](https://finance.biggo.com/news/a090bf89b921a843)).
- **Small models out of edits**: Anthropic positions Haiku 5.5 as a subagent beside Opus or Sonnet, which stay better for complex agentic coding ([Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5)); Anthropic's guide keeps code edits on the main model ([claude.dev](https://claude.dev/blog/which-claude-model-should-you-build-with/)); Bito's runs confine Luna to "lookups you will verify yourself" ([Bito](https://bito.ai/blog/gpt-6-1-terra-vs-gpt-6-1-sol-vs-gpt-6-luna/)).
- **No `max`**: OpenAI's model-selection guide recommends no max setting; the Vals Index scores Fable 5.2 best at high, above xhigh and max, and Anthropic staff advise reserving xhigh for the hardest problems ([Latent Space](https://latent.space/p/ainews-fable-5-2-retakes-world-1-llm-spot-as-ant-ipo-roadshow-begins/)).

### Shortlist

| Pair | Coding | General | Run cost | Decision |
|---|---|---|---|---|
| Fable high | 53.3 | 61.8 | $7,106 | Claude `oracle`, kept |
| Fable xhigh | 53.2 | 62.2 | $11,742 | best general score, non-max |
| Opus xhigh | 50.1 | 57.4 | $4,766 | Opus's best coding score, non-max |
| Opus high | 44.2 | 51.8 | $2,716 | Claude `implementer`, kept |
| Opus medium | 40.9 | 48.2 | $2,031 | Claude `reviewer`, kept |
| Sonnet high | 33.0 | 41.5 | $1,268 | |
| Haiku high | 22.6 | 29.9 | $121 | Claude `worker`, kept (floor 22.1) |
| Astra 6.2 xhigh | 55.0 | 61.6 | $2,484 | best general score, non-max; the `oracle` bar is 58.6 |
| Astra 6.2 high | 52.3 | 60.1 | $2,007 | Codex `oracle`, was Sol 6.1 xhigh: cheapest pair over the bar |
| Astra 6.2 medium | 51.4 | 57.0 | $1,457 | under the `oracle` bar |
| Sol 6.2 xhigh | 48.1 | 55.7 | $698 | Sol's best coding score, non-max |
| Sol 6.2 high | 47.6 | 54.9 | $553 | Codex `implementer`, was Sol 6.1 high: Sol 6.2 medium is within the margin but only 27% cheaper |
| Sol 6.2 medium | 47.3 | 52.7 | $405 | Codex `reviewer`, was Sol 6.1 medium |
| Sol 6.1 xhigh | 44.7 | 52.5 | $718 | previous Codex `oracle` |
| Sol 6.1 high | 42.6 | 50.3 | $573 | previous Codex `implementer` |
| Sol 6.1 medium | 39.2 | 46.3 | $389 | previous Codex `reviewer` |
| Terra medium | 33.7 | 38.2 | $190 | Codex `worker`, kept (floor 23.8) |
| Terra low | 20.8 | 29.4 | $111 | below the worker floor |
| Luna xhigh | 14.3 | 23.5 | $86 | below the worker floor |

Copilot keeps all four lists, `oracle`, `implementer`, and `reviewer` on `[claude-opus-5.5, gpt-6.1-sol]` and `worker` on `[claude-haiku-5.5, gpt-6.1-terra]`, because GitHub's [supported-models page](https://docs.github.com/en/copilot/reference/ai-models/supported-models) and its changelog list no GPT-6.2 model on 2026-11-17.
Once it lists them, the OpenAI entries become `gpt-6.2-astra` for `oracle` and `gpt-6.2-sol` for `implementer` and `reviewer`.
Its `oracle` stays on Opus because GitHub publishes no Copilot CLI ID for Claude Fable 5.2.

### Method change: a successor on the same rung

The guide's change rule compared the rule's pick with the current pin and did not say what happens when Stage 1 retires the current pin's model.
Read literally against Sol 6.1 high, the pick (Sol 6.2 medium, 4.6 coding points up and 29% cheaper) cleared neither threshold and the Codex `implementer` would have stayed on a model OpenAI no longer recommends.
This run moved the pin to the successor at the same effort and applied the change rule from there, which kept `high`; the maintainer confirmed that reading on 2026-11-17 and the guide's change rule now states it.
The evidence for the move itself is thin: 4.9 coding points at `high` is inside the margin of 7, and AA's Codex-harness index reports Sol 6.2 below Sol 6.1 at max.

### Open question: Claude `oracle` at `medium`

The rule keeps Fable at high: Fable medium's general score is 56.4 ([AA](https://artificialanalysis.ai/models/claude-fable-5-2-medium)), outside the margin of the best pair's 62.2, at $3.80 against $9.08 per index task for high.
A task-specific measurement on 2026-11-12 found no loss at medium on spec review, the shape of `plan`'s `oracle` gate (tables and limits in `docs/adrs/ADR-031-oracle-at-two-gates.md`, Context):

- Plan self-review, 12 runs per arm, blind scorer: Fable medium found 32 of 32 planted gaps and 13 build-changing others, Fable high 32 and 12, at $1.53 against $3.33 per review.
- Plan second opinion, 4 runs per effort, unblinded scorers: medium raised 6 of 6 build-changing gaps the reviewer missed, high 5 of 6, at $1.69 against $2.89 per run.

It was kept at high because two small bundles and eight unblinded runs on one task shape do not outweigh an independent general score, and the hand-over and `decide` jobs it never ran are the ones the depth is for; no mechanism lets one gate run below the role's effort.
Reopen on a larger blinded run across the `oracle`'s jobs; a move to medium also redoes ADR-031's cost lines.
