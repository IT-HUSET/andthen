# Brief Mode

Deltas to the `andthen:clarify` skill's steps under `BRIEF_MODE`; everything the body states and this file does not override still holds. Feature scope only – product scope already writes one document, so the flag is a no-op there.

The subject is whatever needs sharpening: a feature before its PRD, or a decision, a plan, a proposal. The project anchors the body reads (`Product`, `Architecture`, the glossary) bind only where the subject is this product's.

**Step 1** – an `intent.md` at the resolved path is **amended**, touched sections only, rather than folded into a PRD, and a subject that is not a feature has no PRD to fold into: it re-enters with `--brief` or not at all. On such a subject the gap list is the intent doc's own sections rather than the PRD's, and the Vague-Input Bailout infers the narrowest coherent framing where a feature would get the smallest coherent MVP.

**Step 2** – the interview may stop earlier than a PRD's, where the user says the picture is clear enough to share: what is still open becomes the intent doc's Open Questions, not a gap to close here, and the gate takes each one recorded there in place of "no blocking ambiguities". The document is the playback: its edit is the correction. On a subject that is not a feature, the questions are the intent doc's sections and the forks between them.

**Step 3** – write `OUTPUT_DIR/intent.md` from the Intent Document template in intent-template.md: the five sections plus the `Decisions Log` of what the interview settled, with `> **Source**:` populated as the body states. Each Open Question carries the recommendation and alternatives the interview would have put to the user, so whoever reads the document can answer it there; a hand author's bare bullet is still valid. On re-entry an answer written in place is a settled decision to fold, and an untouched recommendation is asked again, never taken as accepted.

**Steps 4–6 do not run** – their checks are PRD-shaped and nothing in an intent doc is settled enough for a reviewer or a Non-Goal; verify only the `Source` line and the body's sharpness test on Open Questions.

**Follow-up** – nothing downstream yet; close on exactly `Edit and share intent.md, then run the andthen:clarify skill on <OUTPUT_DIR>.` A non-feature subject's line closes on exactly `Edit and share intent.md, then run the andthen:clarify skill with --brief on <OUTPUT_DIR>.` instead – that re-entry amends the intent doc.
