# Setup – Writing the Visual Validation Document

The deliverable is the `Visual Validation` document at its **Project Document Index** location (default `docs/VISUAL-VALIDATION.md`). Later runs capture the way it says, which is what makes a re-validation comparable to the first pass.

## Rules

- Confirm serving, routes, states, and reference locations with the user: a guess made once here is repeated by every run that reads the document.
- Judging stays out of the document – severity, gates, and the report shape are the skill's, in one copy.

## Workflow

### 1. Prove it

Start from what the project already states: the `Key Dev Commands` document's run and test rows, the browser or screenshot tooling the environment provides, the `Wireframes` and `Design System` locations, and any `Visual Validation Workflow` section in the root agent instruction file.

A serve command or capture step that was not run successfully in this session does not go in the document. Serve the app, capture one route at one breakpoint with the tooling in scope, and open the image – a 404, a blank page, or unloaded fonts means the procedure is wrong. What cannot be proved is left out with the reason. An app that cannot be served at all stops setup.

**Gate**: one route at one breakpoint is captured and its image opened without a 404, blank page, or unloaded fonts, or setup has stopped.

### 2. Write it

Create the document with one heading per bullet in Output, dropping a heading this project has nothing for rather than leaving it `TODO`. Where it already exists, rewrite only the sections this run proved and leave the rest byte-identical, so a hand-written note survives a re-run.

A `Visual Validation Workflow` section's content belongs in this document. Remove the section only after the user confirms the document carries it: it is hand-written project policy in a file this skill does not own.

Add the `Visual Validation` Index entry to the root agent instruction file when it is absent, in the shape that Index already uses.

**Gate**: the document carries every proven section, and its Index entry exists.

## Output

The document carries:

- **Serving** – the command that starts the app, the URL it lands on, how to tell it is ready, and any seed data, fixture, or login the screens need.
- **Capture** – the tooling a validator invokes and the command shape that takes a viewport and an output path; captures land in `.agent_temp/validation/` unless this project says otherwise.
- **Routes and states** – the screens worth validating with their paths, plus the non-default states (empty, error, loading, signed-in) and how to reach each.
- **Breakpoints** – the viewport widths this project judges at.
- **References** – where each screen's wireframe, design spec, or baseline lives, and which screens have none.
- **Traps** – what makes a capture lie here: animation, web fonts, non-deterministic data, a scrollbar that shifts layout, a state that needs a reset between shots.

The report is the document path, one line per section naming the command or capture that proved it, and one line per thing left out with its reason.
