# Refactor Invariants

Cross-file invariant pass for the `code` and `gap` lenses, loaded when the diff shape fires a trigger below. An invariant no single hunk hosts is what hunk-by-hunk review misses. Findings use the Structured Finding Contract and merge into the primary lens's severity sections, never segregated.


## Trigger Conditions (any one)

- Diff deletes a file, public symbol, exported member, or configuration/schema key
- Diff renames or moves a symbol or file (git rename detection, or grep-detectable rename)
- Diff introduces a cache, memoized value, or "resolve once, consume many" result
- Diff moves a check between lifecycle stages (load-time → runtime, build-time → install-time, sync → async, validator → caller precondition, …)
- Diff generates artifacts that must obey the same rules as authored ones (codegen, synthetic config, scaffolded steps)
- Diff migrates data shape across a schema/storage boundary (frontmatter relocation, column move, file-format change)
- Diff threads a new required parameter through helper signatures


## Invariant Checks

Apply only the checks whose trigger fired. Every finding is backed by project-native search evidence (`rg`, `ast-grep`, IDE find-references, a language LSP), never asserted from memory.

1. **Deletion completeness** – for every deleted symbol, file, or key, prove no reference remains in production code across every package, tests (deleted, not skipped; orphan fixtures cleaned), registration sites (routes, exports, barrels, DI containers, plugin manifests, build configs), documentation (README, architecture docs, CHANGELOG, inline comments, user guides), and downstream skills, CLIs, scripts, or external tooling. A remaining reference compiles and lints clean while dead, misleading, or routed to a removed handler.
2. **Resolve-once, consume-many** – for every cache, memoized result, or resolved value the diff introduces, list every consumer and verify it reads the resolved value rather than re-deriving it. A second derivation site is a finding even when it yields the same value today: it desyncs silently when derivation logic, inputs, or upstream resolution change.
3. **Lifecycle relocation** – when a check (validation, authorization, normalization, …) moves between lifecycle stages: old call sites are removed, not commented or feature-gated; tests exist at the new stage **and would fail against the pre-change code**, exercising the new mechanism rather than the old one under a new name; documentation that promised the old timing is updated and consumers that assumed it are re-anchored.
4. **Generated-artifact obedience** – every synthetic artifact the diff introduces (codegen output, scaffolded steps, synthetic config blocks) passes the validators, precondition checks, and invariants authored artifacts satisfy; a bypass surfaces authoring errors in the generator only at runtime.
5. **Schema / data migration** – when a field moves between schema versions, frontmatter blocks, or storage locations, behavior equivalence is proved by a contract test comparing pre/post resolved behavior, not by reading the code: inlined defaults, fallback chains, and override precedence drift silently.
6. **Parameter threading** – when a new parameter encodes a correctness invariant, every call site provides it. A defaulted or optional parameter whose value is required for correctness is a finding: the default silently re-introduces the bug the parameter was added to prevent and masks the call sites that should have been updated.


## Composition

- **With `--mode gap`**: the gap lens's Integration/wiring failure mode is the primitive check 1 generalizes; when both fire, keep one finding per concrete reference.
- **With Project Rules Context** (the Step 3 Guardrails check): when a guardrail violation is also an invariant violation, emit one finding citing the rule, with the invariant as evidence.
