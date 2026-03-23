# Verification Patterns Reference

Comprehensive verification patterns for ensuring implementation quality beyond mere existence.

> **Core Principle (Nyquist Rule)**: Every task verification must be an automated command.
> Verification checks 4 dimensions: Exists, Substantive, Wired, Functional.


## The Four Dimensions of Verification

### 1. Exists
File, route, component, or endpoint is present at the expected path.

### 2. Substantive
Real implementation with actual logic – not a placeholder, stub, or TODO.

### 3. Wired
Connected to the rest of the system – imported, routed, called, migrated, rendered.

### 4. Functional
Actually works when invoked – build passes, tests pass, behavior is observable.


## Stub Detection Patterns

Use `rg` (ripgrep) to scan for indicators of incomplete implementation:

### Generic Indicators
```bash
rg "TODO|FIXME|placeholder|not.implemented|lorem ipsum" <path>
```

### Function Stubs
- Empty function bodies: `{}`
- Single return statements: `return null`, `return undefined`, `return 0`, `return ""`
- Python: `pass` as only statement
- Throw-only: `throw new Error("not implemented")`

### React/Component Stubs
- Components returning only `<div/>`, `<></>`, or `<Fragment/>`
- No props consumed (props declared but never read)
- Hardcoded placeholder text with no dynamic content

### API Route Stubs
- Handlers returning hardcoded responses
- No database or service calls
- `res.json({})` or `return new Response("ok")`

### Database Stubs
- Migrations with no columns or empty `up()` bodies
- Models with no fields beyond `id`
- Seeders with no data

### Test Stubs
- `test.skip(...)`, `it.todo(...)`, `xit(...)`, `xdescribe(...)`
- Assertions with hardcoded expected values matching hardcoded actual values
- Tests with no assertions at all
- `expect(true).toBe(true)` or equivalent no-ops

### Configuration Stubs
- `.env.example` values left unchanged in `.env`
- Default placeholder URLs (`http://localhost:3000`, `https://example.com`)
- Default secret keys (`changeme`, `secret`, `xxx`)

### CSS Stubs
- Empty rulesets: `.class {}`
- `/* TODO */` or `/* placeholder */` comments
- Only `display: none` rules


## Wiring Check Patterns

Verify that new code is actually connected to the running system:

### Route Registration
```bash
# Is the route handler registered in the router?
rg "import.*from.*['\"].*routeFile['\"]" src/
rg "app\.(get|post|put|delete|use).*routePath" src/
```

### Component Mounting
```bash
# Is the component imported and rendered somewhere?
rg "import.*ComponentName" src/
rg "<ComponentName" src/
```

### API Endpoint Consumption
```bash
# Is the API endpoint actually called from the frontend?
rg "fetch.*\/api\/endpoint" src/
rg "apiClient.*endpoint" src/
```

### Database Model Usage
```bash
# Is the model referenced in queries or migrations?
rg "ModelName" src/ --type ts
rg "from.*models.*import.*ModelName" src/
```

### Environment Variable Usage
```bash
# Is the env var actually read by the application?
rg "process\.env\.VAR_NAME|env\(.*VAR_NAME\)|Env\.get.*VAR_NAME" src/
```

### Middleware Application
```bash
# Is middleware applied to relevant routes?
rg "use\(.*middlewareName\)" src/
rg "middleware.*middlewareName" src/
```

### Export/Import Completeness
```bash
# Is the export consumed by at least one import?
rg "export.*functionName" src/  # find exports
rg "import.*functionName" src/  # verify imports exist
```


## Quick Verification Commands

### Existence Check
```bash
# Verify files exist at expected paths
ls -la path/to/expected/file
```

### Substance Check
```bash
# Scan for stub indicators in recently changed files
rg "TODO|FIXME|placeholder|not.implemented" <changed-files>

# Check for empty function bodies (JS/TS)
rg "=>\s*\{\s*\}" <changed-files>
rg "function.*\(\).*\{\s*\}" <changed-files>
```

### Wiring Check
```bash
# For each new file, verify it's imported somewhere
rg -l "import.*from.*newFile" src/
```

### Functional Check
```bash
# Build verification
npm run build  # or equivalent
deno task check

# Test verification
npm test
deno test

# Type verification
npx tsc --noEmit
```


## Applying Verification in FIS Tasks

Each task's `Verify:` line should cover all 4 dimensions where applicable:

```
- **Verify**: [Exists] file present at expected path;
  [Substantive] contains real logic (no TODOs/stubs);
  [Wired] imported/registered by parent module;
  [Functional] build/tests pass
```

Not every dimension applies to every task – use judgment:
- A config file might only need Exists + Substantive
- A UI component needs all four dimensions
- A migration needs Exists + Substantive + Functional (runs without error)
