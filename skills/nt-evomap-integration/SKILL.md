---
name: nt-evomap-integration
description: Use when integrating evomap.ai advisory workflows into NautilusTrader systems with non-blocking execution, explicit approval gates, and auditable decision provenance.
---

# nt-evomap-integration

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` passed against pinned upstream `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; current-develop drift is version-scoped in `README.md`. |
| G1 Legacy label | No Cython/v1/TradingNode guidance remains unlabelled outside source-pinned upstream snapshots. | Pass | `uv run python tools/check_dev_guide_sync.py` passed; `uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'` passed 25 tests. |
| G2 V2 example validation | Compile or validate examples applicable to this skill against the pinned NT V2 baseline. | Pass | `uv run python tools/check_skill_g2_harnesses.py --execute --skill nt-evomap-integration` passed the repository AI-advisory contract in its pinned V2 Python environment against `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; schema-v2 provenance is recorded in `references/g2-evidence/nt-evomap-integration.json`. |
| G3 Rust bindings/PyO3 | Rust bindings, PyO3 registration paths, callback routing, and crate ownership match current nautilus_core/V2 boundaries. | Pass | `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'` passed 10 tests. |
| G4 Lane and API shape | Classify migration-only Python, active AI/advisory Python, bounded PyO3 control-plane, and Rust production lanes while using current V2 API shapes. | Pass | `uv run pytest -q tests/test_markdown_lane_contract.py tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed; `uv run python tools/check_dev_guide_snapshot_sync.py` matched all 18 pinned guide bodies. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | `uv run pytest -q --ignore=tests/test_quality_gates.py` passed; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'` passed 24 tests. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pass | `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md` records the post-fix findings, validation commands, gate results, and residual risk. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

EvoMap gates: Python is allowed only for the AI/advisory lane through the proxy mailbox/control plane; every recommendation requires audit trail, approval gate, timeout/fallback, and explicit non-authority over execution-critical order/risk/live-node paths. Rust trading/adapters must continue safely when the advisory sidecar is unavailable.

Integrate EvoMap as an external advisory sidecar for NautilusTrader without coupling external availability to trade execution.

## When to use

- You want to publish strategy or actor artifacts to EvoMap for cross-agent refinement.
- You want to fetch EvoMap suggestions and selectively apply them under operator control.
- You need repeatable governance for external intelligence in backtest, paper, or live.
- You need to wrap a LangChain/LangGraph advisory workflow around Nautilus outputs without making it execution authority.

Do not use this skill for building venue adapters. Use `nt-dex-adapter` for adapter construction.

## Core invariants

1. Nautilus remains the only execution authority.
2. EvoMap remains advisory-only and never auto-applies to live behavior.
3. No external network I/O, LLM calls, or graph execution in hot handlers (`on_bar`, `on_quote_tick`, `on_order_book_deltas`).
4. EvoMap failures must degrade safely to local-only operation.
5. Every accepted or rejected suggestion must be traceable.
6. Agents call the local Proxy mailbox; the agent does not call Hub APIs directly.

## Integration architecture

Use two separated processes and one local contract:

- External Python proxy: owns Proxy HTTP, model/graph work, redaction, retries, and durable provenance.
- `python_sidecar/brainstorming_evomap`: the only shipped executable Python
  network client in this skill; it may call the localhost Proxy and must not be
  imported by the actor or any Rust execution path.
- `AdvisoryBridgeActor`: NT V2 `DataActor` that drains only a bounded local mailbox on a short timer callback.
- `AdvisoryMailboxPort`: non-blocking request/result queues plus two independent durable-transfer outboxes: one FIFO for non-terminal provenance and one FIFO for terminal checkpoints. The actor owns this local port; the proxy-facing integration may only transfer records into and out of it. It has no network client, message-bus, signal, data-publication, or execution capability.

