from __future__ import annotations

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
