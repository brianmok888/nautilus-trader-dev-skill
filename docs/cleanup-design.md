# Master-Prompt Alignment Cleanup Design

## Goal

Align `nautilus-trader-dev-skill` with `docs/prompts/master-prompt.md` so the repository contains only reusable skills, references, templates, tests, and validation tooling for NautilusTrader development. Upstream NautilusTrader remains read-only evidence. AI/EvoMap work belongs to `nautilus-daedalus-dev-skill` and must not remain as an active or test-gated lane here.

## Removal boundary

Remove:

- the complete `skills/nt-evomap-integration/` lane and its G2 evidence;
- EvoMap/advisory plans, templates, tests, and cross-references;
- completed historical design, implementation, audit, reconciliation, handoff, and session-state artifacts under `docs/plans/`, `docs/superpowers/`, `docs/handoffs/`, and `.superpowers/`;
- obsolete cutover-attestation tooling/tests and scaffolding whose only role is historical process tracking;
- optional legacy EvoMap sidecar guidance under `nt-implement`.

Retain:

- `docs/prompts/master-prompt.md` as the repository mission specification;
- current tracking documents when rewritten to describe the post-cleanup repository;
- current NT skills, references, examples, tests, and validators that directly guide or prove NautilusTrader development behavior;
- migration-labelled Python NT material where it remains useful for upstream-compatible migration/reference work.

## Main skill and documentation alignment

Update the `nt` router, `README.md`, `AGENTS.md`, `skills/AGENTS.md`, end-to-end guidance, tracking charters, and G2 registry so they:

1. route only to NautilusTrader-development skills;
2. identify no active AI/EvoMap lane;
3. state that AI/advisory work is out of repository scope rather than a Python exception;
4. preserve the Rust V2 default and migration/reference-only labels for legacy NT Python material;
5. treat current upstream source and developer guides as read-only authority.

## Validation strategy

Add or update boundary tests first so they fail while excluded artifacts and references remain. Then remove the approved files and update the smallest set of repository manifests and docs needed to satisfy the new contract. Finish with the complete test suite, deterministic sync/freshness validators, non-AI G2 card validation, diagnostics, diff checks, and manual router inspection.

## Success criteria

- No tracked file or current repository guidance routes to EvoMap/AI advisory work.
- Historical execution/session artifacts are absent from the working tree.
- The `nt` main skill exposes only NT-development routes and explicitly keeps upstream read-only.
- All retained skill G2 evidence hashes match their owned content.
- Full validation passes without exclusions for a removed AI lane.
