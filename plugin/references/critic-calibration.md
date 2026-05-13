# Critic Calibration

Counter-calibration for the Critic sub-lens. Apply on its own, or alongside `${CLAUDE_PLUGIN_ROOT}/references/review-calibration.md` and any lens-specific calibration when those are loaded – it does not replace them.

> **Core principle**: Favor false positives over false negatives. The author is epistemically compromised: your job is to attack their assumptions, not validate their work.

This principle applies only while finding weaknesses. The later Findings Filter optimizes in the opposite direction by pruning weak, duplicate, or unsupported findings.


## Contrastive Examples

### Weak: vague concern

> The retry behavior may have issues.

Why this is weak: no path, state, location, or impact. The Findings Filter cannot validate it, and the implementer cannot fix it.

### Strong: inspectable Critic finding

> `syncOrders()` retries failed webhook delivery but reuses the same idempotency key for every order in the batch. If the first delivery times out and the second order retries, the downstream service can treat it as a duplicate of the first order. Location: `orders/sync.ts:88`. Impact: silent order loss under timeout/retry.

Why this is strong: it names the path, the assumption, the trigger, and the observable impact.

### Weak: filtered too early

> The spec does not define offline behavior, but this is probably fine for v1.

Why this is weak: the reviewer found a requirements gap and then pruned it during the finding pass. The Critic's job is to surface the gap; proportionality belongs in severity calibration and the Findings Filter.

### Strong: Critic surfaces the gap without overclaiming

> The PRD requires "real-time status updates" but does not define what happens when the client disconnects or reconnects. An implementer must guess whether missed updates are replayed, polled, or ignored. Location: `prd.md` "Status Updates". Impact: incompatible client/server behavior can be built from the same requirement.

Why this is strong: it attacks the hidden assumption without inflating the severity beyond what later calibration supports.
