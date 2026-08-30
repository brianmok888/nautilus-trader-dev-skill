# Skill-Pack Specifications

Status: approved bootstrap, 2026-08-29.

This directory contains concise, machine-addressable behavior specifications for stable `nautilus-trader-dev-skill` governance and scope contracts. The bootstrap was reviewed against the current prompt, root instructions, trackers, validators, and tests before activation.

## Truth and drift

Upstream NautilusTrader source and official documentation remain the subject-matter ground truth in the hierarchy defined by `docs/prompts/master-prompt.md`. Within this repository, current skill content, executable validators and tests remain primary truth; these specs are the canonical documentation of approved stable behavior. If a spec conflicts with those executable surfaces, do not follow the stale spec or silently edit it. Record the discrepancy and reconcile the implementation and spec through the mission's declared `spec-deltas`.

Historical research explains why guidance changed. These files state the currently approved stable contracts. Existing trackers keep their charters: `Handguard.md` owns invariants, `Structure.md` owns repository shape, `Components.md` owns skill readiness, and `Findings.md` owns finding state and closure evidence.

## Mission delta schema

Every Phase 2 implementation manifest declares a top-level YAML `spec-deltas` field.

No behavior-spec change:

```yaml
spec-deltas: []
```

A behavior-spec change:

```yaml
spec-deltas:
  - file: docs/specs/skill-pack-authority.md
    operation: amend
    section: repository-scope
    summary: Clarify the new supported NT V2 development boundary.
```

Each entry contains exactly:

- `file`: an existing or proposed path below `docs/specs/`;
- `operation`: `add`, `amend`, or `remove`;
- `section`: the stable lowercase kebab-case section identifier targeted in that file;
- `summary`: one sentence stating the observable contract change.

Apply entries in listed order during Phase 5 reconciliation after Phase 3 approval. `add` creates the named section or file, `amend` changes the named existing section, and `remove` deletes the named existing section or file. Missing or duplicate targets block closure. `spec-deltas: []` makes no spec edit.

## Initial specifications

- `workflow-governance.md` — mission lifecycle, receipt ownership, evidence classification, and secret safety.
- `skill-pack-authority.md` — repository scope and upstream/skill-pack authority boundaries.
