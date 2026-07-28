from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_dev_guide_snapshot_sync as snapshot_sync
from tools.check_dev_guide_snapshot_sync import (
    EXPECTED_UPSTREAM_COMMIT,
    compare_snapshot,
    strip_local_metadata,
    upstream_commit,
)


def test_strip_local_metadata_preserves_upstream_body() -> None:
    assert strip_local_metadata("---\nsource_commit: abc\n---\n\n# Python\n") == "# Python\n"


def test_compare_snapshot_reports_changed_missing_and_extra_files(tmp_path: Path) -> None:
    local = tmp_path / "local"
    upstream = tmp_path / "upstream"
    local.mkdir()
    upstream.mkdir()
    (local / "same.md").write_text("---\nsource_commit: abc\n---\nsame\n")
    (upstream / "same.md").write_text("same\n")
    (local / "changed.md").write_text("---\n---\nlocal\n")
    (upstream / "changed.md").write_text("upstream\n")
    (local / "extra.md").write_text("extra\n")
    (upstream / "missing.md").write_text("missing\n")

    result = compare_snapshot(local, upstream)

    assert result.changed == (Path("changed.md"),)
    assert result.extra == (Path("extra.md"),)
    assert result.missing == (Path("missing.md"),)


def test_pinned_upstream_checkout_matches_expected_commit() -> None:
    upstream = snapshot_sync.default_upstream_root()
    assert upstream_commit(upstream) == EXPECTED_UPSTREAM_COMMIT


def test_missing_upstream_checkout_fails_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing-upstream"
    result = subprocess.run(
        [
            sys.executable,
            "tools/check_dev_guide_snapshot_sync.py",
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
