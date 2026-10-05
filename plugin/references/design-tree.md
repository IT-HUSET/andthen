# Design Space Decomposition

Decompose when a flat list of options would hide the real trade-offs. For a simple, single-axis choice, compare the options directly.

## Key Principle: Dimension Independence

Default to **independent peer dimensions**, not hierarchy.

- **Independent dimensions**: any option from A could in principle combine with any option from B.
- **Dependent dimensions**: a parent choice changes what options exist for the child.

Nest only when one choice truly determines the choices available below it. Handle every other incompatibility in cross-consistency notes.

## Cross-Consistency Rubric

Mark important pairs **Compatible**, **Incompatible**, or **Conditional** (works only if some condition is true). This is the pruning step: rule out combinations that do not make sense.

## Floor Option

Every alternative set includes the **floor option**: the smallest option that still satisfies the stated criteria, usually *do nothing* or *extend what already exists*. The recommendation states what the chosen option buys over it.

Without a floor, weighted-criteria scoring favors whichever option scores on the most criteria, which is the biggest one. The floor applies the distillation test to components: *delete this component – is the outcome now worse?* When the answer needs a scenario nobody has stated, the floor option is the recommendation.

## Output Shapes

Pick the shape whose information density matches the decision.

- **Compact List** – default for inline use in specs and intent docs.
- **Morphological Matrix** – when combinations across many dimensions need systematic reasoning.
- **Hierarchical Nesting** – only for genuine dependency.
