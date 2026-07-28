from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_rust_trading_reference_sync as rust_sync


def test_rust_trading_references_match_pinned_upstream_examples() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    upstream_root = rust_sync.DEFAULT_UPSTREAM_ROOT

    rust_sync.assert_expected_upstream(upstream_root)
    result = rust_sync.compare_examples(
        repo_root / rust_sync.LOCAL_EXAMPLES,
        upstream_root / rust_sync.UPSTREAM_EXAMPLES,
    )

    assert result.ok, rust_sync.report_sync(result)


def test_compile_command_checks_the_synced_upstream_example_crate() -> None:
    assert rust_sync.CARGO_CHECK_COMMAND == (
        "cargo",
        "check",
        "-p",
        "nautilus-trading",
        "--features",
        "examples,high-precision",
        "--lib",
    )


def test_missing_upstream_checkout_fails_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing-upstream"
    result = subprocess.run(
        [
            sys.executable,
            "tools/check_rust_trading_reference_sync.py",
            "--upstream-root",
            str(missing),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "No such file or directory" in result.stderr or "not a git repository" in result.stderr
