# Verification Patterns Reference

Use this when defining or reviewing proof of completion. The point is to prove the outcome, not merely show that a file exists or a build still passes.

## The Four Dimensions of Verification

### 1. Exists
The file, route, component, command, or config is present where it should be.

### 2. Substantive
There is real implementation, not a placeholder, TODO, no-op, or thin stub.

### 3. Wired
The new code is actually connected to the rest of the system.

### 4. Functional
The behavior works when exercised.

Most meaningful `Verify:` lines cover more than one dimension.

## Stub Detection Patterns

Look for evidence that code is present but not real:

- TODOs, placeholders, `not implemented`, lorem ipsum
- empty bodies or trivial returns
- components that render only empty wrappers or placeholder text
- handlers that always return a canned success response
- skipped or empty tests
- config values left at placeholder defaults

Representative scans:

```bash
rg "TODO|FIXME|placeholder|not[_ -]implemented|lorem ipsum" <path>
rg "=>\\s*\\{\\s*\\}" <changed-files>
rg "test\\.skip|it\\.todo|xdescribe|xit" <path>
```

## Wiring Check Patterns

Ask the concrete integration question that matches the change:

- Is the new route registered?
- Is the new component imported and rendered?
- Is the new endpoint actually called by a client?
- Is the new model used in queries or migrations?
- Is the new env var actually read?
- Is the middleware applied where it matters?
- Is the new export consumed anywhere?

Representative scans:

```bash
rg "import.*ComponentName|<ComponentName" src/
rg "app\\.(get|post|put|delete|use).*routePath" src/
rg "process\\.env\\.VAR_NAME|env\\(.*VAR_NAME\\)" src/
```

## Quick Verification Commands

Use commands that prove the specific claim:

### Existence Check
```bash
ls -la path/to/expected/file
```

### Substance Check
```bash
rg "TODO|FIXME|placeholder|not[_ -]implemented" <changed-files>
```

### Wiring Check
```bash
rg -l "import.*from.*newFile|<ComponentName|routePath" src/
```

### Functional Check
```bash
npm run build
npm test
npx tsc --noEmit
```

Replace the commands with the project's actual tooling. Generic green checks are weak if they do not exercise the claimed outcome.

## Applying Verification in FIS Tasks

Good `Verify:` lines are concrete and falsifiable.

Weak:
- `Verify: build passes`
- `Verify: tests pass`
- `Verify: output exists`

Stronger:
- `Verify: traces list output includes columns IN_TOKENS, OUT_TOKENS, CACHE_R, CACHE_W`
- `Verify: dispatch loop calls effectiveConcurrency() from TI01 when maxParallel is set`
- `Verify: integration test fails before the change and passes after resume=true is returned at the harness boundary`

Rule of thumb:
- If the task prescribed a format, field, file path, or behavior, the verification must name it.
- If the task created a new integration point, verification must prove it is wired.
- If the task changes user-visible behavior, verification must exercise that behavior directly.
