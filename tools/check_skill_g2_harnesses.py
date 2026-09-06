from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.g2_owned_content import (
    OwnedContentError,
    assert_owned_content_tracked,
    harness_content_hash,
)
from tools.upstream_baseline import UPSTREAM_COMMIT, default_upstream_root

EXPECTED_UPSTREAM_COMMIT = UPSTREAM_COMMIT
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SHARED_TRADING_COMMAND = (
    "cargo",
    "check",
    "-p",
    "nautilus-trading",
    "--features",
    "examples,high-precision",
    "--lib",
)


class WorkingDirectory(Enum):
    REPOSITORY = "repository"
    UPSTREAM = "upstream"
    UPSTREAM_PYTHON = "upstream-python"


class RunStatus(Enum):
    PASS = "pass"
    PENDING = "pending"
    BLOCKED = "blocked"


class PythonV2RuntimeError(RuntimeError):
    """Raised when a pinned upstream checkout lacks its required PyO3 runtime."""


@dataclass(frozen=True)
class Step:
    command: tuple[str, ...]
    cwd: WorkingDirectory = WorkingDirectory.REPOSITORY


@dataclass(frozen=True)
class Harness:
    skill: str
    scope: str
    summary: str
    allowed_tokens: tuple[str, ...]
    steps: tuple[Step, ...]
    owned_paths: tuple[Path, ...] = ()
    evidence_file: Path | None = None


@dataclass(frozen=True)
class RunResult:
    skill: str
    status: RunStatus
    failed_step: Step | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status is RunStatus.PASS


def upstream_step(*command: str) -> Step:
    return Step(command=command, cwd=WorkingDirectory.UPSTREAM)


def upstream_python_step(*command: str) -> Step:
    return Step(command=command, cwd=WorkingDirectory.UPSTREAM_PYTHON)


def repository_step(*command: str) -> Step:
    return Step(command=command)


PYTHON = sys.executable

