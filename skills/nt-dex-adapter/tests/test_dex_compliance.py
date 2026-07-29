# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode
# references in this file are retained for migration/reference-only context.
# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.

"""Current DEX configuration and instrument-provider structural checks."""

import importlib.util
from inspect import iscoroutinefunction
from pathlib import Path

import pytest

pytest.importorskip("pydantic")

_templates = Path(__file__).parent.parent / "templates"


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, _templates / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_config_mod = _load_module("dex_config")
_provider_mod = _load_module("dex_instrument_provider")

MyDEXInstrumentProviderConfig = _config_mod.MyDEXInstrumentProviderConfig
MyDEXDataClientConfig = _config_mod.MyDEXDataClientConfig
MyDEXExecClientConfig = _config_mod.MyDEXExecClientConfig
MyDEXInstrumentProvider = _provider_mod.MyDEXInstrumentProvider


class TestInstrumentProviderInterface:
    """Checks all required InstrumentProvider methods are present and async."""

    def test_load_all_async_exists(self):
        assert hasattr(MyDEXInstrumentProvider, "load_all_async")

    def test_load_all_async_is_coroutine(self):
        assert iscoroutinefunction(MyDEXInstrumentProvider.load_all_async)

    def test_load_ids_async_exists(self):
        assert hasattr(MyDEXInstrumentProvider, "load_ids_async")

    def test_load_ids_async_is_coroutine(self):
        assert iscoroutinefunction(MyDEXInstrumentProvider.load_ids_async)

    def test_get_all_exists(self):
        assert hasattr(MyDEXInstrumentProvider, "get_all")

    def test_find_exists(self):
        assert hasattr(MyDEXInstrumentProvider, "find")

    def test_parse_pool_to_instrument_exists(self):
        assert hasattr(MyDEXInstrumentProvider, "_parse_pool_to_instrument")


class TestConfigInterface:
    """Checks that all config classes have required security-sensitive fields."""

    @staticmethod
    def _has_field(config_cls, name: str) -> bool:
        model_fields = getattr(config_cls, "model_fields", None)
        if model_fields is not None:
            return name in model_fields
        legacy_fields = getattr(config_cls, "__fields__", None)
        if legacy_fields is not None:
            return name in legacy_fields
        return hasattr(config_cls, name)

    def test_exec_config_has_secret_str_private_key(self):
        """Private key must be SecretStr, not plain str."""
        from pydantic import SecretStr

        config = MyDEXExecClientConfig()
        assert hasattr(config, "private_key"), (
            "private_key field missing from ExecClientConfig"
        )
        assert isinstance(config.private_key, SecretStr), (
            f"private_key must be SecretStr, got {type(config.private_key)}. "
            "Plain str leaks keys in logs and repr()!"
        )

    def test_exec_config_has_sandbox_mode(self):
        assert self._has_field(MyDEXExecClientConfig, "sandbox_mode")

    def test_exec_config_has_max_slippage_bps(self):
        assert self._has_field(MyDEXExecClientConfig, "max_slippage_bps")

    def test_data_config_has_poll_interval(self):
        assert self._has_field(MyDEXDataClientConfig, "poll_interval_secs")

    def test_provider_config_has_sandbox_mode(self):
        assert self._has_field(MyDEXInstrumentProviderConfig, "sandbox_mode")

    def test_exec_config_defaults_to_sandbox_mode(self):
        config = MyDEXExecClientConfig()

        assert config.sandbox_mode is True

    def test_exec_config_default_private_key_is_empty(self):
        config = MyDEXExecClientConfig()

        assert config.private_key.get_secret_value() == ""

    def test_exec_config_default_chain_is_not_mainnet(self):
        config = MyDEXExecClientConfig()

        assert config.chain_id != 1

    def test_exec_config_rejects_live_mode_without_private_key(self):
        from pydantic import SecretStr

        with pytest.raises(ValueError, match="private_key"):
            MyDEXExecClientConfig(
                private_key=SecretStr(""),
                sandbox_mode=False,
            )
