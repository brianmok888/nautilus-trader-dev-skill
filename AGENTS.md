# PROJECT KNOWLEDGE BASE

## Agent Workflow

This workflow applies only within `nautilus-trader-dev-skill`. Repository-specific mission, scope, and commands elsewhere in this file remain authoritative.

### Communication

- Be concise, direct, and candid.
- Distinguish verified facts, uncertainty, and recommendations. Challenge assumptions that conflict with repository evidence.
- When explaining complex behavior, invoke the `Visualize` skill. If it is unavailable, use a compact Mermaid or ASCII diagram and disclose the fallback.

### Sources and Research

- Ground version-sensitive claims in current authoritative sources: this repository, the read-only upstream NautilusTrader checkout, official documentation, specifications, release notes, or primary maintainer statements.
- Link important external evidence and cite repository evidence as `path/to/file.ext:line`.
- Never present memory or inference as verified fact.

### Execution

For authorized implementation work:

1. Read every applicable `AGENTS.md`; deeper files override broader files.
2. Preserve the user's original goal, the NT-only scope, the read-only upstream boundary, and all stated constraints.
3. Inspect the relevant implementation, callers, tests, and repository status.
4. Load relevant skills before acting.
5. Plan the smallest complete change.
6. Add a failing behavioral regression test for a bug or behavior change.
7. Implement the minimal correction in this skill repository only.
8. Run diagnostics, related tests, and the repository validation commands documented below.
9. Exercise the changed behavior through its real user-facing interface when one exists.
10. Review substantial changes before reporting completion.

Do not stop at a proposal when implementation was authorized.

### Decisions and Questions

- Make ordinary, reversible implementation decisions independently.
- Ask one focused question only when different answers materially change the result, the action is destructive or externally visible, or credentials, approval, or unavailable information are required.
- State the blocked decision and its consequences.

### Skills and Delegation

- Use a skill when it materially applies to the task.
- Spawn subagents only for genuinely independent work that can run concurrently.
- Give each subagent one bounded deliverable and required evidence.
- Independently verify and synthesize subagent findings; do not forward reports uncritically.

### Change Discipline

- Keep changes focused on the requested NT-skill outcome and preserve the separation from Daedalus, AI, and other downstream application work.
- Avoid unrelated cleanup, speculative abstractions, compatibility shims, and low-signal tests.
- Match existing repository conventions and preserve unrelated working-tree changes.
- Never use destructive Git operations or modify upstream, production, downstream, or external systems without explicit authorization.

### Verification

A change is complete only when:

- the requested observable behavior works;
- relevant diagnostics and tests pass;
- the real interface has been exercised when one exists;
- failures caused by the change are fixed; and
- pre-existing failures are identified rather than hidden.

Do not claim that something passes unless the proving command was executed and its output inspected.

### Reporting

- During work, report only meaningful phase changes, decisions, and blockers.
- Final responses should state the outcome, evidence, concise changes with file references, and residual blockers or uncertainty.
- Avoid routine progress narration and unsupported assurances.

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material in this file is migration/reference-only; prefer Rust V2/PyO3 and `LiveNode` for current work.

## Mission

This repository contains reusable AI-agent skills for **NautilusTrader development only**. It guides architecture, implementation, testing, integration, operation, and review of NautilusTrader components. `docs/prompts/master-prompt.md` is the maintenance mission and scope authority.

Upstream NautilusTrader is read-only ground truth. Inspect its source, developer guides, examples, tests, schemas, and toolchain standards to improve this repository, but never implement or prepare upstream changes while executing the master prompt. AI, advisory, evolution-system, and downstream application work belong in separate repositories.

## Repository shape

```
nautilus-trader-dev-skill/
├── skills/                       # 17 NT development skills
│   ├── nt/                       # Entry-point router
│   ├── nt-architect/             # Architecture decomposition
│   ├── nt-implement/             # Rust-first component implementation
│   ├── nt-strategy-builder-rust/ # Production Rust strategy and LiveNode path
│   ├── nt-strategy-builder/      # Migration/reference-only Python workflows
│   ├── nt-dex-adapter/           # Custom DEX adapter development
│   └── nt-review/                # Pre-deployment review
├── references/                   # Upstream-derived NT references and contracts
├── tests/                        # Repository behavior and evidence gates
├── tools/                        # Sync, freshness, classification, and G2 validators
└── docs/                         # Current guides, prompt, and tracking charters
```

## Routing

Start with `skills/nt/SKILL.md`. It classifies the request and loads the smallest relevant skill set.

| Work | Primary skill |
| --- | --- |
| Architecture and decomposition | `nt-architect` |
| Component implementation | `nt-implement` |
| Production Rust strategies | `nt-strategy-builder-rust` |
| Backtests | `nt-backtest` |
| Live operation | `nt-live` |
| Market data and catalogs | `nt-data` |
| Orders, positions, and execution | `nt-trading`, `nt-model` |
| CeFi adapters | `nt-adapters` |
| DEX adapters | `nt-dex-adapter` |
| Signals and indicators | `nt-signals` |
| Core contribution guidance | `nt-dev`, `nt-testing` |
| Review | `nt-review` |
| Learning | `nt-learn` |

## Source authority

1. Pinned upstream commit from `tools/upstream_baseline.py` for reproducible G2 validation.
2. Reviewed current-develop delta in `references/upstream-delta-review.json` for version-scoped overlays.
3. Local canonical contracts in `references/developer_guide/contracts/`.
4. Skill guidance and templates.

When sources disagree, label the version boundary explicitly. Do not invent APIs or treat a current-develop feature as available at the pin.

## Development rules

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material below is migration/reference-only; use Rust V2/PyO3 and `LiveNode` for current work.

- Default new guidance to Rust V2, PyO3, and `LiveNode`.
- Label Cython/v1 and Python `TradingNode` material migration/reference-only.
- Preserve user and concurrent-agent changes; do not revert unrelated work.
- Use test-first development for behavioral changes.
- Keep files focused and avoid speculative abstractions.
- Update G2 owned-content hashes when owned skill/test/tool content changes.
- Do not modify AI or downstream-project artifacts; they are outside this repository and should not exist here.

## Validation

Run the relevant focused tests while editing, then complete:

```bash
python3 -m pytest -q
python3 tools/check_dev_guide_sync.py
python3 tools/check_dev_guide_snapshot_sync.py
python3 tools/check_rust_trading_reference_sync.py
python3 tools/check_legacy_labelling.py
python3 tools/check_upstream_freshness.py --format json
python3 tools/check_skill_g2_harnesses.py --check-cards
git diff --check
```

A validator result is evidence only when its command exited successfully in the current work session.

## Tracking charters

- `docs/tracking/Handguard.md`: non-negotiable invariants.
- `docs/tracking/Structure.md`: current repository wiring and inventory.
- `docs/tracking/Components.md`: per-skill behavior and readiness.
- `docs/tracking/Findings.md`: current findings and closure evidence.

Do not store session handoffs, completed implementation plans, external attestations, or generated agent state in the repository.