The actor stages immutable `AdvisoryRequest`, `AdvisoryResult`,
`AdvisoryDecision`, and `AdvisoryAuditRecord` values. Approval must match the
request ID, suggestion ID, and suggestion hash. Its maximum representable
authority is `OFFLINE_CHANGE_REVIEW`; it cannot submit orders or change live
trading behavior. Audit acceptance occurs before any approval state transition,
so audit backpressure fails closed. Each terminal checkpoint ID is a SHA-256
digest of the complete immutable record, including request and suggestion
identity, outcome, reason, and timestamp; sequence/outcome pairs alone are not
checkpoint identities.

The proxy must persist before removal on both outboxes: peek the oldest record,
durably persist it, then acknowledge that exact digest so the port removes that
exact head record. No destructive `take` operation is exposed for proxy-facing
audit or checkpoint transfer. Terminal persistence also atomically advances the
durable `request_sequence_floor` before the proxy enqueues the matching local
checkpoint acknowledgment. The actor removes the exact checkpoint before it
mutates its sequence floor, authority, or request slot. Mismatched/stale
acknowledgments fail closed, duplicate decisions cannot replace a pending
terminal checkpoint, and lifecycle reset preserves a pending checkpoint and an
already-enqueued acknowledgment for idempotent recovery. The sidecar's
`AdvisoryCheckpointStore` is the reference durable adapter: one SQLite
transaction inserts the immutable terminal record and advances the sequence
floor, then returns the acknowledgment. Retrying after commit but before
acknowledgment delivery is idempotent; injected failures before commit roll back
both writes. This adapter is a reference implementation for the trusted local
proxy boundary, not a network service and not an execution-authority component.

### Proxy mailbox contract

Current Evolver integrations communicate through a local Proxy mailbox. Keep the protocol boundary inside the sidecar client:

Discover the local Proxy from `~/.evolver/settings.json`; the default is
`http://127.0.0.1:19820`, overrideable by `EVOMAP_PROXY_PORT`. Agent-side code
talks to localhost only. The Proxy owns Hub auth, heartbeat, retries, and sync.

- `POST /mailbox/send` — enqueue local messages for asynchronous sync.
- `POST /mailbox/poll` — fetch local mailbox results such as asset review decisions.
- `POST /mailbox/ack` and `GET /mailbox/status/{message_id}` — acknowledge and observe outcomes.
- `GET /mailbox/list?type=...&limit=...` — inspect local messages for diagnostics.
- `POST /asset/submit` — submit Gene/Capsule/EvolutionEvent assets.
- `POST /asset/fetch` and `POST /asset/search` — retrieve or search advisory assets.
- `POST /task/subscribe`, `GET /task/list`, `POST /task/claim`,
  `POST /task/complete`, and `POST /task/unsubscribe` — optional task
  workflow endpoints; keep them out of trading logic unless the sidecar is
  explicitly handling offline review work.

Treat direct Hub protocol details as Proxy-owned. Strategy and Actor code should only see domain methods such as `submit_assets`, `poll`, and `search_assets`.

### LangChain / LangGraph boundary

If advisory reasoning uses LangChain or LangGraph:

- Use LangChain only for model/tool abstraction and structured proposal generation around exported artifacts.
- Use LangGraph `StateGraph` only for stateful, durable, human-in-the-loop review workflows outside Nautilus hot handlers.
- Persist graph checkpoints/proposals as advisory evidence, not as executable trading state.
- Resume or interrupt advisory graphs through an operator approval gate before any strategy configuration changes.
- Do not add LangChain or LangGraph as required dependencies of this skill repo or of execution-critical trading code.

## Recommended flow

1. Build an offline review artifact outside NT market handlers.
2. Enqueue an immutable request through the bounded local mailbox.
3. Let the external proxy perform all network/model work outside the actor.
4. On the actor timer, drain at most one already-local result, reject late or mismatched identity, write audit provenance, and stage it as non-actionable.
5. Accept an exact human decision only after terminal-checkpoint capacity is available; keep the staging provenance FIFO independent from the terminal checkpoint outbox. The external proxy peeks and atomically persists the complete terminal record plus `request_sequence_floor`, then returns its record-bound digest as a local acknowledgment. Remove that exact checkpoint before granting offline review authority or releasing terminal request state.
6. Continue Rust trading, adapter, risk, and live-node operation unchanged when the mailbox or proxy is unavailable.

