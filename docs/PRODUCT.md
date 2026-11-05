# Product: AndThen

## Vision

AndThen is a lightweight agentic software engineering framework for AI coding agents, with spec-driven development as its main workflow. It helps developers and teams turn intent into verified changes.

## Target Users

- **Developers and teams using an AI coding agent** (Claude Code, Codex CLI, GitHub Copilot CLI, or another agent through loose skills): have the agent build against a spec they agreed to.

## Value Propositions

- Aims for fewer omissions, less rework, and less supervision on the way from intent to a verified change. Not yet measured (see Success Metrics).
- Integration through files: other tools work with its artifacts' documented shapes (PRD, `plan.json`, FIS, review report), not through an API or service.

## Product Principles

- **Decision Rule:** Choose the smallest approach that meets the requirement and its verification bar; extending what exists, or changing nothing, is always a candidate. Every addition – a step, artifact, dependency, configuration, agent call, instruction, rule, or check – names the outcome it enables or the failure it prevents. A new instruction or check also covers a path most runs take or a failure that is destructive or silent. Analysis establishes the need when the text omits a step, gives an output no home, or directs the wrong behaviour; a claim that the model goes wrong where the text is silent needs the run where it did, because without that run the instruction may change nothing (**Intent-driven**).

  The rule covers existing design in scope, not only proposals: simplify or remove machinery whose benefit no longer covers its cost. That is judgment, not another approval step or document.
- **Lean:** one source of truth per fact; rework it rather than layering duplicates, exceptions, and bookkeeping on top.
- **Lightweight:** each skill is useful without adopting the whole pipeline. Dependencies stay few, and context loads only when a path needs it.
- **Efficient:** optimize total cost to a verified completion, not local savings that raise failures or rework.
- **Pragmatic:** size planning, specification, and review to scope, uncertainty, and consequence – a one-line fix needs no PRD.
- **Flexible:** adapt to the project and the run at hand. Respect the project's existing locations, tools, and conventions, and keep artifacts readable on every supported host. Word each instruction as generally as the skill's purpose allows, so it fits runs its author did not picture. Strictness – a fixed procedure, format, order, or input check – stands only where a contract, a gate, or a recorded failure needs it.
- **Robust:** follow Postel's law – write artifacts to their templates, read input leniently. A missing field, a partial header, or an off-template file gets its best reading, recorded where it matters, and the run continues. Stop only when the run cannot proceed, never on form alone.
- **Verified:** prove intended behavior with evidence its author did not produce – an executed test, a fresh-context reader. A pass that re-reads its own output is not verification. Remove such a pass by an explicit workflow change; a run never skips an active gate.
- **Intent-driven:** state outcomes, constraints, and the reason behind each non-obvious rule. A capable model does routine work unprompted, so instructing it changes nothing and dilutes the rules that matter.
- **Readable:** agents execute skill and reference files, people maintain them. Plain, concise language; a scannable structure with the flow visible at a glance, one concern per paragraph, and file links gathered where a file loads, not threaded through the prose.

## Non-Goals

- A mandatory methodology, a fixed project layout, or a rigid input format.
- Replacing coding agents, execution platforms, or project-management systems.
- Keeping specs in sync with code after merge. `plan.json` and each FIS govern one branch, and `ship` deletes them before its merge unless the user keeps them as an unmaintained record; the Product document, PRDs, Learnings, and Decisions stay. A spec maintained past merge is a second record of what the code already states.

## Proportionality

- **Stage**: experimental framework, distributed as 1.0. Each adopting project sets its own criticality and verification bar.
- **Scale**: users, active maintainers, and artifact volume are unknown; size nothing against assumed scale.
- **Distribution**: one `plugin/` directory under Claude Code and Codex manifests, the Claude Code pair also serving Copilot CLI, plus a loose-skill installer for other agents; no build step and no AndThen-operated service.
- **Runtime**: prompts and assets only; no shipped script.
- **Standing technical non-goals**: no required hosted control plane, no central workflow database, no duplicated downstream adapters. Workflow state lives in the local artifact that owns it.

## Success Metrics

Compare equivalent tasks at the same verification bar on requirements met, escaped defects, rework, tokens, elapsed time, and human intervention, counting setup and failed attempts. Skill counts, document volume, and completed workflow steps are not evidence of value.

No baseline exists. The eval harness (`evals/`) checks that skills behave as specified on Claude Code and Codex; it does not compare against working without AndThen. Never report an expectation, or an eval pass rate, as a measured gain.
