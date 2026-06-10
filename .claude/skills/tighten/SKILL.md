---
description: Tighten AndThen skill/reference/prompt content – remove redundant restatement, fix wrong-altitude prose, and integrate accreted edits, with zero contract loss. Project-local (not shipped in the plugin). Trigger on 'tighten this skill', 'compress this prompt', 'reduce skill bloat', 'dedup these references', 'rework don't accrete pass'.
argument-hint: "[--auto] [--path <dir/file>] [scope/description]"
---

# Tighten Skill & Prompt Content

Make AndThen skill/reference/prompt content more compact and cohesive without losing any contract. This is the prompt-domain sibling of the `andthen:simplify-code` skill: same scope discipline and Intent anchor, but the lenses target *prose* failure modes and the safety net is **not tests** – prompt content has no test that proves behavior is preserved, so the gate is measurement + install-bundle reachability + a fresh-context contract-preservation review.

Why this exists: the project's own rules forbid accretion ("Rework, don't accrete"; "Repetition is dilution"), yet they are always-on background context during feature work and easy to rationalize past one local edit at a time. The cost only shows up in aggregate. This skill is the forcing function that measures the aggregate with fresh eyes after the work is done.


## VARIABLES

ARGUMENTS: $ARGUMENTS (strip flag tokens like `--auto` or `--path` before interpreting the remainder as scope/description)

### Optional Flags
- `--auto` → AUTO_MODE: automation-safe execution with no conversational prompts


## INSTRUCTIONS

- Read project rules first: `CLAUDE.md` § "Skill, Prompt and Intent Engineering Rules" and § "Maintenance Contracts", `docs/SKILL-AUTHORING-GUIDELINES.md`, `docs/prompt-guidelines/PROMPT-ENGINEERING-GUIDELINES.md`. These are the rubric – the lenses below operationalize them.
- **Measure by characters/tokens, never lines.** Line counts lie – a reflow changes lines without changing size.
- **Zero contract loss is the hard constraint.** "Contract" = any observable behavior an agent depends on: a deterministic-ops grammar, a cross-skill integration rule, a named failure mode, a REQUIREMENTS-SPEC ID's assertion. Compactness that drops a contract is a regression, not a win. When unsure whether a span is load-bearing, keep it.
- **Net non-increase, except correctness fixes.** A tightening pass should shrink a file or hold it flat. The one sanctioned growth is a *correctness annotation* (clarifying a now-misleading instruction, e.g. a vestigial call under a design pivot) – flag those explicitly so the size delta is honest.
- **Reachability is the prompt-domain "it compiles".** Shared references inline per-skill at install time (`scripts/install-skills.sh` `_skill_assets_<name>` arrays). A pointer "see `X.md`" resolves in an installed bundle **only if X co-installs with every skill that consumes the pointing file**. Collapsing a duplicate into a pointer to an unreachable canonical *is* contract loss – it just doesn't show until install.
- **Behavior-preserving is not intent-preserving.** A tightening that changes *what a REQUIREMENTS-SPEC ID asserts* is a spec change, not a tighten – surface it, do not apply it silently.
- **Apply from one coordinator.** Analysis fans out; edits land from a single agent that holds the whole picture. Cross-file dedup needs one view of what moved where – parallel writers re-expand each other's canonicals or introduce contradictions.
- **Automation mode** (`--auto`): never ask what to do next; apply only the conservative, unambiguous cuts (drop anything the fresh-review or reachability check flags); emit the deterministic block in Phase 4. `BLOCKED:` only when no scope resolves or the base is unavailable.


## GOTCHAS
- **Collapsing a duplicate into an unreachable pointer** – a cross-skill `SKILL.md` is never reachable from another skill's bundle; only shared references and same-file sections are (see Reachability).
- **Deleting a named GOTCHA that names a distinct failure mode** – GOTCHAs earn their tokens by naming traps. Only cut one that merely restates a grammar the operation section already enforces.
- **Re-expanding an established canonical** – when a prior pass made file A the single home for a fact and pointed B/C at it, "tightening" B by inlining the fact back is accretion in disguise.
- **Trusting a sub-agent's "behavior-preserving" claim** – it has no test to back it. The Phase 4 fresh-context review is the check.
- **Tightening the regression baseline into terseness that loses a clause** – `REQUIREMENTS-SPEC` IDs are checked clause-by-clause; splitting an overloaded ID is good, dropping one of its assertions is not.


## WORKFLOW

### Phase 1: Scope, Baseline & Rules

1. **Scope** (precedence): `--path` > described files > current-branch diff vs its base (fall back to `git diff main`) > files edited earlier in this conversation. Treat as authoritative; never widen. Default base for deltas is `main` unless the branch tracks another base.
2. **Size baseline**: record `wc -c` per in-scope file now and at base (`git show <base>:<file> | wc -c`; new files = 0). This is the before/after ledger Phase 4 reports against.
3. **Reachability baseline**: for any shared reference in scope, note its consumer set from `scripts/install-skills.sh` `_skill_assets_<name>` arrays – needed to validate pointer cuts.
4. **Rules + Intent Context**: collect both bundles per [`intent-and-rules-context.md`](plugin/references/intent-and-rules-context.md). The governing "intent" for shipped content is the observable contract in `docs/REQUIREMENTS-SPEC.md` plus the skill-authoring rules. Record `Intent Context: none discoverable` only when truly none applies.

