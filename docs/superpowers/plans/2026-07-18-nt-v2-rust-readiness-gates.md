# NT V2 Rust Readiness Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add progressive NT V2 Rust readiness gates to every relevant NautilusTrader skill and enforce them with the repo checker.

**Architecture:** Keep the change documentation-first and checker-backed. Add a compact shared gate contract to NT skills, then make `tools/check_dev_guide_sync.py` validate that new skill guidance contains status vocabulary, universal gate labels, Rust-first ownership terms, AI/Python advisory boundaries, and evidence commands before a generated NT build can be called ready.

**Tech Stack:** Markdown skills, Python stdlib static checker, pytest, ruff.

---

### Task 1: RED tests for missing readiness gates

**Files:**
- Modify: `tests/test_dev_guide_sync.py`

- [ ] **Step 1: Add failing tests**

Add tests that create minimal temporary skill files and assert `run_checks()` reports:
- missing `## NT V2 Rust readiness gates` section;
- missing status vocabulary (`Pass`, `Pending`, `Blocked`, `N/A`, `Waived`);
- missing universal gates `G0` through `G7`;
- missing Rust checker evidence terms on Rust-critical skills;
- missing AI/advisory Python boundary terms on AI-capable skills.

- [ ] **Step 2: Run targeted tests to verify RED**

Run:

```bash
python3 -m pytest -q tests/test_dev_guide_sync.py -k 'readiness_gate or rust_checker or advisory_python_boundary'
```

Expected: FAIL because the checker does not yet implement these new gate validations.

### Task 2: GREEN checker implementation

**Files:**
- Modify: `tools/check_dev_guide_sync.py`

- [ ] **Step 1: Add target maps**

Add constants for all relevant `skills/nt*/SKILL.md` files requiring the shared gate section. Add per-skill required term maps for Rust evidence and AI/advisory boundaries.

- [ ] **Step 2: Add checker functions**

Implement helpers that require:
- `## NT V2 Rust readiness gates`;
- statuses `Pass`, `Pending`, `Blocked`, `N/A`, `Waived`;
- universal gate labels `G0 Upstream baseline` through `G7 Completion report`;
- per-skill gate terms.

- [ ] **Step 3: Run targeted tests**

Run:

```bash
python3 -m pytest -q tests/test_dev_guide_sync.py -k 'readiness_gate or rust_checker or advisory_python_boundary'
```

Expected: PASS after the skill content is updated in Task 3.

### Task 3: Update NT skill guidance

**Files:**
- Modify: `skills/nt/SKILL.md`
- Modify: `skills/nt-adapters/SKILL.md`
- Modify: `skills/nt-architect/SKILL.md`
- Modify: `skills/nt-backtest/SKILL.md`
- Modify: `skills/nt-data/SKILL.md`
- Modify: `skills/nt-dev/SKILL.md`
- Modify: `skills/nt-dex-adapter/SKILL.md`
- Modify: `skills/nt-evomap-integration/SKILL.md`
- Modify: `skills/nt-implement/SKILL.md`
- Modify: `skills/nt-learn/SKILL.md`
- Modify: `skills/nt-live/SKILL.md`
- Modify: `skills/nt-model/SKILL.md`
- Modify: `skills/nt-review/SKILL.md`
- Modify: `skills/nt-signals/SKILL.md`
- Modify: `skills/nt-strategy-builder/SKILL.md`
- Modify: `skills/nt-strategy-builder-rust/SKILL.md`
- Modify: `skills/nt-testing/SKILL.md`
- Modify: `skills/nt-trading/SKILL.md`

- [ ] **Step 1: Insert concise gate sections**

For each skill, add `## NT V2 Rust readiness gates` near the frontmatter/overview area. Include the shared status vocabulary and universal gates.

- [ ] **Step 2: Add per-skill gates**

Add concise bullets that connect the universal gates to each skill’s domain:
- Rust ownership and PyO3/FFI boundaries for production/performance/live paths;
- Python only for research/config/AI/advisory work;
- current NT V2 APIs (`LiveNode`, builder APIs, `StrategyCore`, etc.) where relevant;
- `cargo nextest`, `cargo clippy`, `cargo deny`, `cargo fmt --check`, fuzz/property tests, and Python checks only when applicable.

### Task 4: Verification and reconciliation

**Files:**
- Inspect all changed files.

- [ ] **Step 1: Run targeted checker tests**

```bash
python3 -m pytest -q tests/test_dev_guide_sync.py
```

Expected: PASS.

- [ ] **Step 2: Run repository checks**

```bash
python3 tools/check_dev_guide_sync.py
python3 -m pytest -q
python3 -m compileall -q tools tests
uv run --with ruff ruff check .
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Review diff**

Run `git diff --stat` and inspect changed checker/tests/skills for overbroad prose or unrelated edits.

### Task 5: Commit and push

**Files:**
- Stage only requested files.

- [ ] **Step 1: Commit**

```bash
git add docs/superpowers/plans/2026-07-18-nt-v2-rust-readiness-gates.md tools/check_dev_guide_sync.py tests/test_dev_guide_sync.py skills/nt*/SKILL.md
git commit -m "Add NT V2 Rust readiness gates"
```

- [ ] **Step 2: Push**

```bash
git push origin main
```

Expected: push succeeds to `origin/main`.

## Self-review

Spec coverage: covers progressive gates per NT skill, Rust-first V2 cutover, AI lane remaining Python, checker enforcement, tests, reconciliation, commit, and push. Placeholder scan: none. Type consistency: checker/test names use `NT V2 Rust readiness gates` consistently.
