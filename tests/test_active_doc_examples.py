from __future__ import annotations

import ast
import re
from pathlib import Path

from tools.upstream_baseline import default_upstream_root

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text()


def test_active_serialization_python_fences_parse() -> None:
    text = read("docs/serialization.md")
    fences = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)

    assert fences
    for fence in fences:
        ast.parse(fence)


def test_end_to_end_guide_uses_published_release_lane() -> None:
    text = read("docs/end_to_end_guide.md")
    cargo = re.search(r"```toml\n(.*?)```", text, flags=re.DOTALL)

    assert cargo is not None
    quickstart = (
        default_upstream_root() / "docs/how_to/run_rust_live_trading.md"
    ).read_text()
    for name in ("nautilus-live", "nautilus-okx"):
        dependency = re.search(rf'^{name}\s*=\s*"[^"]+"', quickstart, re.MULTILINE)
        assert dependency is not None
        assert dependency.group(0) in cargo.group(1)
    assert "Verify registry availability" in text
    assert "source-pinned checkout or path dependencies" in text


def test_learning_setup_uses_pinned_upstream_bootstrap() -> None:
    setup = read("skills/nt-learn/curriculum/01-setup.md")
    stage09 = read("skills/nt-learn/curriculum/09-full-rust-trading.md")

    assert "make sync" in setup
    assert "uv sync --all-extras" not in setup
    assert "rustup toolchain install nightly" not in setup
    quickstart = (
        default_upstream_root() / "docs/how_to/run_rust_live_trading.md"
    ).read_text()
    dependency = re.search(r'^nautilus-live\s*=\s*"[^"]+"', quickstart, re.MULTILINE)
    assert dependency is not None
    assert dependency.group(0) in stage09
    assert 'version = "0.62"' not in stage09
