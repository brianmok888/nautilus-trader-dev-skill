from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
    upstream = Path("/tmp/nautilus_trader_upstream_audit_20260728")
    if not upstream.exists():
        pytest.skip("pinned upstream checkout is not available")
    assert upstream_commit(upstream) == EXPECTED_UPSTREAM_COMMIT
