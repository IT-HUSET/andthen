# Changeset Walkthrough Template

Headings and table/fence shapes are the contract the `andthen:visualize` skill's changeset renderer parses. Follow this template exactly.

````markdown
# Changeset Walkthrough: <title>

> TL;DR: <2–4 sentences: what this changeset does and why, in plain language.>

## At a Glance

- **Source**: PR #<N> (`<head>` → `<base>`) | branch `<head>` vs `<base>` | working tree
- **Commits**: <N> · **Files**: <N> · **Lines**: +<adds> −<dels>
- **Intent**: <one line, from PR body / FIS / commits – or "derived from code (no stated intent found)">
- **Risk profile**: <low|medium|high> – <one-line why>

## Change Map

| File | Kind | Δ | Cluster | Risk | Role |
|---|---|---|---|---|---|
| `src/http/client.ts` | modified | +84 −32 | C1 | attention | Retry policy extracted; public signature unchanged |

## Change Narrative

### C1: <cluster title> – behavior

<Why this change exists and what it does – the prose a good PR description never has room for.>

#### `src/http/client.ts`

<One paragraph: this file's part in the cluster.>

```diff
@@ src/http/client.ts:42 @@
 context line
-removed line
+added line
```

> <Optional margin note attached to the hunk above – a non-obvious why, a subtle interaction.>

## Architectural Delta

<Omit this whole section when no component boundary changed.>
<Prose: which relationships changed and why it matters.>

```mapviz
[HttpClient] "src/http" hot
[RetryPolicy] "src/http/retry · new" hot
[OrdersSvc] "consumer"
OrdersSvc -> HttpClient : "unchanged"
HttpClient -> RetryPolicy : "new · extracted"
```

## Reviewer Focus Points

1. **<title>** – <why this deserves careful eyes> (`path:line`)

## Out of Scope

- <Deliberate non-goal of this changeset>
- <Pre-existing issue noticed but untouched – flagged, not fixed>

## Verification

- [x] <test/check that was run or added – with the command when known>
- [ ] <verification still pending or recommended>
````

Template notes:
- Diff fences open with an `@@ <path>:<startline> @@` line so the renderer can label hunks; mark changed `mapviz` nodes `hot` and label new/removed edges in the edge text.
- `attention`/`medium`/`safe` and the five cluster kinds are closed vocabularies – the renderer color-codes on them.
- One H4 per file inside its cluster; `safe`-risk files may share a single H4-less summary paragraph instead of individual hunks.
- Cap embedded hunks at what comprehension needs (typically ≤3 per file, trimmed). An oversized walkthrough recreates the wall-of-diff problem it exists to solve.
