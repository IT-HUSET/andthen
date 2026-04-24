# Composition Playbook

Five archetype recipes for common diagram intents. Each recipe is a **starting layout** – pick one based on the diagram's narrative, then adapt. Reading a recipe is faster than inventing geometry from scratch.

> **Before you start**, commit to a Layout Contract (see `SKILL.md` Phase 1.5): narrative spine, hero, directional axis, shape vocabulary, zone plan, size cascade. The recipes below are keyed to those decisions.

All recipes assume the **Hand-drawn Blueprint** aesthetic, fontFamily 5 (Excalifont), and snap all coordinates to a 20px grid.

---

## Archetype 1 – Pipeline / Workflow

**Use for**: ordered processes, ETL, lifecycles, request/response flows, CI pipelines.

**Narrative**: "Input enters at A, transforms through B, C, D, and exits as E."

**Axis**: Left → right.

**Canvas**: `1400 × 800` (L or XL).

### Layout

```
 ┌────────────────────────────────────────────────────────────────┐
 │   TITLE                                                         │  y=40
 │   subtitle                                                      │  y=80
 │                                                                 │
 │   ╭──── Zone A (sparse, primary color) ─────────────╮           │
 │   │   (  stage 1  ) ──► ( stage 2 ) ──► ( stage 3 ) │           │  y=140
 │   │                                                 │           │
 │   │      │                  │               │       │           │
 │   │      ▼                  ▼               ▼       │           │
 │   │   [secondary]      [evidence artifact]          │           │  y=360
 │   ╰─────────────────────────────────────────────────╯           │
 │                                                                 │
 │   ╭──── Zone B (dense, accent color) ──────────╮                │
 │   │   {detail notes, leaf nodes, 14px labels}   │               │  y=560
 │   ╰─────────────────────────────────────────────╯                │
 └────────────────────────────────────────────────────────────────┘
```

### Recipe

- **Title**: free-floating text, `x: 40, y: 40, fontSize: 30`
- **Subtitle**: `x: 40, y: 82, fontSize: 16, color: #868e96`
- **Zone A** (primary flow): `x: 40, y: 140, width: 1320, height: 400, bg: blue[0], opacity: 50`
- **Stages**: 5 primary ellipses or rectangles, `180 × 90` each, y: 200, x-spacing `260` (80px gap between shapes). Row spans x: 80 → 1280. Primary row ends at y=290.
  - Exactly ONE stage is the hero → upsize to `220 × 110`, shift its y to 190, and shift neighboring x positions by ±20 to preserve the 80px gap
- **Primary flow arrow**: single bold (`strokeWidth: 4`) arrow binding stage 1 through stage 5 — or 4 bold arrows end-to-start-bound between stages
- **Secondary nodes** under stages: `120 × 60`, y: 320 (30px gap below primary row), connected with thin arrows. Ends at y=380.
- **Evidence artifact**: one dark rectangle, `240 × 120`, y: 400, positioned under the most interesting stage. Ends at y=520, inside Zone A (140–540).
- **Zone B** (detail / appendix): `x: 40, y: 580, width: 1320, height: 180, bg: bronze[0], opacity: 50`

### Anti-checks
- Not all stages the same size (must break uniform grid)
- Each stage actually has an arrow to the next (not implied by position)
- Evidence artifact present (this is a technical diagram)

---

## Archetype 2 – Architecture / System Map

**Use for**: service architectures, system boundaries, data-flow diagrams, dependency maps.

**Narrative**: "Clients talk to the API, which delegates to workers and persists to data stores."

**Axis**: Radial (hero center) or left→right with hero-center.

**Canvas**: `1600 × 1100` (XL or XXL).

### Layout (hero-center variant)

