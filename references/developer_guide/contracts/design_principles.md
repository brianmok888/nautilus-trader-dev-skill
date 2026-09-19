# Design Principles Contract

Sources:

- `references/developer_guide/design_principles.md`

## Required guidance

- Preserve message immutability across actor, strategy, adapter, cache, and
  message-bus boundaries.
- Use new value objects or state transitions instead of mutating published
  messages in place.
- Treat determinism, replayability, concurrency safety, auditability, and
  debuggability as production design constraints.
- Preserve callback causal roots through command, event, system, and time
  channels: within one runtime thread, canonical actor and strategy callbacks
  preserve publication order across components and topics, and a nested
  publication must not overtake an earlier publication's pending deliveries
  (see `references/developer_guide/callback_dispatch.md`).
- Charge callback progress budgets by causal root: budget accounting counts
  completed callback deliveries per root; it does not bound callback duration
  or command-only loops.

## Review rule

Code or examples that mutate events, commands, requests, or responses after they
are published need redesign or a documented local-only exception. Callback
designs that assume queued actor/strategy delivery is active, that drop causal
roots when forwarding work across channels, or that rely on synchronous
message-bus reentry activating queued callbacks, contradict the pinned
callback-dispatch contract and need redesign.