**Gate**: Scope fixed, size + reachability baselines captured, rules/intent bundles collected.


### Phase 2: Analyze (prompt lenses)

Fan out **read-only** analysis – one sub-agent per file or cohesive cluster for non-trivial scope; inline for a single small file. Each returns proposed `old → new` (or DELETE) spans with a char delta and a one-line **contract-preservation note** naming where the contract still lives (and, for pointer cuts, that the canonical is reachable per Phase 1.3). Apply these lenses:

- **Redundant restatement** – the same contract stated 2+ times across co-installed content. Collapse to one canonical + pointer. The worst offenders are facts restated 4–7× across a feature's files, already drifting in wording.
- **Wrong altitude** – step-by-step prescription, if-then chains, or exhaustive enumeration a frontier model would do unprompted. Replace with the principle + its *why*. (Keep counter-intuitive contracts and named failure modes specific – those are the right altitude.)
- **Agent audience** – human-oriented narration, motivational filler, over-explanation. Skills are read by agents; cut what an agent infers.
- **Accretion seams** – sentences bolted onto existing sections leaving doubled altitude or a contradiction with surrounding text. Rework so the section reads as one coherent statement ("Rework, don't accrete").
- **Stale/version phrasing** – historical-change notes ("previously X, now Y", "as of 0.X"), format-version qualifiers (`v1`/`v2`) in shipped content. Describe the current shape only; history belongs in CHANGELOG/ADRs.

**DON'T-CUT calibration** (keep; these earn their tokens): operational contracts and process outlines in `SKILL.md` openings; cross-skill integration contracts; deterministic grammars, exact tokens, and key-order rules; distinct named GOTCHAs; established canonical homes; TOCs on references over ~100 lines. When a sub-agent is unsure, it returns the span as DON'T-CUT, not as a cut.

**Intent anchor**: drop any proposed cut that would change what a REQUIREMENTS-SPEC ID asserts or contradict a stated contract – surface it as `SURFACED: contract change, not a tighten` for the user to decide. Phase 2 only *demotes*; it never promotes a risky cut.

Produce one prioritized, deduplicated edit list.

**Gate**: Edit list assembled; each item carries a char delta + reachable contract-preservation note.


### Phase 3: Apply (one coordinator)

**Convergence exit**: if Phase 2 found no reachable zero-loss cut, the content is already tight – report convergence, skip the edit cycle, run only the Phase 4 size-ledger no-op confirmation, and stop. A clean no-op is a valid, honest outcome, not a failure; do not invent marginal cuts to look productive.

Apply the edit list surgically, smallest coherent change per span. Do not batch unrelated rewrites into one edit. Track, per file, the running char delta and flag any net *growth* with its correctness-fix justification (the only sanctioned growth).

**Gate**: Edits applied; per-file char deltas recorded.


### Phase 4: Verify (the no-tests safety net)

The substitute for "tests pass", in order:

1. **Size ledger** – per-file and total `wc -c` delta vs base. Net non-increase except flagged correctness fixes; report the numbers, do not assert "smaller".
2. **Reachability / install integrity** – every pointer target still exists and co-installs with all consumers of the pointing file. When in doubt, run `bash scripts/install-skills.sh` (and `--claude-user`) and confirm references inline and paths rewrite.
3. **Wording audit** – `rg 'andthen:[a-z-]+' CLAUDE.md plugin/ docs/`: no new skill-as-agent drift; every `andthen:<name>` prose reference keeps an adjacent type noun.
4. **Contract baseline** – REQUIREMENTS-SPEC IDs referenced by changed skills still hold; no ID silently lost an assertion.
5. **Fresh-context contract-preservation review** – invoke the `andthen:quick-review` skill (or dispatch a `review-critic` sub-agent) on the diff, scoped to *zero contract loss and no contradiction introduced*. This is the core gate – the agent that proposed/applied the cuts cannot clear its own work. Treat any surviving HIGH/CRITICAL as a revert-or-fix. **N/A on a no-op**: if Phase 3 applied no edits, there is no cut to clear – the size ledger is the proof, skip this gate. **No dispatch available**: when the host can't spawn a fresh-context sub-agent, fall back to a deliberate independent re-read against the contract-preservation and reachability checklists, and say so in the report (a same-context re-read is weaker than a fresh one – note the reduced assurance).

**If a check fails**: fix or revert the offending span and re-verify. One pass; do not loop.

In `--auto`, emit a deterministic block:
- `STATUS:` `OK` | `BLOCKED: <reason>`
- `FILES_CHANGED:` newline-separated repo-relative paths (empty if none)
- `SIZE:` `before <N> → after <M> chars (Δ <±K>)` total, plus per-file lines
- `VERIFY:` one line per check (`reachability: ok`, `wording-audit: clean`, `fresh-review: 0 contract findings`, …)
- `SURFACED:` newline-separated contract-change items Phase 2 demoted (empty if none)

**Gate**: Size ledger reported, reachability + wording + contract checks pass, fresh review clean (or surviving findings fixed/reverted).


## OUTPUT

- Per-file and total char delta vs base (the honest size ledger).
- What was deduplicated and where each fact's single canonical now lives.
- `SURFACED:` contract-change items left for the user (never auto-applied).
- Verification results (reachability, wording audit, contract baseline, fresh-context review).