```
   ┌─ Client zone (sparse) ─┐     ┌─ Core zone (hero) ─┐     ┌─ Data zone (dense) ─┐
   │                         │     │                     │     │                      │
   │   [Web app]             │     │      ╔═════════╗    │     │   [Postgres]         │
   │   [Mobile]      ──────► │     │      ║   API   ║    │ ──► │   [Redis]            │
   │   [CLI]                 │     │      ║ Gateway ║    │     │   [S3]               │
   │                         │     │      ╚═════════╝    │     │                      │
   │                         │     │      │    │    │    │     │   { evidence:        │
   │                         │     │      ▼    ▼    ▼    │     │     real schema }    │
   │                         │     │   (auth)(rate)(log) │     │                      │
   └─────────────────────────┘     └─────────────────────┘     └──────────────────────┘
```

### Recipe

Asymmetric three-zone layout so the hero gets room to breathe:

- **Client zone** (left, sparse): `x: 40, y: 140, width: 380, height: 800`
- **Core zone** (center, hero): `x: 460, y: 140, width: 680, height: 800` — wide enough for a `320 × 160` hero with 180px breathing room on each side
- **Data zone** (right, dense): `x: 1180, y: 140, width: 380, height: 800`
- Total canvas: 1600 wide with 40px outer padding both sides and 40px inter-zone gaps.
- **Hero**: API gateway at `x: 640, y: 380, width: 320, height: 160` — centered in the core zone. Horizontal breathing room: `(680 − 320)/2 = 180px` on each side inside the zone.
- **Satellites around the hero**: 3 small ellipses (auth / rate-limit / log), `120 × 60`, arranged below the hero at y: 600, with radiating thin arrows from the hero.
- **Client nodes** (left zone): 3 rectangles, `180 × 90`, stacked vertically, each arrow-bound to the hero.
- **Data nodes** (right zone): 3 rectangles with mixed fill styles (`solid` for services, `hachure` for one of the DBs), `180 × 90`.
- **Evidence artifact**: 1 dark rectangle inside the data zone showing the real schema or a sample payload, `280 × 180`.
- **Arrows**: all client→hero arrows are same color (gray). Hero→data arrows are primary-flow bold (`strokeWidth: 4`). Include a **legend** bottom-right if you use colored arrows.

### Anti-checks
- Clear hero (squint test: the gateway still dominates)
- Three zones with three different color families
- Isolation halo: no element within 80px of the hero's bounding box on any side

---

## Archetype 3 – Taxonomy / Map

**Use for**: categorizing things (database types, AI techniques, design patterns), landscapes, "kinds of X."

**Narrative**: "These are the regions of X. Here's what lives in each region and where they overlap."

**Axis**: None (spatial categories, not a flow).

**Canvas**: `1400 × 900` (L).

### Layout (Kleppmann map metaphor)

```
    ╭─────────── Category A (teal) ──────────╮
    │    ItemA1   ItemA2                     │
    │                ItemA3                  │
    │   ┌── overlap ──┐                      │
    │   │  CrossItem1 │                      │
   ╭╰───┘             └─ Category B (violet) ╯╮
   │       ItemB1     ItemB2    ItemB3        │
   │               ItemB4                     │
   ╰───────────────────────────────────┬──────╯
                                       │
    ╭─────── Category C (bronze) ──────┴───╮
    │   ItemC1    ItemC2    ItemC3         │
    ╰──────────────────────────────────────╯
```

### Recipe

- **Zones overlap or abut**. Use rounded rectangles with `opacity: 50`, shade[0] backgrounds.
- **Category name**: free-floating text (no box), `fontSize: 28`, zone stroke color (shade[4]) at full opacity (100). Positioned top-center of each zone. This is the "continent name" – dominant, not boxed. Use the zone color itself for visual recession, not a lowered text opacity.
- **Items inside zones**: free-floating text at `fontSize: 18`. No boxes unless the item is connectable. **This is the key variance** — a taxonomy is NOT a grid of boxes.
- **Overlap items**: place them straddling the zone boundary.
- **No primary-flow arrow.** Relationships, if any, use dotted thin lines.
- **Evidence artifacts**: optional – one per zone showing a canonical example.

### Anti-checks
- Less than 30% of text elements are inside containers (Box-budget rule)
- No explicit arrows pointing from item to item (that would imply process, not categorization)
- Category names are bigger than items (hierarchy preserved)

