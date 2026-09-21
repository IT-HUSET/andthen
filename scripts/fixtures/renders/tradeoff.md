# Trade-off Analysis: Audit Write Placement

## Decision Statement

Where the sign-in audit row is written relative to the response, given that the reviewer needs the row whenever the response claims success.

## Scoring Matrix

| Option | Durability | Latency | Simplicity | Total |
|---|---|---|---|---|
| Synchronous write ← chosen | 5 | 2 | 5 | 12 |
| Buffered local queue | 4 | 5 | 3 | 12 |
| Fire-and-forget | 1 | 5 | 5 | 11 |

## Options

### Synchronous write

#### What changes
The handler awaits the audit write before sending the response.

#### Where it changes
`src/auth/routes/sign-in.ts` only; the audit client is unchanged.

#### Risk
Audit latency becomes sign-in latency, and an audit outage becomes a sign-in outage.

### Buffered local queue

#### What changes
The handler enqueues the event; a drainer writes it.

#### Where it changes
`src/auth/routes/sign-in.ts` plus a new drainer module and its lifecycle wiring.

#### Risk
A crash between enqueue and drain loses rows, which is the failure the audit exists to prevent.

## Recommendation

Synchronous write, with a bounded timeout that degrades to the buffer. The durability claim is the point of the feature; the latency cost is measurable and bounded.
