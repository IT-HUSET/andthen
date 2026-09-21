# Design Space Decomposition

Decompose when a flat list of "options" would hide the real trade-offs; for a simple, single-axis choice compare the options directly.

## Key Principle: Dimension Independence

Default to **independent peer dimensions**, not hierarchy.

- **Independent dimensions**: any option from A could in principle combine with any option from B
- **Dependent dimensions**: a parent choice changes what options exist for the child

Handle incompatibilities in cross-consistency notes, not by inventing a tree too early. Only nest when one choice truly determines the available choices below it.

## Cross-Consistency Rubric

Mark important pairs **Compatible**, **Incompatible**, or **Conditional** (works only if some condition is true). This is the pruning step: rule out combinations that do not make sense.

## Floor Option

Every alternative set includes the **floor option** – the smallest option that still satisfies the stated criteria, usually *do nothing* or *extend what already exists* – and the recommendation states what the chosen option buys over it. Weighted-criteria scoring otherwise structurally favors whichever option scores on the most criteria, which is the biggest one. This is the distillation test applied to components: *delete this component – is the outcome now worse?* When the answer needs a scenario nobody has stated, the floor option is the recommendation.

## Output Shapes

Three named shapes; pick the one whose information density matches the decision.

- **Compact List** – default for inline use in specs and intent docs.
- **Morphological Matrix** – when combinations across many dimensions need systematic reasoning.
- **Hierarchical Nesting** – only for genuine dependency.
