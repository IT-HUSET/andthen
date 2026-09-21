# Product: AndThen

## Purpose

AndThen is a lightweight spec-driven development framework for AI coding agents. Help developers and teams turn intent into verified changes with fewer omissions, less rework, and less supervision. Support integration through explicit artifact contracts.

## Decision Rule

Choose the smallest approach that meets the requirement and verification bar, including extending what exists or making no change. Justify every addition by the outcome it enables or failure it prevents: steps, artifacts, dependencies, configuration, agent calls, instructions, rules, checks. A new instruction or check names the run where the model did the wrong thing without it.

Apply it to existing design in scope, not only new proposals. Simplify machinery whose benefit no longer justifies its cost – judgment, not another approval step or document.

## Product Principles

- **Lean:** keep one source of truth; rework it instead of layering on duplicates, exceptions, and bookkeeping.
- **Lightweight:** make individual skills useful without adopting the whole pipeline. Keep dependencies few and context loaded only when needed.
- **Efficient:** optimize total cost through verified completion, not local savings that increase failures or rework.
- **Pragmatic:** size planning, specification, and review to scope, uncertainty, and consequences.
- **Flexible:** respect existing project locations, tools, and conventions. Keep artifacts readable across supported hosts.
- **Effective:** prove the intended behavior with evidence its author did not produce – an executed test, a fresh-context reader. A pass re-reading its own output is not verification; remove it by an explicit workflow change, never skip an active gate.
- **Intent-driven:** state outcomes, constraints, and reasons for non-obvious rules; prescribe procedure only where a contract requires it. A capable model does routine work right unprompted; instructing it changes nothing and dilutes the rules that do.

## Non-Goals

- A mandatory methodology or fixed project layout.
- Replacing coding agents, execution platforms, or project-management systems.
- Permanent synchronization of specifications with code: governing artifacts are branch-scoped, product intent and lessons durable.

## Proportionality

<!-- pre-release: drop "release candidate" at 1.0.0 -->
- **Stage:** experimental framework, distributed as a 1.0 release candidate. Adopting projects set their own criticality and verification requirements.
- **Scale:** users, active maintainers, and artifact volume are unknown; establish requirements before designing for assumed scale.
- **Distribution:** one source plugin directory; agent hosts or loose-skill installs; no build step or AndThen-operated service.
- **Runtime:** prompts and assets for workflows; Python 3 standard library for the tracker projection, the one shipped script.
- **Standing technical non-goals:** no required hosted control plane, no central workflow database, and no duplicated downstream adapters. Keep workflow state with its owning local artifact.

## Success Indicators

Compare equivalent tasks at the same verification bar: requirements met, escaped defects, rework, tokens, elapsed time, human intervention. Count setup and failed attempts. Skill counts, document volume, and completed workflow steps are not evidence of value.

No baselines exist; never report an expectation as a measurement.
