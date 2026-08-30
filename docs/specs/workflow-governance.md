# Workflow Governance Specification

Status: approved bootstrap, 2026-08-29.

## mission-lifecycle

The master-prompt mission uses preflight followed by Phases 0 through 6. Phase 2 implements source-backed findings and emits an implementation manifest. Explicit user approval permits Phase 3 read-only verification. Phase 5 reconciles accepted evidence and applies declared spec deltas. Phase 6 requires separate explicit approval before any commit, merge, push, release, or publication.

## spec-deltas

Every Phase 2 implementation manifest declares `spec-deltas`. An empty array means no approved stable behavior-spec change. Non-empty entries use the deterministic schema in `docs/specs/README.md` and are applied only during Phase 5 reconciliation after Phase 3 approval.

## receipt-ownership

Governance receipts are versioned JSON files validated by `tools/check_governance_receipts.py`.

Phase 2 owns implementation receipts. Phase 3 never modifies them; it writes separate verifier-owned receipts for fresh reruns. For a legacy or externally implemented mission with no Phase 2 receipts, Phase 3 may create verifier-owned receipts and proceed when fresh evidence covers every Finding ID. Missing historical implementation receipts are recorded as a provenance limitation, not an entry deadlock.

## evidence-and-severity

Finding impact (`P0`, `P1`, `P2`, or `none`) is independent of evidence state (`verified`, `verified-manual`, or `unverified`). Missing evidence never lowers impact. An unverified P0/P1 finding keeps its impact, rejects Phase 3 approval, and remains open until fresh evidence resolves it. Only verified evidence authorizes closure or lifecycle transitions.

## secret-safety

Receipts never store raw credentials, tokens, cookies, private keys, database passwords, credential-bearing URLs, or unbounded output. Commands and output excerpts are redacted before storage; the receipt lists redaction rules and hashes the stored redacted excerpt. When no safe excerpt can be retained, the receipt stores the fixed omission marker documented in `docs/tracking/receipts/README.md` and hashes that marker.
