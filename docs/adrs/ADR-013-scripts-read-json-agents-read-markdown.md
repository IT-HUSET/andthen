# ADR-013: Scripts read JSON, agents read markdown

**Status:** Superseded on 2026-09-21 by the **Still Current** decision "The `ops` skill and its script are retired" in [Decisions](../DECISIONS.md#still-current) – no script reads or writes `plan.json` any more, so the JSON/markdown split this record draws has nothing left on the script side. What survives it: every FIS, Key Dev Commands, Index, Learnings and Tech Debt document stays agent-read and agent-edited, and completion stays bound to a proof line the executing context saw. Previously amended by [ADR-014](ADR-014-story-runs-where-invoked.md) on 2026-09-13 and [ADR-015](ADR-015-two-entries-to-the-spec-driven-path.md) on 2026-09-14.

**Recorded:** 2026-09-11

**Supersedes:** [ADR-012](ADR-012-size-notice-only.md). **Amends:** [ADR-003](ADR-003-runtime-state.md), [ADR-011](ADR-011-per-story-code-review.md).

## Context

`ops.py` grew a second reader for every markdown document an agent already reads. `complete-story` located `AGENTS.md`, parsed the Project Document Index table for the Key Dev Commands row, opened that file, regexed its Testing table for the `fast` and `run one test` rows, then regexed the FIS for task ids, scenario labels, `SATISFIES` lists and Proof/Verify targets in three grammars, ran them, and wrote a JSON receipt under `.agent_temp/receipts/`. `validate-plan` dry-ran the same rows; `close-plan` cross-checked receipts against the FIS; `update-fis`, `update-learnings` and `update-tech-debt` edited markdown sections by regex; the size notice parsed the Index again for a Ceiling cell. A standalone FIS carried its state in a schema of its own, `<fis-stem>.state.json`, so every verb had two branches.

Each parser pinned a document's shape: the Index could not stop being a table, the Testing table could not be a list, a FIS bullet could not gain a word before its id. The exec-spec coordinator was already reading the diff and running the proofs itself (ADR-011), so the script ran them a second time. The founding incident behind proof-bound completion (a 0.x story done with 237 boxes checked and no probe executed) was a story whose author certified its own work with nobody instructed to run anything; it was never a case for a script parsing prose.

## Decision

`ops.py` reads and writes `plan.json`, runs git, and checks that a named file exists. It parses no markdown for meaning. The FIS, the Key Dev Commands document, the Project Document Index, Learnings and Tech Debt are agent-read documents, and agents edit them with their editor.

**Verification.** `exec-spec` runs the tier – full by default, fast under `--no-full-tier` – and every `Proof` and `Verify` itself (commands as written, test targets through the run-one-test row, inspection targets by reading the file), keeps one line per proof id – what ran and its exit code, or what it saw – and calls `complete-story <plan.json> <story-id> --verified "<one line>"` quoting one of those lines. The verb requires an executable status and done dependencies, writes `verified: {at, summary}` into the story record, and sets `done`. No receipt files.

**One state shape.** Every FIS is a plan story. `andthen:spec` for a standalone feature writes a one-story `plan.json` beside the FIS; the sidecar and `fis-state.schema.json` retire. `complete-task` becomes `complete-task <plan.json> <story-id> <task-id>`.

**Retired verbs.** `update-fis` (agents append to Implementation Observations directly, per `fis-mutability.md`), `update-learnings` and `update-tech-debt` (agents append one bullet under the fitting heading after reading the document; the admission test stays in the document's own header note), `parse-artifact` and its fixture corpus. `validate-plan` keeps the schema and plan-internal cross-field checks plus FIS-pointer existence; the proof dry run, task-id reconciliation against the FIS and provenance parsing go. `close-plan` deletes the bundle and reports; routing Drift Notes and cited ADRs is the caller's read before the call. `read-state` and `progress` project `plan.json` only.

## Rationale

Independence comes from who verifies, not from what language runs the command. The proof lines are tool results the executing context saw, the same trust every subagent report carries, and the change's independent read is the per-story reviewer ([ADR-014](ADR-014-story-runs-where-invoked.md)). The script's contribution was a second execution and a parser for each document it needed, and the parser's cost was paid on every edit of those documents.

Runnable Proof Forms remain authoring guidance in `fis-authoring-guidelines.md`: a proof nothing can run is still what lets unwired code complete green, and `exec-spec` is its reader. What changes is that a grammar violation is a finding, not a parse error.

Rejected: a verb that runs a command list the verifier hands it. It keeps exit codes machine-recorded, but adds a JSON contract for a fabrication risk the verifier's own tool results already cover. Rejected: the coordinator runs the proofs itself with no verifier, which is leanest but accumulates every story's test output in one exec-plan session. Rejected: runtime state in the FIS, which puts either the author's checkbox or a script's markdown edit back in the loop.

## Consequences

`ops.py` loses the FIS scanner, the proof runner, receipts, Key Dev Commands and Index resolution, the size notice, the sidecar path, four verbs and their tests; the artifact fixture corpus goes with `parse-artifact`. A spec directory holds two files. The Index and the Testing table are free to take whatever shape reads best. A misreported proof line is caught by the per-story review and the completion report, not by a script.

Reopens on a story reaching `done` with a proof `exec-spec` did not run.

## Evidence

- History: `8c1d584` (2026-09-11) retires the context-budget gate, the other Index parser; `fc5c039` and ADR-011 retire the story gate around the proof runner; `322b23d` and ADR-012 cut the durable-document checks to the notice this record removes.
- Analysis: this session's trace of `resolve_tiers` → `index_document` → `index_rows` → `read_tiers`, and of `scan_fis` callers across nine verbs; `docs/temp/research/1.0-audit/00-SYNTHESIS.md` D8 – local, not committed.

## Amendments

- 2026-09-13 – [ADR-014](ADR-014-story-runs-where-invoked.md). The verifier subagent retires, so Verification now reads as `exec-spec` running the tier and every proof itself and quoting one of its own proof lines into `complete-story --verified`; the Rationale's independence sentence names those lines as the executing context's own tool results and the per-story reviewer as the change's independent read; `exec-spec` replaces the verifier as the reader of Runnable Proof Forms; and Consequences attributes a misreported proof line to the per-story review and names `exec-spec` in the Reopens clause. ADR-014 adopts the option the Rationale rejected – the executing context runs the proofs with no verifier – because each story now runs in its own context.
- 2026-09-14 – [ADR-015](ADR-015-two-entries-to-the-spec-driven-path.md). The one-story `plan.json` a single feature gets is written by `spec` on the quick track, or by `plan` from a PRD source when the feature comes in as one story; "One state shape" holds for both.
