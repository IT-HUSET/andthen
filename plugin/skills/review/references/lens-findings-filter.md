# Lens Findings Filter (Shared Wrapper)

This pass cannot find new issues; that is the Critic Lens's job (`${CLAUDE_PLUGIN_ROOT}/references/lens-adversarial.md`).

Run the full Findings Filter only when any finding is Critical OR total findings > 5. Otherwise apply an inline self-check: re-read each finding against calibration examples and adjust severity. Withdrawals follow the same Verdict-discipline floor as the formal filter ([`adversarial-challenge.md`](${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md)) — concrete falsifier required; "doesn't hold up" alone is a downgrade. Add one line: "Applied inline severity calibration (Findings Filter skipped: no Critical findings and <=5 total)."

**Full filter** (when triggered): Use `${CLAUDE_PLUGIN_ROOT}/references/adversarial-challenge.md` (`Generic Findings-Filter Template`) with:
- **Role**: `<ROLE>`
- **Shared calibration**: `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md`
- **Skill calibration**: `<SKILL_CALIBRATION>`
- **Context block**: `<CONTEXT_BLOCK>`
- **Questions**: <QUESTIONS>
- **Verdicts**: `VALIDATED`, `DOWNGRADED`, `WITHDRAWN`
- **Findings payload**: `<FINDINGS_PAYLOAD>`

Apply verdicts before `<VERDICTS_BEFORE_X>`. _(Lens-specific: see call-site for the exact verb — "writing the final report" for doc; "scoring" for gap and security.)_
