# Review Calibration Reference

Universal calibration for all review skills. Load it before assigning severity, then load the domain-specific calibration for the review type. Checklists say *what* to look for. This file says *how rigorously*, because models trend toward leniency: identifying real issues, then rationalizing them away.

## Anti-Leniency Protocol

1. **If you identified a problem, it is a problem.** Record it at the severity it deserves rather than talking yourself into "isn't a big deal" or "probably works fine". Accurate identification is the job, and the remediation plan can deprioritize. The most dangerous failure is identifying real issues, then approving anyway: a payment-integrity gap or a bypassable webhook signature is CRITICAL, not MEDIUM, and the verdict is FAIL.
2. **"Works on the happy path" is not a pass.** Verify edge cases, error paths, boundary conditions, and integration points, in code and documents alike. A feature that only works in the simplest scenario is incomplete, and so is a spec that only covers it.
3. **Substance over surface.** Check that things are actually complete, not just present. A stub that compiles is still a stub. A requirement that says "handle errors appropriately" is still vague.
4. **Apply the peer-review standard.** If you would flag this in a review for a team you respect, flag it here. Do not lower your standards because this is an automated review.
5. **Probe deeply, not broadly.** Verify the artifact fulfills its purpose – implementations work end-to-end, specifications are implementable, requirements are testable – rather than that each item has a corresponding artifact.
6. **No hedging language.** Don't soften findings with "could be an issue", "might cause problems", or "probably fine". State the condition that fails and the impact if it does. Hedging is the verbal form of the leniency bias: it lets the reviewer mark a problem as a non-problem without writing down a falsifier.
7. **Disclaimer-as-finding inside changed files.** "Did not touch pre-existing X" or "out of scope", applied to an issue sitting *inside the files modified by the change set under review*, is itself a finding, not a disclaimer: flag it. Issues in unchanged files remain out of scope. Default to MEDIUM unless the lens reference sets a different severity.
8. **Severity is per-finding, not cumulative.** A group of five LOW issues is five LOW findings, not one HIGH. Never escalate a finding because many others sit near it. Aggregate volume informs the overall readiness verdict, never an individual finding's severity. Domain calibrations may define narrow aggregation exceptions for mechanical conformance classes, where findings merge and severity still never escalates.

## Scope Discipline

Proportionality is never permission to go easy on a defect. **Analysis Paralysis** is the failure mode, and it has a shape: effort scaling with the codebase instead of with the change, a finding re-derived to a certainty its severity does not justify, a report that lists without concluding.

**Finding Distillation** – the distillation test, applied to a finding: *delete it; does the reader now do something different, and worse?* No means it is a `Note`, or it is nothing. **CRITICAL and HIGH are exempt**, because severity that high is always worth the reader's attention. Below it, a second pass to confirm a MEDIUM costs more than the MEDIUM.

**Verdict first** – the top-level judgment leads the report, and leads your own order of work. A review that produced no verdict-level judgment has not reviewed yet, however many findings it holds. One architectural finding outranks ten style nits and must not be buried under them.

## Structured Finding Contract

Field names and value spaces are load-bearing across every review lens: a filter pass compares findings by them, a remediation agent reads the report by them, and downstream tooling parses a written report by them. Never rename a field or widen a value space.

The `andthen:architecture` skill's findings use this contract as its `review-output` reference extends it: `INFO` added to `severity`, three architecture fields added, `Class:` and `Routing:` not applicable.

Every finding carries:

- `reviewer`
- `severity`: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- `confidence`: `0`, `25`, `50`, `75`, or `100`
- `location`
- `scope_relation`: `primary`, `secondary`, or `pre_existing`
- `finding`
- `threatened_assumption_or_invariant`
- `evidence`
- `impact`
- `suggested_fix`
- `verification_needed`

A finding that does not name the behavior, its location, the cause, the impact, and how to verify is not actionable.

Reports render the same fields as prose labels (`Threatened assumption or invariant`, `Scope relation`), or in the finding's heading where a report template puts one there (`severity`). A snake_case name and its prose label name one field, not two.

Findings that survive the Findings Filter (below) additionally carry:

- `Class:` – exactly one of:
  - `code-defect`: the artifact is wrong relative to Intent/requirements and the correction is clear.
  - `spec-stale`: requirements trail the implementation or decision now in force.
  - `design-changed`: a coherent design pivot that needs explicit reconciliation.
  - `ambiguous-intent`: a missing decision prevents knowing whether code or spec is wrong. Reserve it: an unattended executor stops on this class, so it must mark a decision the artifact genuinely lacks, not one the Intent or Expected Outcomes resolve.
- `Routing:` – `Fix` or `Note`, with a one-line rationale. `Fix` only when every condition of the **Fix bar** holds:
  - confidence ≥75;
  - scope relation is `primary`;
  - class is `code-defect`;
  - the fix is mechanical, bounded, and uniquely determined, and does not expand past Intent;
  - a security fix is mechanically secure, not merely plausible.

  Everything else is `Note`: surfaced, never applied on this tag's authority, even under `--fix`. Ties default to `Note`.

This section owns the field set, its value spaces, the class meanings, and the Fix bar.

## Findings Filter

A second pass over findings already collected. It validates, downgrades, or withdraws them and never adds one: new issues belong to the caller's Critic pass. The caller supplies the role, the review scope, the calibrations to load, and the per-finding questions. The verdicts are `VALIDATED`, `DOWNGRADED`, and `WITHDRAWN`.

**Withdrawal floor.** `WITHDRAWN` requires a concrete falsifier of one of three shapes:

- an **observed mitigation in the artifact under review** – a guard, escape, or check that demonstrably handles the path the finding names, or for docs, text that already covers what it flagged as missing;
- an **explicit upstream citation** – the requirements baseline (for a gap review the mandatory source, never the implementation under review), an authoritative external source, or an established project convention, cited rather than inferred from silence;
- a **calibration example the finding clearly matches** and that classifies it the same way.

"Low impact" or "probably fine" is `DOWNGRADED`. The floor binds every variant, and every inline self-check that withdraws a finding in place of the full pass. Without it the filter becomes where real findings get talked away, which is the failure the Anti-Leniency Protocol above is calibrated against.

Return one record per finding – `original_reviewer`, `original_location`, `verdict`, `final_severity`, `confidence`, `reason`, `required_change` – and close with `Filter summary: N validated, N downgraded, N withdrawn`. The counted line is what makes the pass auditable rather than assertable.
