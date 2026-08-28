from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_clean_tree_passes_legacy_labelling_gate() -> None:
    result = subprocess.run(
        [sys.executable, "tools/check_legacy_labelling.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "relative_path, guidance",
    [
        ("skills/nt-example/SKILL.md", "Use cdef and cimport in a .pyx wrapper.\n"),
        ("references/example.md", "Call the removed v1 LegacyApi directly.\n"),
        ("templates/example.md", "Implement this wrapper with cpdef.\n"),
    ],
)
def test_unlabelled_scoped_legacy_guidance_fails(
    tmp_path: Path,
    relative_path: str,
    guidance: str,
) -> None:
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(guidance, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert f"unlabelled legacy/Cython/v1 guidance in {relative_path}" in result.stdout


@pytest.mark.parametrize(
    "guidance",
    [
        "Configure `LiveExecEngineConfig` for the execution engine.\n",
        "Subclass `LiveExecClientConfig` for the venue client.\n",
        "Import the removed `FillModelConfig` helper.\n",
        "```python\nfrom nautilus_trader.backtest.engine import BacktestEngine\n```\n",
        "```python\nfrom nautilus_trader.core.rust.model import FixFn\n```\n",
        "```python\nfrom nautilus_trader.test_kit.debug_helpers import print_raw\n```\n",
        "```python\nfrom nautilus_trader.analysis.statistic import PortfolioAnalyzer\n```\n",
        "```python\nfrom nautilus_trader.model.identifiers import OrderId\n```\n",
    ],
)
def test_unlabelled_removed_v2_symbols_fail(tmp_path: Path, guidance: str) -> None:
    path = tmp_path / "references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text(guidance, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert (
        f"unlabelled removed-v2-symbol guidance in {path.relative_to(tmp_path)}"
        in result.stdout
    )


@pytest.mark.parametrize(
    "guidance",
    [
        "Configure `LiveExecutionEngineConfig` for the execution engine.\n",
        "Subclass `ExecutionClientConfig` for the venue client.\n",
        "```python\nfrom nautilus_trader.backtest import BacktestNode\n```\n",
        "```python\nfrom nautilus_trader.testkit import TestComponentStubs\n```\n",
        "```python\nfrom nautilus_trader.model import OrderId\n```\n",
    ],
)
def test_current_v2_symbols_do_not_fail(tmp_path: Path, guidance: str) -> None:
    path = tmp_path / "references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text(guidance, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout


def test_removed_v2_symbols_pass_with_file_level_label(tmp_path: Path) -> None:
    path = tmp_path / "references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "<!-- NT v2 compatibility note: retained v1 migration/reference-only content; "
        "this whole file is retained as legacy reference. -->\n\n"
        "```python\nfrom nautilus_trader.backtest.engine import BacktestEngine\n```\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout


def test_removed_v2_symbols_pass_with_proximate_label(tmp_path: Path) -> None:
    path = tmp_path / "references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "legacy: v1-only import below retained for migration review\n\n"
        "```python\nfrom nautilus_trader.backtest.models import FillModelConfig\n```\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout


def test_label_above_fence_covers_long_block(tmp_path: Path) -> None:
    path = tmp_path / "references/example.md"
    path.parent.mkdir(parents=True)
    filler = "\n".join(f"# filler line {i}" for i in range(1, 30))
    path.write_text(
        "## Guide\n\n"
        "NT v2 compatibility note: v1 migration reference below.\n\n"
        "```python\n"
        f"{filler}\n"
        "from nautilus_trader.execution.messages import CancelOrder\n"
        "```\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("status", ["Pass", "Blocked"])
def test_readiness_card_does_not_suppress_unlabelled_guidance(
    tmp_path: Path,
    status: str,
) -> None:
    path = tmp_path / "skills/nt-example/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "# Example\n\n"
        "## NT V2 Rust readiness gates\n\n"
        "| Gate | Criterion | Status | Evidence |\n"
        "| --- | --- | --- | --- |\n"
        "| G0 Scope | Rust-first | Pass | evidence |\n"
        f"| G1 Legacy labelling | Label old APIs | {status} | evidence |\n\n"
        "Use v1 LegacyApi directly in current work.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unlabelled legacy/Cython/v1 guidance" in result.stdout


def test_nested_skill_reference_is_in_mandatory_scope(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text("Use cdef and cimport in a .pyx wrapper.\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "skills/nt-example/references/example.md" in result.stdout


def test_migration_note_within_five_lines_passes(tmp_path: Path) -> None:
    path = tmp_path / "templates/example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "legacy: migration/reference-only; prefer Rust/PyO3 for new work.\n"
        "\n"
        "This retained example uses cdef in a historical .pyx wrapper.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "guidance",
    (
        "Use cython for the current adapter.\n",
        "Use the runtime v1 for current work.\n",
        "Use v1-equivalent coverage for current work.\n",
    ),
)
def test_case_and_grammar_variants_of_unlabelled_v1_guidance_fail(
    tmp_path: Path, guidance: str
) -> None:
    path = tmp_path / "skills/nt-example/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(guidance, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1, result.stdout + result.stderr


def test_api_v1_path_does_not_require_a_legacy_label(tmp_path: Path) -> None:
    path = tmp_path / "references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text("See /api/v1/orders for the HTTP endpoint.\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_scan_root_fails_closed(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(missing_root),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "scan root does not exist" in result.stdout


def test_active_docs_and_readme_are_scanned(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/active.md").write_text("Use cdef in new active guidance.\n")
    (tmp_path / "README.md").write_text("Use .pyx for new work.\n")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1
    assert "unlabelled legacy/Cython/v1 guidance" in output
    assert "docs/active.md" in output or "README.md" in output


def test_tracking_history_is_intentionally_excluded(tmp_path: Path) -> None:
    tracking = tmp_path / "docs/tracking"
    tracking.mkdir(parents=True)
    (tracking / "Findings.md").write_text("Historical cdef audit evidence.\n")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
