# Ledger Forms

Per-form actions for every `update-ledger` form. Usage grammars and Common rules are the skill's *Update Reconciliation Ledger* section; "GOTCHAS" is the skill's GOTCHAS section; [`reconciliation-ledger.md`](${CLAUDE_PLUGIN_ROOT}/references/reconciliation-ledger.md) is the shared canonical reference.

Actions for `add` form:
- **File-creation exception** (see GOTCHAS): if the passed ledger file does not exist, scaffold it from the canonical ledger template in `reconciliation-ledger.md` before appending.
- Append a new entry with `Status: OPEN`, the given `Class:`, `Stale targets:`, `Source run:`, `Recurrence: 1`, `Falsifier: –`, `Override reason: –`, and `Created:`/`Updated:` set to today.
- **Idempotent**: no-op only if a non-terminal (OPEN / RECONCILE REQUIRED) entry already matches the full stable ID. If another non-terminal entry shares `{relative-path}:{class}` but has a different slug, append the new entry.
- **Terminal-match re-open**: when the stable ID matches a terminal (`CLOSED`/`WITHDRAWN`) entry, re-open it in place rather than appending – mechanics owned by `reconciliation-ledger.md` *Status lifecycle and transitions / add*. Requires refuting evidence in the call (the `[notes]` argument); reject (no-op + `BLOCKED: re-open requires refuting evidence`) when none is supplied.
- Reject (no-op + `BLOCKED: invalid ledger class "<value>"`) on an out-of-vocabulary class.

Actions for `reconcile` form:
- Require an existing matching entry in `OPEN` or `RECONCILE REQUIRED`. For `RECONCILE REQUIRED`, require non-empty evidence that the sanctioned `update-fis design-change` amendment and ADR path completed; reject a bare `update-ledger reconcile <ledger-path> <stable-id>` with `BLOCKED: reconcile requires design-change + ADR evidence for RECONCILE REQUIRED`. Transition valid entries to `CLOSED`; set `Updated:`.
- Reject (no-op + `BLOCKED: no matching ledger entry for <stable-id>`) when no entry matches; reject when the entry is already terminal (`CLOSED`/`WITHDRAWN`).

Actions for `withdraw` form:
- Require an existing matching non-terminal entry and a non-empty `<falsifier>`. Transition to `WITHDRAWN`; record `Falsifier:`; set `Updated:`.
- Reject (no-op + `BLOCKED: withdraw requires a falsifier`) when the falsifier is empty; reject when no entry matches.

Actions for `bump-recurrence` form (escalation rules owned by `reconciliation-ledger.md` *Recurrence and escalation rules*):
- Require an existing matching `OPEN` entry. For `spec-stale`/`design-changed`: increment `Recurrence:`; at `2`, transition to `RECONCILE REQUIRED`. Set `Updated:`.
- **No-op** for `code-defect`/`ambiguous-intent` entries (these classes do not escalate) – report the no-op, do not error.
- Reject (no-op + `BLOCKED: no matching ledger entry for <stable-id>`) when no entry matches.

Actions for `override-close` form:
- Require an existing matching `OPEN`/`RECONCILE REQUIRED` entry and a non-empty `<reason>`. Record the `Override reason:` against that entry; set `Updated:`. The entry keeps its status (the override unblocks the completion-presentation gate; it does not close the entry).
- Reject (no-op + `BLOCKED: override-close requires a reason`) when the reason is empty; reject when no entry matches.
