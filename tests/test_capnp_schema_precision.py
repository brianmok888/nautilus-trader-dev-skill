from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPOSITORY_ROOT / "skills/nt-implement/templates/capnp_schema.capnp"


def _schema_text() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _struct_body(schema: str, name: str) -> str:
    match = re.search(rf"struct\s+{re.escape(name)}\s*\{{(?P<body>.*?)\n\}}", schema, re.DOTALL)
    assert match is not None, f"missing struct {name}"
    return match.group("body")


def _assert_field(body: str, name: str, ordinal: int, capnp_type: str) -> None:
    declaration = rf"^\s*{re.escape(name)}\s+@{ordinal}\s+:{re.escape(capnp_type)}\s*;"
    assert re.search(declaration, body, re.MULTILINE), (
        f"missing {name} @{ordinal} :{capnp_type}"
    )


def test_trading_values_use_upstream_fixed_point_shapes() -> None:
    schema = _schema_text()
    signed_raw = _struct_body(schema, "Int128")
    unsigned_raw = _struct_body(schema, "UInt128")
    signal = _struct_body(schema, "TradingSignal")
    market_data = _struct_body(schema, "CustomMarketData")

    _assert_field(signed_raw, "lo", 0, "UInt64")
    _assert_field(signed_raw, "hi", 1, "UInt64")
    _assert_field(unsigned_raw, "lo", 0, "UInt64")
    _assert_field(unsigned_raw, "hi", 1, "UInt64")
    _assert_field(signal, "valueRaw", 2, "Int128")
    _assert_field(signal, "valuePrecision", 5, "UInt8")
    _assert_field(market_data, "priceRaw", 1, "Int128")
    _assert_field(market_data, "quantityRaw", 2, "UInt128")
    _assert_field(market_data, "pricePrecision", 4, "UInt8")
    _assert_field(market_data, "quantityPrecision", 5, "UInt8")
    assert "Float64" not in signal
    assert "Float64" not in market_data


def test_schema_compiles_and_fixed_point_signal_round_trips(tmp_path: Path) -> None:
    capnp = shutil.which("capnp")
    if capnp is None:
        pytest.skip("Pending: capnp compiler is unavailable; structural boundary test remains active")

    subprocess.run(
        (capnp, "compile", "-o-", str(SCHEMA_PATH)),
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    signal_text = (
        '(timestamp = 42, instrumentId = "BTCUSDT", '
        "valueRaw = (lo = 123456789, hi = 0), valuePrecision = 8, "
        'metadata = "round-trip", side = buy)'
    )
    encoded = subprocess.run(
        (capnp, "convert", "text:binary", str(SCHEMA_PATH), "TradingSignal"),
        input=signal_text.encode(),
        check=True,
        capture_output=True,
    ).stdout
    decoded = subprocess.run(
        (capnp, "convert", "binary:text", str(SCHEMA_PATH), "TradingSignal"),
        input=encoded,
        check=True,
        capture_output=True,
    ).stdout
    reencoded = subprocess.run(
        (capnp, "convert", "text:binary", str(SCHEMA_PATH), "TradingSignal"),
        input=decoded,
        check=True,
        capture_output=True,
    ).stdout

    assert reencoded == encoded
    assert b"valueRaw" in decoded
    assert b"valuePrecision = 8" in decoded
