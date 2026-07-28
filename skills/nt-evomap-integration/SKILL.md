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
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as f20f8af36e0f488779d3f543a217b2d19ea2db81. |
| G1 Lane classification | Classify the work as Rust execution-critical/performance, supported Python V2 strategy/config, Python AI/advisory, or legacy. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template lane inventory and Python/Rust V2 strategy boundary tests. |
| G2 Legacy label | Label legacy Cython/v1 and Python live TradingNode guidance as migration/reference-only. | Pass | Compatibility note in this file names legacy Cython/v1 and Python live `TradingNode` as migration/reference-only. |
| G3 Rust ownership | Rust owns runtime, adapter networking/parsing, normalization, risk/execution state, and performance-sensitive paths; Python and Rust strategies remain supported V2 surfaces. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the ownership-boundary regression tests; `references/developer_guide/python.md:12-14` records upstream Python strategy support. |
| G4 NT V2 API shape | Use current NT V2/PyO3 API shapes and crate/module boundaries instead of retired APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` byte-compared all 18 guide bodies to pinned upstream f20f8af; `uv run pytest -q tests/test_v2_guidance_hardening.py` passed current API-shape regressions. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 253 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 106 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pending | Final Phase 4 reconciliation, logical commit SHAs, and push evidence are recorded only after the working tree is committed and pushed. |

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

Use five explicit components:

- `EvoMapProxyMailboxClient`: thin local gateway for Proxy mailbox and asset endpoints.
- `CapsuleMapper`: transforms internal events and model outputs into bounded payloads.
- `CapsulePolicy`: enforces allowlists, retry budgets, approval gate, and payload redaction.
- `ProvenanceStore`: records `event_id`, asset id, suggestion hash, and decision reason.
- `AdvisoryOrchestrator` (optional): LangChain/LangGraph workflow for offline analysis, never trading-loop execution.

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

1. Emit lightweight internal events from Strategy/Actor to a bounded queue.
2. On timer events, map queue items into sanitized assets and call `asset/submit` through the local Proxy mailbox client.
3. Poll for suggestions or asset review results on timer boundaries, validate through policy, and stage for review.
4. Apply only approved local configuration changes outside hot handlers and persist outcome metadata.
5. Report accepted/rejected outcomes through mailbox/asset events for EvoMap provenance.

## Implementation checklist

- [ ] Create a Proxy mailbox sidecar client and keep endpoint semantics isolated from trading logic.
- [ ] Add timer-driven sync loop and bounded queue.
- [ ] Implement policy checks for field allowlist, approval gate, retry budgets, and payload redaction.
- [ ] Add deterministic fallback when EvoMap, LangChain, or LangGraph orchestration is unavailable.
- [ ] Add provenance logging for all suggestion decisions.
- [ ] Cover behavior in tests for success, timeout, degraded mode, and approval-gated resume.

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
- `nt-strategy-builder` for runtime wiring in backtest/paper/live nodes.
- `nt-review` for final safety and readiness checks.
