# Refactor Invariants

Cross-file invariant pass for the `code` and `gap` lenses. Load when the diff
shape triggers any of the conditions below. Targets the class of issue that
hunk-by-hunk review structurally misses on refactors: invariants no single hunk
hosts. Findings merge into the primary lens's severity sections – this is not a
separate mode or report.

## Contents
- Trigger Conditions (any one)
- Invariant Checks: 1 Deletion completeness · 2 Resolve-once-consume-many · 3 Lifecycle relocation · 4 Generated-artifact obedience · 5 Schema/data migration · 6 Parameter threading
- How to Run · Composition

> **Why this pass exists**: each diff hunk can be self-consistent while the
> diff as a whole violates an invariant (deleted symbol with a remaining caller
> in another file; cache introduced but a downstream consumer re-derives the
> value; validation moved to a new lifecycle stage but the migrated test still
> exercises the old stage). The find-pass calibrations elsewhere target
> code-level defects; this one targets diff-level defects.


## Trigger Conditions (any one)

- Diff deletes a file, public symbol, exported member, or configuration/schema key
- Diff renames or moves a symbol or file (git rename detection, or grep-detectable rename)
- Diff introduces a cache, memoized value, or "resolve once, consume many" result
- Diff moves a check between lifecycle stages (load-time → runtime, build-time → install-time, sync → async, validator → preflight, …)
- Diff generates artifacts that must obey the same rules as authored ones (codegen, synthetic config, scaffolded steps)
- Diff migrates data shape across a schema/storage boundary (frontmatter relocation, column move, file-format change)
- Diff threads a new required parameter through helper signatures

If none fire, skip this pass.


## Invariant Checks

Apply only the checks whose trigger fired. Each finding must be backed by
project-native search evidence (`rg`, `ast-grep`, IDE find-references, language
LSP) – do not assert from memory.

### 1. Deletion completeness

For every deleted symbol, file, or key, prove no remaining reference exists in:
- Production code (all packages/modules/apps)
- Tests (deleted, not skipped; orphan fixtures cleaned)
- Registration sites (routes, exports, barrels, DI containers, plugin manifests, build configs)
- Documentation (README, architecture docs, CHANGELOG, inline comments, user guides)
- Downstream skills, CLIs, scripts, or external tooling that referenced the symbol

> *Finding template*: "Deleted `<symbol>`; remaining reference at `<path>:<line>` is not unwired. Will compile/lint clean but is dead, misleading, or routes to a removed handler."

### 2. Resolve-once, consume-many

For every cache, memoized result, or "resolved value" the diff introduces, list
every consumer. For each consumer, verify it reads the resolved value rather
than re-deriving it. A second derivation site is a finding even when it
produces the same value today.

> *Finding template*: "`<consumer>` at `<path>:<line>` re-derives `<value>` instead of reading the cached `<name>` introduced at `<path>:<line>`. Will silently desync if derivation logic, inputs, or upstream resolution changes."

### 3. Lifecycle relocation

When a check (validation, authorization, normalization, …) moves between
lifecycle stages, verify:
- Old call sites are removed (not commented, not feature-gated)
- Tests for the check exist at the new stage **and would fail against the
  pre-change code** – i.e. they exercise the new mechanism, not the old one
  passed under a new name
- Documentation that promised the old timing is updated; downstream consumers
  that assumed the old timing are re-anchored

> *Finding template*: "`<check>` moved from `<old stage>` to `<new stage>`, but `<test/doc/consumer>` is still anchored to `<old stage>`. The test passes against the old code as well, so it does not prove the relocation."

### 4. Generated-artifact obedience

For every synthetic/generated artifact the diff introduces (codegen output,
scaffolded steps, synthetic config blocks), verify it passes the same
validators, preflight checks, and invariants as authored artifacts.

> *Finding template*: "Synthetic `<kind>` generated at `<path>:<line>` bypasses `<validator/preflight/invariant>` that authored `<kind>` instances satisfy. Authoring errors in the generator surface only at runtime, after the bypass."

### 5. Schema / data migration

When a field moves between schema versions, frontmatter blocks, or storage
locations, prove behavior equivalence via a contract test, not by reading the
code. Inlined defaults, fallback chains, and override precedence are the
typical drift surfaces.

> *Finding template*: "Field `<field>` relocated from `<old location>` to `<new location>`; no contract test compares pre/post resolved behavior. Equivalence asserted from code reading alone is insufficient – override precedence and fallback chains drift silently."

### 6. Parameter threading

When a new parameter encodes a correctness invariant, verify every call site
provides it. A defaulted or optional parameter where the value is required for
correctness is a finding – the default silently re-introduces the bug the
parameter was added to prevent.

> *Finding template*: "Helper `<fn>` accepts `<param>` to preserve `<invariant>`, but caller `<path>:<line>` omits it and relies on the default. Default-valued correctness parameter masks call sites that should have been updated."


## How to Run

Run after the primary lens's find-pass collects standard findings, before the
Findings Filter. The invariant pass produces ordinary findings with the same
Structured Finding Contract – do not segregate them.

**Inline**: walk each triggered check against the diff, using the project's
search tooling to gather evidence. Required when no sub-agent dispatch is
available.

**Sub-agent dispatch**: when the host supports sub-agents, the invariant pass
may run as its own fresh-context sub-agent in parallel with the primary lens's
Critic pass. Pass this file's path explicitly in the task prompt alongside
`${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` – custom-agent
instructions are not a substitute for the rubric.

When `large-diff-fanout.md` (sibling reference) is in effect, each partition's sub-agent
runs the triggered subset of these checks scoped to its partition; the boundary
pass re-runs checks 1, 2, and 6 across partition boundaries (these are the
checks where the second site can live in a different partition than the first).


## Composition

- **With `--council`**: when a council is active, the invariant pass is the
  Correctness Reviewer's primary surface on refactor-shaped change sets. The
  Cross-Lens Critic in chain mode still attacks lens-boundary surface – the
  invariant pass attacks file-boundary surface within a lens. Both can fire.
- **With `--mode gap`**: the gap lens's existing wiring check (Step 3) is the
  primitive that check 1 (deletion completeness) generalizes. When both fire,
  keep one finding per concrete reference; do not double-count.
- **With Project Rules Context** (Step 3 Guardrails pass): rule citations
  take precedence when a guardrail violation is also an invariant violation –
  emit one finding citing the rule, with the invariant as evidence.
