from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text()


def test_active_serialization_python_fences_parse() -> None:
    text = read("docs/serialization.md")
    fences = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)

    assert fences
    for fence in fences:
        ast.parse(fence)


def test_end_to_end_guide_uses_resolvable_release_lane() -> None:
    text = read("docs/end_to_end_guide.md")
    cargo = re.search(r"```toml\n(.*?)```", text, flags=re.DOTALL)

    assert cargo is not None
    assert 'nautilus-live = "0.62"' in cargo.group(1)
    assert 'nautilus-okx = "0.62"' in cargo.group(1)
    assert 'nautilus-live = "0.63.0"' not in cargo.group(1)


def test_learning_setup_uses_pinned_upstream_bootstrap() -> None:
    setup = read("skills/nt-learn/curriculum/01-setup.md")
    stage09 = read("skills/nt-learn/curriculum/09-full-rust-trading.md")

    assert "make sync" in setup
    assert "uv sync --all-extras" not in setup
    assert "rustup toolchain install nightly" not in setup
    assert 'nautilus-live = "0.62"' in stage09
    assert 'version = "0.61"' not in stage09