## Implementation checklist

- [ ] Keep Proxy HTTP and model/graph work in the external Python proxy, never the actor.
- [ ] Use the bounded non-blocking `AdvisoryMailboxPort`; never wait or replace older work.
- [ ] Match request sequence, request ID, suggestion ID, and suggestion hash before approval.
- [ ] Assign strictly increasing request sequences from durable proxy state, restore `request_sequence_floor` from the durable audit checkpoint after restart, reject `now_ns >= deadline_ns` as late, and reject every replay deterministically.
- [ ] Keep terminal requests pending until the external proxy acknowledges atomic persistence of the audit record and sequence floor.
- [ ] Use separate provenance and terminal-checkpoint outboxes; persist-peek-ack-remove each exact record and expose no destructive proxy-facing transfer.
- [ ] Bind each checkpoint digest to the complete immutable record, reject stale/mismatched acknowledgments, and preserve pending checkpoint acknowledgments across reset.
- [ ] Require provenance or checkpoint acceptance before staged/approved state changes.
- [ ] Release the request slot only after the durable checkpoint acknowledgment for an audited approval, operator rejection, or timeout.
- [ ] Cover sequential success, rejection, timeout, replay, identity mismatch, audit backpressure, and degraded mode.

## Safety review checklist

- [ ] No EvoMap, LangChain, or LangGraph calls on hot handlers.
- [ ] No secrets in payloads or logs.
- [ ] No auto-merge of external suggestions.
- [ ] Rejected suggestions include reason codes.
- [ ] Fallback mode is explicit and observable.
- [ ] Local Proxy mailbox is the only EvoMap network boundary used by agent-side code.

## Example invocation prompts

Use these copy-paste prompts with the skill to accelerate common workflows.

### 1) Architecture boundary definition

```text
Design an EvoMap integration boundary for our NautilusTrader system.
Constraints:
- EvoMap must remain advisory-only
- No network I/O, LangChain model calls, or LangGraph execution in hot handlers
- Deterministic local fallback when the Proxy mailbox or advisory graph is unavailable
- Include provenance fields for every accept/reject decision
Deliverable:
- Component diagram (Proxy client/mapper/policy/store/orchestrator)
- Lifecycle placement (`on_start`, timer loop, `on_stop`)
- Failure-mode table
```

### 2) Implementation planning

```text
Create an implementation plan for adding EvoMap sidecar support.
Include:
- `EvoMapProxyMailboxClient` interface (`mailbox/send`, `mailbox/poll`, `asset/submit`, `asset/fetch`, `asset/search`)
- Timer-driven queue processing design
- Payload allowlist and redaction policy
- Optional LangChain/LangGraph advisory workflow boundaries
- Test matrix for success, timeout, approval-gated resume, and degraded mode
Output should be ordered as: files to edit, code skeletons, tests, rollout steps.
```

### 3) Runtime wiring and rollout

```text
Wire EvoMap sidecar into our strategy runtime.
Requirements:
- Proxy asset submit/search and mailbox poll run on timer boundaries only
- Approval gate required before behavior changes
- Emit metrics for queue size, submit success rate, fallback activation, and graph checkpoint state
- Keep backtest behavior deterministic
Return a rollout checklist for dev -> paper -> live.
```

### 4) Pre-deployment review

```text
Review EvoMap integration for live readiness.
Verify:
- advisory-only enforcement
- local Proxy mailbox boundary only
- no secret leakage in payloads/logs
- explicit degraded-mode behavior
- full provenance coverage and decision reason codes
- optional LangGraph StateGraph checkpoints cannot auto-apply changes
Classify findings as blocker/major/minor with concrete fixes.
```

## Verification commands

```bash
# Run relevant tests in your project
pytest -q

# Validate strategy wiring if used
python examples/live_node.py
```

## Works with

- `nt-architect` for boundary definition and lifecycle placement.
- `nt-implement` for component-level implementation patterns.
- `nt-strategy-builder-rust` for Rust `LiveNode` or backtest runtime wiring; `nt-strategy-builder` is migration/reference-only.
- `nt-review` for final safety and readiness checks.
