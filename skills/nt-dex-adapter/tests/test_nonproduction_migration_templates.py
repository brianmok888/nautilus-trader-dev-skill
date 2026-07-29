"""Non-production smoke checks for quarantined Python migration templates."""

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("pydantic")

_templates = Path(__file__).parent.parent / "templates"
_legacy_templates = _templates / "legacy_migration"
sys.path.insert(0, str(_templates))


def _load_migration_module(name: str):
    spec = importlib.util.spec_from_file_location(name, _legacy_templates / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize(
    "module_name",
    ("dex_data_client", "dex_exec_client", "dex_factory"),
)
def test_quarantined_migration_template_imports(module_name: str) -> None:
    assert _load_migration_module(module_name) is not None
