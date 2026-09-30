from __future__ import annotations

import subprocess
from pathlib import Path

from tools.upstream_baseline import UPSTREAM_COMMIT, default_upstream_root

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_pyo3_custom_data_injection_is_in_current_pin() -> None:
    result = subprocess.run(
        ["git", "-C", str(default_upstream_root()), "merge-base", "--is-ancestor",
         "998005124e298e9b0c2f6c60be21e581f3426da1", UPSTREAM_COMMIT],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_rust_state_persistence_is_in_current_pin() -> None:
    result = subprocess.run(
        ["git", "-C", str(default_upstream_root()), "merge-base", "--is-ancestor",
         "9a9e5fe7b762410229b380d5af92d32c13169c3a", UPSTREAM_COMMIT],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_state_guidance_distinguishes_backtest_and_live_shutdown_paths() -> None:
    live = read("skills/nt-live/SKILL.md")
    trading = read("skills/nt-trading/SKILL.md")

    assert "after residual event processing" in live
    assert "before cache teardown" in live
    assert "backtest and live" in trading
    assert "load before component startup" in trading
    assert "save once during shutdown" in trading
