# NT V2 Rust Cutover Hardening Design

## Outcome

Close the remaining audit findings so every NautilusTrader skill is V2-aware, Rust-first by default, and backed by measurable readiness evidence. The only Python-default lane is AI/EvoMap advisory work; it remains non-authoritative, asynchronous, approval-gated, and unable to submit orders or block execution.

## Authority and baseline

- Official NautilusTrader latest/nightly documentation and the upstream repository are authoritative.
- Reproducible compile evidence uses upstream `develop` commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`.
- That baseline reports NautilusTrader V2 `2.0.0rc2`, Rust workspace `0.61.0`, and Rust `1.97.1`.
- A separate read-only freshness command reports drift from current stable/develop/nightly without silently changing the reproducible baseline.

## Design

### 1. Deterministic Rust-first routing

Ambiguous strategy, live, adapter, execution, or production requests route to Rust skills and `LiveNode`. The Python strategy builder is selected only for explicit Python intent or the AI/advisory lane. Inventories list all 18 NT skills, including `nt-strategy-builder-rust`.

### 2. Copyable guidance must be executable

The Rust strategy builder contains a self-contained, upstream-shaped example. A test extracts its named Rust fence into a temporary crate and runs Cargo against the pinned upstream checkout. Stale API names, hard-coded crate versions, and brittle adapter counts are rejected by static tests.

### 3. Legacy code is quarantined, not blessed by banners

Default live, paper, DEX, and multi-venue executable surfaces become Rust-oriented or are removed when an existing Rust reference already covers the use case. Retained Python `TradingNode` material is moved or renamed into explicit legacy/migration locations. The classifier scans both template and executable-example roots and rejects legacy APIs in default/live files even when a generic file banner exists.

### 4. Evidence is content-bound

The G2 registry contains exactly the 18 NT skills. Each harness hashes at least its `SKILL.md` plus owned examples, tests, or contracts. Evidence validates upstream commit, command, result, and complete owned-path hashes; no harness may pass with an empty ownership set. `nt-live`, `nt-trading`, and `nt-strategy-builder-rust` get targeted Rust checks.

### 5. AI advisory authority is mechanically constrained

AI/EvoMap guidance and executable surfaces may analyze and recommend, but may not expose order submission, execution-client access, or synchronous hot-handler network calls. Static structural tests enforce this boundary and require timeout, fallback, approval, audit, and non-blocking semantics in the skill contract.

### 6. Reconciliation remains measurable

Readiness cards are regenerated only from fresh checks. Every gate uses `Pass`, `Pending`, or `Blocked (+ reason)` and cites a command, file, artifact, or official URL. Post-fix review reruns the original finding searches, all targeted and full quality gates, independent code review, and architecture review before shipping.

## Segment boundaries

1. Routing and 18-skill inventory.
2. Canonical Rust example plus current V2 APIs.
3. Legacy executable migration and checker hardening.
4. Complete G2 registry, content provenance, and AI authority checks.
5. Upstream freshness and archival cleanup.
6. Readiness regeneration, reconciliation, review, and shipping.

Each segment begins with a failing regression test, implements only that segment, passes its targeted tests, and receives a conventional commit.

## Acceptance criteria

- Ambiguous production strategy routing selects Rust without asking for a language.
- All 18 NT skills appear in inventory and G2 evidence.
- The Rust strategy example compiles against the pinned upstream V2 baseline.
- Removed Actor subscription APIs, hard-coded `0.57`, brittle adapter counts, and default `TradingNode` executable paths are absent.
- Legacy/Cython references are either removed or explicitly archival/migration-only.
- Every G2 artifact is non-empty, content-bound, reproducible, and validates its upstream baseline.
- AI advisory examples cannot place orders or block execution.
- Freshness reporting distinguishes reproducible baseline state from current upstream drift.
- Full repository tests, quality gates, Ruff, basedpyright/static analysis, sync checks, all 18 harnesses, and `git diff --check` pass before push.

## Non-goals

- No third-party dependency additions.
- No upstream NautilusTrader source changes.
- No claim that all supported upstream Python strategies are legacy; this repository's stricter policy only controls its own default skill routing.
- No pull request creation.

