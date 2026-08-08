from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.check_skill_g2_harnesses import assert_expected_upstream
from tools.upstream_baseline import default_upstream_root

_HOST_PYTHON_TESTS = frozenset({"skills/nt-dex-adapter/tests/test_dex_compliance.py"})


def uses_host_python(tests: list[str]) -> bool:
    return bool(tests) and all(
        value.split("::", 1)[0] in _HOST_PYTHON_TESTS for value in tests
    )


def main(argv: list[str] | None = None) -> int:
    """Run repository tests with the Python environment built at the V2 pin."""
    upstream_root = default_upstream_root()
    assert_expected_upstream(upstream_root)
    pinned_python = upstream_root / "python/.venv/bin/python"
    tests = sys.argv[1:] if argv is None else argv
    if not tests:
        raise ValueError("at least one pytest path is required")
    if uses_host_python(tests):
        python = sys.executable
    else:
        if not pinned_python.is_file():
            message = (
                f"pinned NautilusTrader Python environment not found: {pinned_python}; "
                + "run `make sync-v2` in the pinned upstream checkout"
            )
            raise FileNotFoundError(message)
        python = str(pinned_python)
    result = subprocess.run(
        (python, "-m", "pytest", "-q", "-o", "addopts=", *tests),
        cwd=Path(__file__).resolve().parents[1],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
