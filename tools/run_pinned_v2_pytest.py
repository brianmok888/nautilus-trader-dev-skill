from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.check_skill_g2_harnesses import assert_expected_upstream
from tools.upstream_baseline import default_upstream_root


def main(argv: list[str] | None = None) -> int:
    """Run repository tests with the Python environment built at the V2 pin."""
    upstream_root = default_upstream_root()
    assert_expected_upstream(upstream_root)
    python = upstream_root / "python/.venv/bin/python"
    tests = sys.argv[1:] if argv is None else argv
    if not tests:
        raise ValueError("at least one pytest path is required")
    result = subprocess.run(
        (str(python), "-m", "pytest", "-q", *tests),
        cwd=Path(__file__).resolve().parents[1],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
