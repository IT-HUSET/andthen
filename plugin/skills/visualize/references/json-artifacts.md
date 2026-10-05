# JSON Artifact Fields

What the five JSON artifacts mean where their field names do not say. The four models and boards each carry a `kind` and a `meta` with the project, the producing skill, a date, and the source `revision`. A revision ending `-dirty` describes uncommitted changes.

## `architecture-model` and `domain-model`

Written by the `andthen:describe` skill; `kind` tells them apart. `contexts` are clusters, and each node's `contextId` places it in one.

- `evidence`, on contexts and edges, says where the claim came from: `imports` and `git-coupling` were measured by a tool (co-change is the weaker signal), `declared` is stated in project documentation, and `inferred` is the producing agent's judgment. Draw measured and judged claims so a reader can tell them apart.
- Architecture node kinds `service`, `entrypoint`, `store`, and `external` are the system's runtime shape: a service runs as its own process, an entrypoint is where a process starts, a store is a datastore read or written at runtime, and an external is a system outside the repository the code talks to.
- Edge `weight` is relative strength, `1` when absent.
- `tours` are ordered walkthroughs. Each step targets one node or one context, with a note on why the stop matters. Draw a tour as a sequence a reader steps through.
- `ref` is a repository path. Show it as text, because a link from the page would not resolve.
- In a `domain-model`, a node is a glossary term of kind `entity`, `action`, `state`, or `policy`, `avoid` lists its synonyms to avoid, and `edges` is always empty. A term with `meanings` is overloaded: it belongs between the contexts its meanings name, not inside one.

## `context-map`

Written by the `andthen:architecture` skill in strategic-design mode. `meta.status` `current` and `target` are a run's report-side maps, and `registered` is the accepted map the project records. A relationship's `pattern` is a DDD context-mapping pattern, and `direction: upstream-downstream` puts `from` upstream of `to`. `subdomainType` is `core`, `supporting`, or `generic`.

## `event-storm`

Written by the `andthen:architecture` skill in event-storming mode. Each sticky sits in its `lane` at column `order` of one timeline all lanes share, with the sticky colours of event storming. A `pivotal` event's column divides every lane, and a `hotspot` hangs on the sticky it is `attachedTo`. `candidates` are the subdomains, workflow boundaries, or aggregates the session found, each grouping its `members`. `meta.level` bounds which sticky kinds appear.

## `plan`

Authored by the `andthen:plan` skill and updated as stories execute. `dependsOn` makes the stories a dependency graph. `status` is `pending`, `in-progress`, `done`, or `skipped`, and a `skipped` story blocks its dependents. A `done` story's `verified.summary` is the proof line its run recorded. `fis` names the story's spec file beside the plan.
