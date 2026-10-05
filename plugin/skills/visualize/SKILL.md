---
description: Draw an AndThen artifact as one self-contained HTML page with inline SVG figures, rendered and looked at before it is shown – the architecture or domain model, a context map, an event storm, a plan, or any spec, report, or ADR. Trigger on 'visualize', 'draw the model', 'show the plan as a diagram'. Checking the project's own UI is the andthen:visual-validation skill.
argument-hint: "<artifact path or name> [what the page should bring out]"
---

# Visualize

Draw one AndThen artifact as a self-contained HTML page whose figures are inline SVG, and look at the rendered page before handing it over. The JSON models and boards AndThen writes have no other public reader, so this page is how a user sees what they hold.

## Input

`$ARGUMENTS` names the artifact, as a path or a name the **Project Document Index** resolves, and anything the page should bring out.

## Rules

- **Self-contained.** Inline every style, figure, and script, so the page opens offline from one file. A web font may load, with a fallback stack so the page still reads without it.
- **Figures are static SVG you lay out yourself**, with no diagram library, template, or layout script, because a page whose figures need its script loses all of them to one script error. Script only adds interaction.
- **Draw what the artifact says.** Add no claim it does not make, and show its path and the date or revision it carries, so a reader can tell a stale view.

## Workflow

1. **Read the artifact.** For JSON whose `kind` is `architecture-model`, `domain-model`, `context-map`, or `event-storm`, or a `plan.json`, read [`json-artifacts.md`](references/json-artifacts.md) for the field meanings the names do not carry. **Gate**: each figure the page will carry is chosen, with the fields it draws.

2. **Write the page** as `visualize/<artifact-stem>.html` under the location the `Agent Temp` Index entry names, default `.agent_temp/`. Keep it out of the committed docs, because it is a derived copy that drifts from its source.

3. **Render and look.** Render the page in a headless browser where one is available, otherwise in any browser you can reach, and look at the result. Fix overlapping shapes or labels, clipped text, arrows whose ends or direction cannot be read, and interactions that do nothing, then render again. Read the browser console too, because one script error disables every control on a page that still looks right. **Gate**: a render showing none of these defects, or no browser reached.

## Output

Report the page's path, and its render as checked in the browser you name, or unchecked.
