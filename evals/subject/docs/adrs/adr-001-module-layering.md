# ADR-001: Strictly downward module layering

**Status**: Accepted
**Date**: 2026-03-27

## Context

The exporter started as one module and grew a command line. The first extraction left `records` importing the command line's argument defaults, and a caller who wanted the exporter from another program had to construct an argument namespace to get at it.

## Decision

Modules form three layers, and an import only ever points downward: `cli` → `pipeline` → {`records`, `export`, `retry`, `text_tools`}. The four leaf modules import nothing else from the package. A shared constant that two leaves both need is owned by the layer above them or duplicated, never imported sideways.

## Consequences

- `pipeline.run` is the whole product without the command line, which is what the journey tests and any embedding caller use.
- A leaf module is testable with no setup beyond its own arguments.
- The rule costs a small duplication when two leaves want the same literal. That is the price of the boundary, not an oversight to fix.
