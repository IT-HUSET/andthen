# Blocking-Decision Interview

Lean interview guidance for driving an implementation-blocking decision to a resolution the executor can act on alone. Scoped tighter than a full requirements interview: the goal is to close *one* decision that would otherwise fork the unattended run, not to re-discover the feature.

## Stance

- **One decision per question.** Each question closes a single `decision_key`. Do not bundle.
- **Recommend, don't decide.** Offer a best-guess answer with a one-line rationale so the user can ratify or redirect. If you have no defensible basis, ask open-ended rather than fabricating one. An unaddressed recommendation is unanswered, not confirmed – wait for input.
- **Settle only sharp, local choices.** Altitude and sharpness are independent. Stakeholder-relevant answers are requirements-altitude and route to the `andthen:clarify` skill. An imprecise implementation choice requires code/architecture investigation; route a genuine architecture fork to the `andthen:architecture` skill, otherwise return the sharpened choice here. Keep the record open through persistence and FIS reconciliation.
- **Decisions interact.** When a question shares an `affected_surface` with a decision already ratified this run, name the interaction in the question and check the new answer against the earlier decision's wording before persisting – two individually sound answers can contradict.
- **Question delivery.** Use an interactive user input tool when available (e.g. `AskUserQuestion` in Claude Code); fall back to numbered markdown otherwise. Lead each question with brief decision context drawn from the record – where it surfaced (`source`), what it affects (`affected_surface`), why an unattended run would fork on it (`evidence`) – so the user can decide informed without re-opening the FIS; keep it scannable (a few tight sentences, never a wall of text). First option = the recommendation with rationale; remaining options = real alternatives, each stating its observable consequence; leave room for free-form input.

## Probing techniques

Apply the matching technique when an answer is vague, over-confident, or solution-shaped. Probe before accepting a load-bearing answer – a confident-sounding answer can still be wrong.

- **Scenario Testing** – when a decision sounds fine in the abstract: what happens in a concrete case? On day one vs. day one hundred? When two conditions are true at once? The fastest way to surface the edge case the executor would otherwise hit.
- **Trade-off Forcing** – when "either is fine" but the choice changes observable behavior: which do you want when they diverge under load / on failure / at scale? Forced scarcity reveals the real preference.
- **Five Whys** – when the user states a mechanism instead of the need behind it: drill from requested mechanism to underlying need, stop once the need is stable. Prevents persisting a decision that solves the wrong problem.
- **Extremes and Boundaries** – when scope around the decision is fuzzy: smallest version that still works? What breaks at 10×? Separates the essential commitment from the ornamental.

## Closing a decision

A blocking decision closes one of four ways:
- **Resolved in place** – the user picks; persist by altitude via the `andthen:ops` skill (atomic FIS affected-surface amendment + decision Note, `DECISIONS.md` Still Current note, or ADR via the `andthen:architecture` skill). The record goes `resolved` only after the final body verifies.
- **Resolved by spike** – when the decision turns on an empirical unknown a discussion cannot settle (which approach is faster, whether an integration is feasible), answer it by building: invoke the `andthen:spike` skill on that one question, then close on its Spike Verdict exactly like *Resolved in place* – same altitude persistence via the `andthen:ops` skill. The spike is throwaway evidence; only the decision persists.
- **Deferred with sign-off** – the user explicitly chooses to punt; persist it in Deferred Decisions. It stops the interview loop but remains an execution hold. A punt without sign-off stays `open`.
- **Resolved through an upstream handoff** – requirements-altitude work returns from the `andthen:clarify` skill; a genuine architecture fork returns from the `andthen:architecture` skill. Re-detect and reconcile the affected FIS surface; the record leaves the blocking set only after that final artifact resolves it. Code/architecture investigation that merely sharpens a local choice returns to the focused interview instead.

Never close a decision by inventing the answer. Under `AUTO_MODE` there is no interview at all – the decision stays `open` and surfaces in the signal.