---

## Archetype 4 – Lifecycle / Loop

**Use for**: feedback loops, iterative processes, retry patterns, state machines.

**Narrative**: "State A leads to B leads to C, and C feeds back to A."

**Axis**: Cyclic (usually clockwise).

**Canvas**: `1000 × 1000` (square).

### Layout

```
           ( State A )
            ▲       ▼
            │       │
         [Action]   [Action]
            ▲       ▼
         ( State D ) ───► ( State B )
            ▲                    ▼
            │                    │
         [Action]              [Action]
            ▲                    ▼
         ( State C ) ◄─── [Action]
```

### Recipe

- 4 states arranged at corners of a square (centers at `(300, 200), (700, 200), (700, 600), (300, 600)`).
- Each state is an **ellipse** (ellipse = state, per shape vocabulary), `180 × 90`, but upsize **one** state that's the entry point to `240 × 120` (the hero).
- Arrows between states curve slightly (3-point `points` array) — not straight lines. The curvature makes the loop visible at a glance.
- Label each arrow with the **action** that triggers the transition (2–3 words), `fontSize: 14`, placed outside the curve.
- Center of canvas reserved for the diagram title and a 1-sentence description – this is the visual anchor of the loop.

### Anti-checks
- Entry-point state is clearly the hero (larger)
- Arrows are curved, not straight
- Actions on arrows are 2-3 words max

---

## Archetype 5 – Comparison / Side-by-Side

**Use for**: before/after, option A vs option B, old vs new, trade-offs.

**Narrative**: "Option A has these properties; Option B has these; they differ in X, Y, Z."

**Axis**: Two parallel vertical columns with a narrow "gap/break."

**Canvas**: `1200 × 800` (L).

### Layout

```
    ┌── Option A (blue) ──────┐  ║  ┌── Option B (bronze) ─────┐
    │  Title A                │  ║  │  Title B                  │
    │  [feature 1]            │  ║  │  [feature 1]              │
    │  [feature 2]            │  ║  │  [feature 2]              │
    │  [evidence A]           │  ║  │  [evidence B]             │
    │                         │  ║  │                           │
    │  ✓ good at X            │  ║  │  ✓ good at Y              │
    │  ✗ weak at Y            │  ║  │  ✗ weak at X              │
    └─────────────────────────┘  ║  └───────────────────────────┘
                                 ↑
                            60–80px gap
                            with vertical guide line
```

### Recipe

- **Two zones** of equal width, `~500 × 700`. Between them: `80px` gap with a thin vertical `#ced4da` line (`strokeWidth: 1`, `strokeStyle: "dotted"`).
- Zone A uses one color family (e.g., Blue). Zone B uses a **contrasting** family (e.g., Bronze – warm vs cool contrast amplifies "these are different").
- Inside each zone, the structure is **identical** (same layout, same shape positions) so the eye can dart across and compare directly. This is the ONE place uniformity helps.
- Trade-off notes at the bottom of each zone: free-floating text with `✓` / `✗` prefixes (or shape markers – no emoji, they don't render).
- No cross-zone arrows.

### Anti-checks
- The two zones use contrasting colors (not two variants of the same color)
- Internal layout within each zone is symmetric to its pair
- Evidence artifacts present (makes the comparison concrete)

---

## Choosing a Recipe

| If the topic is… | Use |
|------------------|-----|
| A sequence of steps | **1 – Pipeline** |
| A system with a clear center of control | **2 – Architecture (hero-center)** |
| A list of kinds / categories / options | **3 – Taxonomy** |
| A self-referential feedback loop | **4 – Lifecycle** |
| Two alternatives to compare | **5 – Comparison** |
| None of these cleanly fit | Combine two (e.g. Pipeline + Comparison = two parallel pipelines) |

**Do not** default to Architecture for everything. Most "architecture diagrams" from AI tools are actually pipelines or taxonomies wearing architecture clothing, and the wrong archetype choice is why they look generic.
