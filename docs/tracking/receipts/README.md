# Governance Evidence Receipts

Receipt schema version: 1.

Receipts are bounded, machine-validated evidence for mission findings. They do not replace fresh verification, and their evidence state never changes the P0/P1/P2 impact of a finding.

## Paths and ownership

Store each receipt as:

```text
docs/tracking/receipts/<mission-stem>/<receipt-id>.json
```

Use lowercase kebab-case mission and receipt identifiers. Phase 2 writes implementation receipts with `owner_stage: phase-2`. Phase 3 never rewrites them; it writes distinct verifier receipts with `owner_stage: phase-3`.

For a legacy or externally implemented mission that predates receipts, Phase 3 may create verifier-owned receipts from fresh evidence and record the missing implementation provenance. That limitation does not block entry into verification.

## Version 1 object

Every JSON object contains exactly:

| Field | Type | Contract |
|---|---|---|
| `schema_version` | integer | Must equal `1`. |
| `mission` | string | Lowercase kebab-case mission/report stem. |
| `receipt` | string | Lowercase kebab-case receipt ID and filename stem. |
| `finding_id` | string | Stable `NT-...` Finding ID. |
| `owner_stage` | string | `phase-2` or `phase-3`. |
| `evidence_state` | string | `verified`, `verified-manual`, or `unverified`. |
| `severity` | string | `none`, `P0`, `P1`, or `P2`; impact is independent of evidence state. |
| `command` | string | Exact redacted command or manual-step sentinel. |
| `exit_code` | integer | Process exit code; use `0` for a completed manual observation. |
| `output_sha256` | string | SHA-256 of the UTF-8 bytes of `output_excerpt` exactly as stored. |
| `output_excerpt` | string | Bounded, normalized, redacted output. |
| `redactions` | array of strings | Rules applied; empty only when no redaction marker is present. |
| `recorded_at` | string | UTC `YYYY-MM-DDTHH:MM:SSZ`. |

Unknown fields are rejected so schema changes require a version bump. The validator also binds each receipt's `mission` and `receipt` values to its directory and filename.

## Secret safety

Never store raw credentials, tokens, cookies, private keys, database passwords, credential-bearing URLs, or unbounded output. Redact the command and output before writing JSON. List every applied redaction in `redactions`, then hash the normalized redacted excerpt. Never hash or retain a raw secret-bearing excerpt in the tracked tree.

When no safe excerpt can be retained, store:

```text
[OMITTED: sensitive output retained outside git]
```

Hash that exact marker and explain the omission in `redactions`. The external output remains untracked and is not a repository receipt.

## Validation

```bash
python3 tools/check_governance_receipts.py
python3 tools/check_governance_receipts.py --help
```

The validator checks schema version, required and unknown fields, enums, stable Finding IDs, directory/filename binding, digest integrity, timestamps, redaction metadata, and common secret patterns.
