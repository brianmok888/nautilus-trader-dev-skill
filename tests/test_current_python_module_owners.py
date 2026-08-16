from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_active_tardis_examples_use_public_adapter_exports() -> None:
    copies = (
        "references/integrations/tardis.md",
        "skills/nt-adapters/references/integrations/tardis.md",
        "skills/nt-data/references/guides/tardis.md",
    )
    for relative in copies:
        text = _read(relative)
        assert "nautilus_pyo3.run_tardis_machine_replay" not in text
        assert "nautilus_pyo3.TardisHttpClient" not in text
        assert "from nautilus_trader.adapters.tardis import" in text
        assert "http_client.instrument(" not in text
        assert "http_client.instruments(" in text


def test_active_serialization_and_tracing_examples_use_current_owners() -> None:
    serialization = _read("skills/nt-data/references/guides/serialization_patterns.md")
    assert "nautilus_pyo3.PRECISION_BYTES" not in serialization
    assert "nautilus_pyo3.quotes_to_arrow_record_batch_bytes" not in serialization
    assert "from nautilus_trader.model import PRECISION_BYTES" in serialization
    assert "from nautilus_trader.serialization import" in serialization

    copies = (
        "references/concepts/logging.md",
        "skills/nt-architect/references/concepts/logging.md",
        "skills/nt-implement/references/concepts/logging.md",
        "skills/nt-live/references/concepts/logging.md",
        "skills/nt-review/references/concepts/logging.md",
    )
    for relative in copies:
        text = _read(relative)
        assert "nautilus_pyo3.init_tracing()" not in text
        assert "from nautilus_trader.common import init_tracing" in text