HARNESSES: dict[str, Harness] = {
    "nt": Harness(
        skill="nt",
        scope="repository:router-and-readiness-dispatch",
        summary="Validate router coverage and every subordinate skill G2 manifest entry",
        allowed_tokens=(
            "test_dev_guide_sync.py",
            "test_v2_guidance_hardening.py",
            "test_v2_strategy_routing_scope.py",
            "test_v2_dex_template_policy.py",
            "test_v2_inventory_pins_versions.py",
            "test_v2_current_develop_overlays.py",
            "--check-card-declarations",
        ),
        steps=(
            repository_step(
                PYTHON,
                "-m",
                "pytest",
                "-q",
                "tests/test_dev_guide_sync.py",
                "tests/test_v2_guidance_hardening.py",
                "tests/test_v2_strategy_routing_scope.py",
                "tests/test_v2_dex_template_policy.py",
                "tests/test_v2_inventory_pins_versions.py",
                "tests/test_v2_current_develop_overlays.py",
            ),
            repository_step(
                PYTHON,
                "tools/check_skill_g2_harnesses.py",
                "--check-card-declarations",
            ),
        ),
        owned_paths=(
            Path("skills/nt/SKILL.md"),
            Path("tests/test_dev_guide_sync.py"),
            Path("tests/test_v2_guidance_hardening.py"),
            Path("tests/test_v2_strategy_routing_scope.py"),
            Path("tests/test_v2_dex_template_policy.py"),
            Path("tests/test_v2_inventory_pins_versions.py"),
            Path("tests/test_v2_current_develop_overlays.py"),
            Path("tools/check_skill_g2_harnesses.py"),
        ),
        evidence_file=Path("references/g2-evidence/nt.json"),
    ),
    "nt-adapters": Harness(
        skill="nt-adapters",
        scope="upstream:crates/adapters/sandbox-and-bitmex-examples",
        summary="Compile credentialless adapter contracts and representative data/exec examples",
        allowed_tokens=("nautilus-sandbox", "nautilus-bitmex"),
        steps=(
            upstream_step("cargo", "check", "-p", "nautilus-sandbox", "--lib"),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-bitmex",
                "--examples",
                "--features",
                "examples",
            ),
        ),
        owned_paths=(Path("skills/nt-adapters/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-adapters.json"),
    ),
    "nt-architect": Harness(
        skill="nt-architect",
        scope="upstream:cross-boundary-core-data-trading-backtest",
        summary="Compile the representative architecture path across component boundaries",
        allowed_tokens=(
            "nautilus-common",
            "nautilus-data",
            "nautilus-trading",
            "nautilus-backtest",
        ),
        steps=(
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-common",
                "-p",
                "nautilus-data",
                "-p",
                "nautilus-trading",
                "-p",
                "nautilus-backtest",
                "--lib",
            ),
        ),
        owned_paths=(Path("skills/nt-architect/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-architect.json"),
    ),
    "nt-backtest": Harness(
        skill="nt-backtest",
        scope="upstream:crates/backtest-examples",
        summary="Compile all Rust backtest examples against V2",
        allowed_tokens=("nautilus-backtest",),
        steps=(
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-backtest",
                "--examples",
                "--features",
                "examples",
            ),
        ),
        owned_paths=(Path("skills/nt-backtest/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-backtest.json"),
    ),
    "nt-data": Harness(
        skill="nt-data",
        scope="upstream:crates/data-persistence-serialization",
        summary="Compile data-engine, catalog persistence, and serialization owners",
        allowed_tokens=(
            "nautilus-data",
            "nautilus-persistence",
            "nautilus-serialization",
        ),
        steps=(
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-data",
                "-p",
                "nautilus-persistence",
                "-p",
                "nautilus-serialization",
                "--lib",
            ),
        ),
        owned_paths=(Path("skills/nt-data/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-data.json"),
    ),
    "nt-dev": Harness(
        skill="nt-dev",
        scope="upstream:rust-format-core-ffi-pyo3",
        summary="Validate formatting plus the core, FFI, and PyO3 development surface",
        allowed_tokens=("cargo", "nautilus-core", "nautilus-model", "nautilus-pyo3"),
        steps=(
            upstream_step("cargo", "fmt", "--all", "--", "--check"),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-core",
                "-p",
                "nautilus-model",
                "-p",
                "nautilus-pyo3",
                "--features",
                "python,ffi,high-precision",
                "--lib",
            ),
        ),
        owned_paths=(Path("skills/nt-dev/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-dev.json"),
    ),
    "nt-dex-adapter": Harness(
        skill="nt-dex-adapter",
        scope="upstream:hyperliquid-and-blockchain-adapters",
        summary="Run local DEX template tests and compile Rust networking/signing surfaces",
        allowed_tokens=(
            "test_dex_compliance.py",
            "nautilus-hyperliquid",
            "nautilus-blockchain",
        ),
        steps=(
            repository_step(
                PYTHON,
                "tools/run_pinned_v2_pytest.py",
                "skills/nt-dex-adapter/tests/test_dex_compliance.py",
            ),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-hyperliquid",
                "--examples",
                "--features",
                "examples",
            ),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-blockchain",
                "--examples",
                "--features",
                "hypersync",
            ),
        ),
        owned_paths=(
            Path("skills/nt-dex-adapter/SKILL.md"),
            Path("skills/nt-dex-adapter/migration_reference/python/templates"),
            Path("skills/nt-dex-adapter/tests"),
        ),
        evidence_file=Path("references/g2-evidence/nt-dex-adapter.json"),
    ),
    "nt-implement": Harness(
        skill="nt-implement",
        scope="repository:fixed-point-schema-plus-upstream-owners",
        summary="Validate implementation templates and compile representative Rust component owners",
        allowed_tokens=(
            "test_capnp_schema_precision.py",
            "nautilus-common",
            "nautilus-indicators",
            "nautilus-trading",
            "nautilus-backtest",
        ),
        steps=(
            repository_step(
                PYTHON,
                "-m",
                "pytest",
                "-q",
                "tests/test_capnp_schema_precision.py",
            ),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-common",
                "-p",
                "nautilus-indicators",
                "-p",
                "nautilus-trading",
                "-p",
                "nautilus-backtest",
                "--lib",
            ),
        ),
        owned_paths=(
            Path("skills/nt-implement/SKILL.md"),
            Path("skills/nt-implement/templates"),
            Path("tests/test_capnp_schema_precision.py"),
            Path("tests/test_skill_g2_harnesses.py"),
        ),
        evidence_file=Path("references/g2-evidence/nt-implement.json"),
    ),
    "nt-learn": Harness(
        skill="nt-learn",
        scope="repository:curriculum-commands-and-rust-examples",
        summary="Validate curriculum commands and the Rust examples learners are taught",
        allowed_tokens=(
            "test_dev_guide_sync.py",
            "test_template_classification.py",
            "nautilus-backtest",
        ),
        steps=(
            repository_step(
                PYTHON,
                "-m",
                "pytest",
                "-q",
                "tests/test_dev_guide_sync.py",
                "tests/test_template_classification.py",
            ),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-backtest",
                "--example",
                "engine-ema-cross",
                "--features",
                "examples",
            ),
        ),
        owned_paths=(
            Path("skills/nt-learn/SKILL.md"),
            Path("skills/nt-learn/curriculum"),
            Path("skills/nt-learn/migration_reference"),
            Path("tests/test_dev_guide_sync.py"),
            Path("tests/test_template_classification.py"),
            Path("tests/test_rust_lane_cutover.py"),
        ),
        evidence_file=Path("references/g2-evidence/nt-learn.json"),
    ),
    "nt-model": Harness(
        skill="nt-model",
        scope="upstream:crates/model-all-targets",
        summary="Compile model types, instruments, fixed-point objects, and benchmark targets",
        allowed_tokens=("nautilus-model",),
        steps=(
            upstream_step("cargo", "check", "-p", "nautilus-model", "--all-targets"),
        ),
        owned_paths=(Path("skills/nt-model/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-model.json"),
    ),
    "nt-live": Harness(
        skill="nt-live",
        scope="upstream:live-node-and-rust-live-example",
        summary="Compile LiveNode and the canonical Rust live trading example",
        allowed_tokens=("nautilus-live", "bitmex-grid-mm"),
        steps=(
            upstream_step("cargo", "check", "-p", "nautilus-live", "--lib"),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-bitmex",
                "--example",
                "bitmex-grid-mm",
                "--features",
                "examples",
            ),
        ),
        owned_paths=(
            Path("skills/nt-live/SKILL.md"),
            Path("skills/nt-live/references"),
        ),
        evidence_file=Path("references/g2-evidence/nt-live.json"),
    ),
    "nt-review": Harness(
        skill="nt-review",
        scope="repository:review-policy-plus-upstream-safety-owners",
        summary="Run review-policy gates and compile Rust safety/binding owners",
        allowed_tokens=(
            "test_dev_guide_sync.py",
            "test_template_classification.py",
            "test_v2_guidance_hardening.py",
            "test_v2_strategy_routing_scope.py",
            "test_v2_dex_template_policy.py",
            "test_v2_inventory_pins_versions.py",
            "test_v2_current_develop_overlays.py",
            "nautilus-core",
            "nautilus-model",
            "nautilus-pyo3",
        ),
        steps=(
            repository_step(
                PYTHON,
                "-m",
                "pytest",
                "-q",
                "tests/test_dev_guide_sync.py",
                "tests/test_template_classification.py",
                "tests/test_v2_guidance_hardening.py",
                "tests/test_v2_strategy_routing_scope.py",
                "tests/test_v2_dex_template_policy.py",
                "tests/test_v2_inventory_pins_versions.py",
                "tests/test_v2_current_develop_overlays.py",
            ),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-core",
                "-p",
                "nautilus-model",
                "-p",
                "nautilus-pyo3",
                "--features",
                "python,ffi,high-precision",
                "--all-targets",
            ),
        ),
        owned_paths=(
            Path("skills/nt-review/SKILL.md"),
            Path("tests/test_dev_guide_sync.py"),
            Path("tests/test_template_classification.py"),
            Path("tests/test_v2_guidance_hardening.py"),
            Path("tests/test_v2_strategy_routing_scope.py"),
            Path("tests/test_v2_dex_template_policy.py"),
            Path("tests/test_v2_inventory_pins_versions.py"),
            Path("tests/test_v2_current_develop_overlays.py"),
        ),
        evidence_file=Path("references/g2-evidence/nt-review.json"),
    ),
    "nt-signals": Harness(
        skill="nt-signals",
        scope="upstream:analysis-and-indicators-owners",
        summary="Compile the pinned V2 Rust analysis and indicator owners",
        allowed_tokens=("crates/analysis/Cargo.toml", "nautilus-indicators"),
        steps=(
            upstream_step(
                "cargo",
                "check",
                "--manifest-path",
                "crates/analysis/Cargo.toml",
                "--all-targets",
            ),
            upstream_step(
                "cargo", "check", "-p", "nautilus-indicators", "--all-targets"
            ),
        ),
        owned_paths=(Path("skills/nt-signals/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-signals.json"),
    ),
    "nt-strategy-builder": Harness(
        skill="nt-strategy-builder",
        scope="repository:python-v2-strategy-templates",
        summary="Validate migration-only Python strategy/configuration references against current V2 APIs",
        allowed_tokens=(
            "skills/nt-strategy-builder/templates",
            "tests/test_strategy_builder_v2_contract.py",
            "test_backtest.py",
            "test_live_configs.py",
        ),
        steps=(
            repository_step(
                PYTHON,
                "tools/run_pinned_v2_pytest.py",
                "tests/test_strategy_builder_v2_contract.py",
            ),
            upstream_python_step(
                "./.venv/bin/python",
                "-m",
                "pytest",
                "-q",
                "tests/acceptance/test_backtest.py",
                "tests/unit/live/test_live_configs.py",
            ),
        ),
        owned_paths=(
            Path("skills/nt-strategy-builder/SKILL.md"),
            Path("skills/nt-strategy-builder/templates"),
            Path("skills/nt-strategy-builder/tests"),
        ),
        evidence_file=Path("references/g2-evidence/nt-strategy-builder.json"),
    ),
    "nt-strategy-builder-rust": Harness(
        skill="nt-strategy-builder-rust",
        scope="repository:compile-extracted-rust-strategy-skill-example",
        summary="Extract and compile the Rust strategy skill example against pinned V2",
        allowed_tokens=("test_rust_strategy_skill_example_compiles",),
        steps=(
            repository_step(
                PYTHON,
                "-m",
                "pytest",
                "-q",
                "tests/test_rust_first_end_to_end.py::test_rust_strategy_skill_example_compiles_against_pinned_upstream",
            ),
        ),
        owned_paths=(
            Path("skills/nt-strategy-builder-rust/SKILL.md"),
            Path("tests/test_rust_first_end_to_end.py"),
        ),
        evidence_file=Path("references/g2-evidence/nt-strategy-builder-rust.json"),
    ),
    "nt-testing": Harness(
        skill="nt-testing",
        scope="upstream:testkit-data-execution-test-targets",
        summary="Run V2 DataTester/ExecTester tests and compile their node examples",
        allowed_tokens=("nautilus-testkit", "nautilus-derive"),
        steps=(
            upstream_step(
                "cargo",
                "test",
                "-p",
                "nautilus-testkit",
                "--lib",
            ),
            upstream_step(
                "cargo",
                "check",
                "-p",
                "nautilus-derive",
                "--examples",
                "--features",
                "examples",
            ),
        ),
        owned_paths=(Path("skills/nt-testing/SKILL.md"),),
        evidence_file=Path("references/g2-evidence/nt-testing.json"),
    ),
    "nt-trading": Harness(
        skill="nt-trading",
        scope="repository:rust-trading-reference-sync-and-compile",
        summary="Validate and compile the mirrored canonical Rust trading examples",
        allowed_tokens=("test_rust_trading_reference_sync.py",),
        steps=(
            repository_step(
                PYTHON,
                "-m",
                "pytest",
                "-q",
                "tests/test_rust_trading_reference_sync.py",
            ),
        ),
        owned_paths=(
            Path("skills/nt-trading/SKILL.md"),
            Path("skills/nt-trading/references/examples/rust_trading"),
            Path("tests/test_rust_trading_reference_sync.py"),
        ),
        evidence_file=Path("references/g2-evidence/nt-trading.json"),
    ),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def upstream_commit(upstream_root: Path) -> str:
    result = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=upstream_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def upstream_is_clean(upstream_root: Path) -> bool:
    result = subprocess.run(
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        cwd=upstream_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return not result.stdout.strip()


def assert_expected_upstream(
    upstream_root: Path, *, expected_commit: str = EXPECTED_UPSTREAM_COMMIT
) -> None:
    actual = upstream_commit(upstream_root)
    if actual != expected_commit:
        raise RuntimeError(
            f"Upstream checkout is {actual}, expected {expected_commit}: {upstream_root}"
        )
    if not upstream_is_clean(upstream_root):
        raise RuntimeError(
            f"Upstream checkout has uncommitted changes: {upstream_root}"
        )


def command_matches_scope(
    command: tuple[str, ...], allowed_tokens: tuple[str, ...]
) -> bool:
    return any(token in argument for token in allowed_tokens for argument in command)


def validate_harnesses(
    harnesses: Mapping[str, Harness],
    *,
    expected_skills: set[str] | None = None,
    root: Path | None = None,
) -> list[str]:
    validation_root = repo_root() if root is None else root
    expected = set(HARNESSES) if expected_skills is None else expected_skills
    actual = set(harnesses)
    errors = [f"missing G2 harness: {skill}" for skill in sorted(expected - actual)]
    errors.extend(f"unknown G2 harness: {skill}" for skill in sorted(actual - expected))

    scopes: dict[str, str] = {}
    for key, harness in sorted(harnesses.items()):
        if harness.skill != key:
            errors.append(
                f"{key} manifest key does not match harness skill {harness.skill}"
            )
        if not harness.steps:
            errors.append(f"{key} has no validation steps")
        if not harness.allowed_tokens:
            errors.append(f"{key} has no machine-checkable scope tokens")
        if not harness.owned_paths:
            errors.append(f"{key} has no owned paths")
        try:
            harness_content_hash(validation_root, harness)
        except OwnedContentError as exc:
            errors.append(f"{key} owned content is invalid: {exc}")
        required_skill_path = Path("skills") / key / "SKILL.md"
        if required_skill_path not in harness.owned_paths:
            errors.append(f"{key} owned paths omit {required_skill_path.as_posix()}")
        for owned_path in harness.owned_paths:
            if not (validation_root / owned_path).exists():
                errors.append(
                    f"{key} owned path does not exist: {owned_path.as_posix()}"
                )
            evidence_file = harness.evidence_file
            if evidence_file is not None and (
                owned_path == evidence_file or owned_path in evidence_file.parents
            ):
                errors.append(f"{key} evidence artifact is included in owned content")
        previous = scopes.get(harness.scope)
        if previous is not None:
            errors.append(f"duplicate G2 scope {harness.scope}: {previous}, {key}")
        scopes[harness.scope] = key
        for step in harness.steps:
            if not command_matches_scope(step.command, harness.allowed_tokens):
                errors.append(f"{key} command falls outside its declared scope")
        if key not in {"nt", "nt-architect", "nt-implement", "nt-learn", "nt-review"}:
            for step in harness.steps:
                if step.command == SHARED_TRADING_COMMAND:
                    errors.append(
                        f"{key} reuses the unrelated shared nautilus-trading compile"
                    )
    return errors


def plan_harnesses(skills: set[str] | None = None) -> list[Harness]:
    selected = set(HARNESSES) if skills is None else skills
    unknown = selected - set(HARNESSES)
    if unknown:
        raise ValueError(f"unknown requested skill: {min(unknown)}")
    return [HARNESSES[skill] for skill in sorted(selected)]


Runner = Callable[..., subprocess.CompletedProcess[str]]


def assert_python_v2_runtime(
    upstream_root: Path, *, runner: Runner = subprocess.run
) -> None:
    python_root = upstream_root / "python"
    interpreter = upstream_root / "python/.venv/bin/python"
    try:
        result = runner(
            (str(interpreter), "-c", "import nautilus_trader._libnautilus.common"),
            cwd=python_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise PythonV2RuntimeError(
            "nt-strategy-builder G2 is blocked: the pinned upstream Python v2 runtime is "
            "not prepared; missing nautilus_trader._libnautilus.common. Prepare a separate "
            f"writable checkout at commit {EXPECTED_UPSTREAM_COMMIT} with `make sync && make build-debug`, "
            "then pass it with `--upstream-root`. Do not build or install into the source-read-only "
            "pinned cache."
        ) from exc
    if result.returncode != 0:
        raise PythonV2RuntimeError(
            "nt-strategy-builder G2 is blocked: the pinned upstream Python v2 runtime is "
            "not prepared; missing nautilus_trader._libnautilus.common. Prepare a separate "
            f"writable checkout at commit {EXPECTED_UPSTREAM_COMMIT} with `make sync && make build-debug`, "
            "then pass it with `--upstream-root`. Do not build or install into the source-read-only "
            "pinned cache."
        )


def run_harness(
    harness: Harness,
    *,
    repo_root: Path,
    upstream_root: Path,
    runner: Runner = subprocess.run,
) -> RunResult:
    evidence_steps: list[dict[str, object]] = []
    if harness.skill == "nt-strategy-builder":
        try:
            assert_python_v2_runtime(upstream_root, runner=runner)
        except PythonV2RuntimeError as exc:
            return RunResult(
                skill=harness.skill, status=RunStatus.BLOCKED, error=str(exc)
            )
    for step in harness.steps:
        cwd = (
            repo_root
            if step.cwd is WorkingDirectory.REPOSITORY
            else upstream_root / "python"
            if step.cwd is WorkingDirectory.UPSTREAM_PYTHON
            else upstream_root
        )
        started = datetime.now(UTC)
        try:
            result = runner(step.command, cwd=cwd, check=False, text=True)
        except FileNotFoundError:
            return RunResult(
                skill=harness.skill,
                status=RunStatus.BLOCKED,
                failed_step=step,
            )
        evidence_steps.append(
            {
                "command": list(step.command),
                "cwd": step.cwd.value,
                "duration_seconds": (datetime.now(UTC) - started).total_seconds(),
                "returncode": result.returncode,
            }
        )
        if result.returncode != 0:
            return RunResult(
                skill=harness.skill,
                status=RunStatus.BLOCKED,
                failed_step=step,
            )
    write_evidence(
        harness, root=repo_root, upstream_root=upstream_root, results=evidence_steps
    )
    status = (
        RunStatus.PENDING
        if harness.skill == "nt-implement" and shutil.which("capnp") is None
        else RunStatus.PASS
    )
    return RunResult(skill=harness.skill, status=status)


def evidence_command(skill: str) -> str:
    return f"uv run python tools/check_skill_g2_harnesses.py --execute --skill {skill}"


def readiness_rows(text: str) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        if not line.startswith(tuple(f"| G{index} " for index in range(8))):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        rows[cells[0].split(maxsplit=1)[0]] = (cells[2], cells[3])
    return rows


def validate_readiness_cards(
    root: Path,
    harnesses: Mapping[str, Harness],
    *,
    require_evidence: bool = True,
    excluded_evidence: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    excluded = set() if excluded_evidence is None else excluded_evidence
    for skill in sorted(harnesses):
        path = root / "skills" / skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing readiness card: {path}")
            continue
        text = path.read_text()
        gate_rows = [
            line
            for line in text.splitlines()
            if line.startswith(tuple(f"| G{index} " for index in range(8)))
        ]
        parsed_rows = readiness_rows(text)
        gate_ids: list[str] = []
        for row in gate_rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if cells:
                gate_ids.append(cells[0].split(maxsplit=1)[0])
            if len(cells) != 4 or cells[2] != "Pass":
                continue
            gate_id = cells[0].split(maxsplit=1)[0]
            if "tools/check_skill_g2_harnesses.py --check-cards" in cells[3]:
                errors.append(
                    f"{skill} {gate_id} readiness row uses the card validator as evidence"
                )
        expected_gate_ids = {f"G{index}" for index in range(8)}
        if set(gate_ids) != expected_gate_ids or len(gate_ids) != len(
            expected_gate_ids
        ):
            errors.append(
                f"{skill} readiness card must declare exactly one row for each G0-G7 gate"
            )
        for gate_id, (gate_status, evidence) in parsed_rows.items():
            if gate_status not in {"Pass", "Pending", "Blocked"}:
                errors.append(f"{skill} {gate_id} readiness row has an invalid status")
            if not evidence or evidence == "—":
                errors.append(f"{skill} {gate_id} readiness row lacks evidence")
        g2_rows = [line for line in gate_rows if line.startswith("| G2 ")]
        if len(g2_rows) != 1:
            errors.append(f"{skill} must contain exactly one G2 readiness row")
            continue
        row = g2_rows[0]
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        status = cells[2] if len(cells) == 4 else ""
        if status not in {"Pass", "Pending", "Blocked"}:
            errors.append(f"{skill} G2 readiness row has an invalid status")
        if f"`{evidence_command(skill)}`" not in row:
            errors.append(
                f"{skill} G2 readiness row lacks its targeted harness command"
            )
        evidence_file = harnesses[skill].evidence_file
        if evidence_file is None:
            errors.append(f"{skill} has no durable evidence artifact configured")
            continue
        if f"`{evidence_file.as_posix()}`" not in row:
            errors.append(
                f"{skill} G2 readiness row lacks its durable evidence artifact"
            )
        if not require_evidence or skill in excluded:
            continue
        evidence_path = root / evidence_file
        if not evidence_path.is_file():
            errors.append(f"{skill} durable evidence artifact is missing")
            continue
        try:
            payload = json.loads(evidence_path.read_text())
        except (OSError, json.JSONDecodeError):
            errors.append(f"{skill} durable evidence artifact is not valid JSON")
            continue
        if payload.get("schema_version") != 2:
            errors.append(f"{skill} durable evidence has an unsupported schema")
        if (
            payload.get("skill") != skill
            or payload.get("scope") != harnesses[skill].scope
        ):
            errors.append(f"{skill} durable evidence does not match its harness")
        evidence_status = payload.get("status")
        if evidence_status not in {"pass", "pending", "blocked"}:
            errors.append(f"{skill} durable evidence has an invalid status")
        if status == "Pass" and evidence_status != "pass":
            errors.append(f"{skill} G2 readiness Pass lacks passing durable evidence")
        if status == "Pending" and evidence_status != "pending":
            errors.append(
                f"{skill} G2 readiness Pending lacks pending durable evidence"
            )
        if status == "Blocked" and evidence_status != "blocked":
            errors.append(
                f"{skill} G2 readiness Blocked lacks blocked durable evidence"
            )
        if evidence_status == "pending" and not payload.get("pending_reason"):
            errors.append(f"{skill} pending durable evidence lacks a reason")
        if evidence_status == "blocked" and not payload.get("blocked_reason"):
            errors.append(f"{skill} blocked durable evidence lacks a reason")
        if payload.get("upstream_commit") != EXPECTED_UPSTREAM_COMMIT:
            errors.append(
                f"{skill} durable evidence does not match the pinned upstream"
            )
        upstream_clean = payload.get("upstream_clean")
        if type(upstream_clean) is not bool:
            errors.append(f"{skill} durable evidence upstream_clean must be a boolean")
        elif not upstream_clean:
            errors.append(
                f"{skill} durable evidence was not produced from a clean upstream"
            )
        verified_at = payload.get("verified_at")
        try:
            timestamp = (
                datetime.fromisoformat(verified_at)
                if isinstance(verified_at, str)
                else None
            )
        except ValueError:
            timestamp = None
        if timestamp is None or timestamp.tzinfo is None:
            errors.append(
                f"{skill} durable evidence verified_at must be a timezone-aware ISO-8601 timestamp"
            )
        if "repository_commit" in payload:
            errors.append(f"{skill} durable evidence uses self-referential provenance")
        if payload.get("owned_content_sha256") != harness_content_hash(
            root, harnesses[skill]
        ):
            errors.append(
                f"{skill} durable evidence does not match owned skill content"
            )
        steps = payload.get("steps")
        if not isinstance(steps, list) or len(steps) != len(harnesses[skill].steps):
            errors.append(f"{skill} durable evidence has incomplete steps")
        else:
            for step in steps:
                if not isinstance(step, dict):
                    continue
                returncode = step.get("returncode")
                if type(returncode) is not int:
                    errors.append(
                        f"{skill} durable evidence returncode must be an integer"
                    )
                elif returncode != 0:
                    errors.append(f"{skill} durable evidence contains a failed step")
                duration = step.get("duration_seconds")
                if (
                    isinstance(duration, bool)
                    or not isinstance(duration, (int, float))
                    or not math.isfinite(duration)
                    or duration < 0
                ):
                    errors.append(
                        f"{skill} durable evidence duration_seconds must be a nonnegative number"
                    )
            recorded = [
                (step.get("command"), step.get("cwd"))
                for step in steps
                if isinstance(step, dict)
            ]
            expected = [
                (list(step.command), step.cwd.value) for step in harnesses[skill].steps
            ]
            if recorded != expected:
                errors.append(
                    f"{skill} durable evidence commands do not match its harness"
                )
    return errors


def write_evidence(
    harness: Harness,
    *,
    root: Path,
    upstream_root: Path,
    results: list[dict[str, object]],
) -> None:
    if harness.evidence_file is None:
        return
    destination = root / harness.evidence_file
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "skill": harness.skill,
        "scope": harness.scope,
        "owned_content_sha256": harness_content_hash(root, harness),
        "upstream_commit": upstream_commit(upstream_root),
        "upstream_clean": upstream_is_clean(upstream_root),
        "verified_at": datetime.now(UTC).isoformat(),
        "steps": results,
    }
    if harness.skill == "nt-implement" and shutil.which("capnp") is None:
        payload["status"] = "pending"
        payload["pending_reason"] = "capnp executable unavailable"
    else:
        payload["status"] = "pass"
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def format_step(step: Step) -> str:
    prefix = "[upstream]" if step.cwd is WorkingDirectory.UPSTREAM else "[repository]"
    return f"{prefix} {' '.join(step.command)}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run domain-scoped NT V2 G2 validation harnesses for skill readiness cards."
    )
    parser.add_argument("--upstream-root", type=Path, default=default_upstream_root())
    parser.add_argument("--skill", action="append", choices=sorted(HARNESSES))
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--check-cards", action="store_true")
    parser.add_argument("--check-card-declarations", action="store_true")
    parser.add_argument(
        "--exclude-evidence", action="append", choices=sorted(HARNESSES)
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    errors = validate_harnesses(HARNESSES)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    if args.list:
        print("\n".join(sorted(HARNESSES)))
        return 0

    try:
        plan = plan_harnesses(set(args.skill) if args.skill else None)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    if args.check_cards or args.check_card_declarations:
        card_errors = validate_readiness_cards(
            repo_root(),
            HARNESSES,
            require_evidence=args.check_cards,
            excluded_evidence=set(args.exclude_evidence or ()),
        )
        if card_errors:
            print("\n".join(card_errors), file=sys.stderr)
            return 1

    if args.dry_run or not args.execute:
        for harness in plan:
            print(f"{harness.skill}: {harness.summary}")
            for step in harness.steps:
                print(f"  {format_step(step)}")
        return 0

    try:
        assert_expected_upstream(args.upstream_root)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1

    for harness in plan:
        try:
            assert_owned_content_tracked(repo_root(), harness)
        except (OwnedContentError, subprocess.CalledProcessError) as exc:
            print(exc, file=sys.stderr)
            return 1
        print(f"==> {harness.skill}: {harness.summary}", flush=True)
        result = run_harness(
            harness,
            repo_root=repo_root(),
            upstream_root=args.upstream_root,
        )
        if result.status is RunStatus.BLOCKED:
            if result.error is not None:
                print(result.error, file=sys.stderr)
            else:
                assert result.failed_step is not None
                print(
                    f"{harness.skill} failed: {format_step(result.failed_step)}",
                    file=sys.stderr,
                )
            return 1
        print(f"{result.status.value.upper()} {harness.skill}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
