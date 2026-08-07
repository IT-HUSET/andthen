# Agent Brief

The handoff payload triage appends to the issue body when an item reaches `ready-for-agent`. A fresh executor (the `andthen:quick-implement`, `andthen:spec`, or `andthen:plan` skill) reads the brief alone – it must carry enough for that executor to start without re-reading the whole thread.

Author it per the **Durability rule** ([`github-publish.md`](${CLAUDE_PLUGIN_ROOT}/references/github-publish.md)): a published body outlives the commit that prompted it, so name behavior and interfaces (types, signatures, commands, endpoints), never file paths, line numbers, or code snapshots. A snippet that itself *is* the settled decision (a schema, a signature) may be inlined, trimmed to the decision-carrying part. Keep it behavioral: what the executor must make true, not how to route the code.

## Template

`edit body` appends the section below to the issue body – delimited by its `## Agent Brief` heading – and replaces it in place on re-triage so it stays idempotent:

```markdown
## Agent Brief

**Current behavior** – what the system does today in the relevant area, stated observably.

**Desired behavior** – what must be true when this is done; the observable change.

**Key interfaces** – the types, signatures, commands, or endpoints the change turns on, named (not located).

**Acceptance criteria** – checkable conditions that prove the desired behavior, one per line.

**Out of scope** – adjacent work this item deliberately does not cover, so the executor does not widen the change.
```

## Worked example

Input item: *"Login lets you submit an empty password and just spins forever."*

```markdown
## Agent Brief

**Current behavior** – The sign-in form submits with an empty password field; the request reaches `AuthService.signIn` with a blank credential and the UI stays in its pending state indefinitely with no error surfaced.

**Desired behavior** – An empty password is rejected before any network call, with an inline field error, and the submit control stays disabled until both fields are non-empty.

**Key interfaces** – `SignInForm` (the form component), `AuthService.signIn(email, password)`, the `ValidationError` type already used by the email field.

**Acceptance criteria**
- Submitting with an empty password shows an inline "Password is required" error and issues no request.
- The submit control is disabled while either field is empty.
- A non-empty password preserves today's sign-in behavior unchanged.

**Out of scope** – Password strength/complexity rules, rate limiting, and the forgotten-password flow.
```
