# Progressive Cutover Gate Template

<!-- CHARTER -->
<!-- Role: Standard gate-card contract for NautilusTrader Rust V2 skill delivery. -->
<!-- Does NOT contain: historical attestations, session plans, or unsupported pass claims. -->

Use this template for every gate that applies to a skill change. Copy the card into
mission evidence or a pull-request description; do not mark `Pass` without a
reproducible command, artifact, metric, or source citation. Use `Pending` when the
check has not run and `Blocked` when a named prerequisite prevents it.

## Gate card

| Field | Required value |
| --- | --- |
| Objective | The single property this gate proves. |
| Applicability | Why the gate applies, or `N/A` with a source-backed reason. |
| Evidence | Reproducible commands, artifacts, metrics, logs, or exact `file:line` citations. |
| Status | `Pass`, `Pending`, or `Blocked`. |
| Owner | Person or subsystem responsible for closing the gate. |
| Last verified | ISO date and the baseline commit or release used. |
| Next action | Smallest concrete action that advances a non-pass gate. |
| Blocker | Named dependency for `Blocked`; `None` otherwise. |

## Standard gates

### Architecture Consistency
- Objective: preserve the Rust V2 boundary, ownership model, event flow, and read-only upstream rule.
- Applicability: all architecture, strategy, adapter, data, model, live, and integration changes.
- Evidence: architecture decision, dependency direction, state ownership, and source-pinned upstream citations.

### Dependency and Build Health
- Objective: prove supported toolchains, dependency versions, lock state, and clean builds.
- Applicability: code, templates, generated projects, dependency instructions, and build tooling.
- Evidence: pinned toolchain metadata plus clean `cargo check`, `uv run python -m pytest`, or equivalent build output.

### API and Binding Contract
- Objective: preserve Rust/PyO3/FFI/API signatures, serialization, errors, ownership, and compatibility guarantees.
- Applicability: public APIs, bindings, schemas, adapters, model types, and generated interfaces.
- Evidence: compile-time checks, contract tests, schema diffs, and exact upstream source citations.

### Correctness Test Pyramid
- Objective: prove behavior at unit, property, integration, and end-to-end levels without timing luck.
- Applicability: every behavior change.
- Evidence: deterministic focused tests, relevant integration tests, and one real-surface execution.

### Performance Regression Control
- Objective: protect latency, throughput, allocation, and memory budgets with comparable measurements.
- Applicability: hot paths, parsers, order books, backtests, networking, persistence, and concurrency.
- Evidence: release-mode benchmark protocol, hardware/toolchain metadata, baseline comparison, and thresholds.

### Resilience and Failure Recovery
- Objective: prove timeouts, backpressure, retry limits, restart behavior, reconciliation, and state recovery.
- Applicability: live, adapter, network, persistence, async, and operational flows.
- Evidence: fault injection, bounded failure tests, recovery checkpoints, and idempotency proof.

### Observability and Operability
- Objective: make failures diagnosable and routine operation measurable without exposing secrets.
- Applicability: services, live nodes, adapters, automation, and long-running tasks.
- Evidence: structured logs, metrics/traces, health signals, runbook steps, and alert ownership.

### Security Safety and Governance
- Objective: protect credentials, signing, permissions, auditability, supply chain, and trading safeguards.
- Applicability: external I/O, secrets, execution, deployment, adapters, plugins, and dependencies.
- Evidence: secret scans, permission review, fail-closed checks, audit records, and dependency provenance.

### Release and Rollback Readiness
- Objective: make promotion, rollback, migration, and compatibility decisions explicit and reversible.
- Applicability: shipped behavior, schemas, persisted data, live configuration, and published artifacts.
- Evidence: release checklist, versioning decision, rollback trigger, state migration, and rollback rehearsal.

### Integration and Acceptance
- Objective: prove the component works with real NautilusTrader integration surfaces and acceptance criteria.
- Applicability: all user-facing skills, templates, adapters, strategies, nodes, and workflows.
- Evidence: credentialless integration harness where possible, matching-surface QA, and acceptance outputs.

### Continuous Improvement
- Objective: capture residual risk, ownership, follow-up evidence, and the next review trigger.
- Applicability: every completed change set.
- Evidence: Findings ledger status, gate residuals, benchmark/test trends, and named owners with dates.

## Status rules

- `Pass`: evidence ran successfully against the stated baseline and is attached or reproducible.
- `Pending`: applicable evidence has not run; name the next action and owner.
- `Blocked`: a named prerequisite prevents execution; name the blocker, owner, and unblock condition.
- `N/A` is allowed only in Applicability, never as a Status, and must state why the gate cannot affect the change.
