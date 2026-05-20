# Shared Review Council Reviewer Roster

Total council size is 5-7 for **within-lens councils** (code or security). Three roles are always included; pick 2-4 scope-relevant specialists on top. Prefer the installed custom agent name when available; otherwise use the focus text here as the inline persona prompt.

For the **cross-lens chain pass** (`--council` on a 2+ lens chain, see `council-mode.md` § *Cross-Lens Chain Mode*), the council is fixed at the 3-role spine below – no additional specialists – because per-lens reviews already produced specialist coverage.

## Always Include

The find/filter/synthesize spine of the council:

| Council role | Installed agent | Focus |
|---|---|---|
| **Critic Reviewer** | `review-critic` | Primary finding role that attacks fragile assumptions, unhappy paths, hidden coupling, guessed behavior, and incomplete wiring. Applies `${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`, `${CLAUDE_PLUGIN_ROOT}/references/critic-calibration.md`, and `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`. |
| **Devil's Advocate** | `review-devils-advocate` | Findings-filter role that validates, downgrades, withdraws, or disputes collected findings. Does not add findings. |
| **Synthesis Challenger** | `review-synthesis-challenger` | Final filter pass for severity consistency, overlap, systemic framing, clean-result proof, and false positives. Does not add unrelated findings. |

## Specialists

| Council role | Installed agent | Focus |
|---|---|---|
| **Correctness Reviewer** | `review-correctness` | Behavior, data flow, edge cases, error handling, concurrency, and tests that prove intent. |
| **Security Sentinel** | `review-security` | Auth, authorization, validation, trust boundaries, secrets, exploitability, LLM/agent attack paths, and supply-chain risk. |
| **Architecture Strategist** | `review-architecture` | Boundaries, coupling, abstractions, domain alignment, resilience, and maintainability. |
| **Test Strategist** | `review-testing` | Coverage quality, missing scenarios, weak assertions, verification gaps, and regression proof. |
| **Project Standards Reviewer** | `review-project-standards` | Local conventions, repo guidelines, naming, maintainability, documentation drift, and agent-instruction compliance. |
| **Product Requirements Reviewer** | `review-product-requirements` | User value, scope fit, acceptance criteria, edge cases, feature intent, and requirements gaps. |
| **Agent Workflow Reviewer** | `review-agent-workflow` | Skills, prompts, custom agents, install-time rewrites, routing contracts, and AI workflow ergonomics. |

## Selection Examples

Code-mode councils:

- **Product feature**: Product Requirements Reviewer, Correctness Reviewer, Architecture Strategist, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **Backend/API work**: Correctness Reviewer, Architecture Strategist, Test Strategist, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **Frontend/UI work**: Product Requirements Reviewer, Correctness Reviewer, Test Strategist, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **Prompt/skill/agent workflow**: Agent Workflow Reviewer, Project Standards Reviewer, Test Strategist, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **Small infrastructure/config change**: Architecture Strategist, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger

Security-mode councils:

- **Web app surface**: Security Sentinel, Correctness Reviewer, Architecture Strategist, Test Strategist, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **API / network-exposed**: Security Sentinel, Correctness Reviewer, Architecture Strategist, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **LLM / agent flows**: Security Sentinel, Agent Workflow Reviewer, Architecture Strategist, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger
- **Supply chain / CI/CD / IaC**: Security Sentinel, Agent Workflow Reviewer, Project Standards Reviewer, Critic Reviewer, Devil's Advocate, Synthesis Challenger
