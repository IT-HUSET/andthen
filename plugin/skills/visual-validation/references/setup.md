# Setup – Writing the Visual Validation Document

Write the project's `Visual Validation` document at its Project Document Index location (default `docs/VISUAL-VALIDATION.md`).

## Rules

- Keep severity, verdict rules, and report format in the skill.

## Workflow

### 1. Establish coverage

Trace the project's user journeys through its routes, requirements, design inventories, and any existing `Visual Validation Workflow`.
Identify the layouts that actually change across supported viewports and content, including non-default states users reach along the way.

**Gate**: every identified journey maps to the views under **Routes and states**, including any with no known capture path.

### 2. Prove the capture paths

Start the UI using `Key Dev Commands` and exercise each distinct way of reaching and capturing a view with the available tooling.
Open a representative shot from each path and identify the intended state at the requested size.
A login redirect, blank page, or unloaded font cannot prove the procedure.

**Gate**: each capture path has an opened example or a recorded gap with its missing prerequisite.
A first setup needs at least one working path to create a guide.

### 3. Write it

Use the applicable headings under Output.
On a rerun update the procedures checked, mark any that failed, and preserve unrelated hand-written sections verbatim.

A `Visual Validation Workflow` section's content belongs in this document. Remove the section only after the user confirms the document carries it: it is hand-written project policy in a file this skill does not own.

A new document gets its Index entry per the Index preamble.

**Gate**: the indexed document accounts for every planned view, including those with unproven paths.

## Output

The document carries:

- **Serving** – the command that starts the app, the URL it lands on, how to tell it is ready, and any seed data, fixture, or login the screens need.
- **Capture** – the proven commands for a viewport and output path, including the first view after an interaction before scrolling or refocusing changes it.
  Captures land in `.agent_temp/validation/` unless this project says otherwise.
- **Routes and states** – for each journey, the screen and state, action or data that reaches it, identifying visible result, applicable viewport, and any capture gap.
- **Breakpoints** – viewport dimensions and the distinct layout or tight fit each exercises.
- **References** – the matching feature's Mockup, wireframe, design spec, or baseline for each view, or which views have none.
- **Traps** – what makes a capture lie here: animation, web fonts, non-deterministic data, a scrollbar that shifts layout, a state that needs a reset between shots.

Report the document path, the commands and opened captures that prove the procedures, and any remaining gaps.
