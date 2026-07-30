# TEMPLATE_CLASSIFICATION: legacy executable; migration/reference-only; not a production default
# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode
# references in this file are retained for migration/reference-only context.
# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.

"""
DEX Adapter Template: Client Factory

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
Registers the DEX adapter's data and execution clients with a TradingNode.

Phase 6 of the 7-phase DEX adapter implementation sequence.

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
Usage in TradingNode:
    node = TradingNode(config=config)
    node.add_data_client_factory("MYDEX", MyDEXLiveDataClientFactory)
    node.add_exec_client_factory("MYDEX", MyDEXLiveExecClientFactory)

Replace 'MyDEX' with your actual DEX name throughout.
"""

import msgspec
from frozendict import frozendict
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock, MessageBus
from nautilus_trader.live.config import LiveDataClientConfig, LiveExecClientConfig
from nautilus_trader.live.data_client import LiveDataClient
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.live.factories import LiveDataClientFactory, LiveExecClientFactory
from nautilus_trader.model.identifiers import AccountId, ClientId, Venue

from ..dex_config import MyDEXDataClientConfig, MyDEXExecClientConfig
from ..dex_instrument_provider import (
    MyDEXInstrumentProvider,
    MyDEXInstrumentProviderConfig,
)
from .dex_data_client import MyDEXDataClient
from .dex_exec_client import MyDEXExecutionClient

VENUE_NAME = "MYDEX"  # ← Change to your actual venue name (e.g. "UNISWAP_V3")


# =============================================================================
# Data Client Factory
# =============================================================================


class MyDEXLiveDataClientFactory(LiveDataClientFactory):
    """
    Factory for creating MyDEX live data clients.

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
    Registered with TradingNode via:
        node.add_data_client_factory("MYDEX", MyDEXLiveDataClientFactory)
    """

    @staticmethod
    def create(
        loop,
        name: str,
        config: LiveDataClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> LiveDataClient:
        """
        Create and return a MyDEX data client.

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop (passed by TradingNode).
        name : str
            The client name (matches the key in data_clients config dict).
        config : MyDEXDataClientConfig
            The data client configuration.
        msgbus : MessageBus
            The Nautilus message bus.
        cache : Cache
            The Nautilus cache.
        clock : LiveClock
            The Nautilus clock.
        """
        if not isinstance(config, MyDEXDataClientConfig):
            raise TypeError("config must be MyDEXDataClientConfig")
        # Share instrument provider between data and exec clients
        # Use a simple module-level cache to avoid double-loading
        provider = _get_or_create_instrument_provider(config)

        return MyDEXDataClient(
            loop=loop,
            client_id=ClientId(name),
            venue=Venue(name),
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )


# =============================================================================
# Execution Client Factory
# =============================================================================


class MyDEXLiveExecClientFactory(LiveExecClientFactory):
    """
    Factory for creating MyDEX live execution clients.

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
    Registered with TradingNode via:
        node.add_exec_client_factory("MYDEX", MyDEXLiveExecClientFactory)
    """

    @staticmethod
    def create(
        loop,
        name: str,
        config: LiveExecClientConfig,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
    ) -> LiveExecutionClient:
        """
        Create and return a MyDEX execution client.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop.
        name : str
            The client name (matches the key in exec_clients config dict).
        config : MyDEXExecClientConfig
            The exec client configuration (includes private key as SecretStr).
        msgbus : MessageBus
            The Nautilus message bus.
        cache : Cache
            The Nautilus cache.
        clock : LiveClock
            The Nautilus clock.
        """
        if not isinstance(config, MyDEXExecClientConfig):
            raise TypeError("config must be MyDEXExecClientConfig")
        provider = _get_or_create_instrument_provider(config)
        account_id = AccountId(f"{name}-001")

        return MyDEXExecutionClient(
            loop=loop,
            client_id=ClientId(name),
            venue=Venue(name),
            account_id=account_id,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )


# =============================================================================
# Shared Instrument Provider Cache
# =============================================================================

_instrument_providers: dict[bytes, MyDEXInstrumentProvider] = {}


def _effective_instrument_provider_config(config) -> MyDEXInstrumentProviderConfig:
    nested = config.instrument_provider
    if isinstance(nested, MyDEXInstrumentProviderConfig):
        rpc_url = nested.rpc_url
        chain_id = nested.chain_id
        pools = nested.pools
        sandbox_mode = nested.sandbox_mode
    else:
        rpc_url = config.rpc_url
        chain_id = config.chain_id
        pools = getattr(config, "pool_addresses", ())
        sandbox_mode = config.sandbox_mode

    return MyDEXInstrumentProviderConfig(
        load_all=nested.load_all,
        load_ids=frozenset(nested.load_ids) if nested.load_ids is not None else None,
        filters=frozendict(nested.filters) if nested.filters is not None else None,
        filter_callable=nested.filter_callable,
        log_warnings=nested.log_warnings,
        use_gamma_markets=nested.use_gamma_markets,
        rpc_url=rpc_url,
        chain_id=chain_id,
        pools=tuple(pools),
        sandbox_mode=sandbox_mode,
    )


def _get_or_create_instrument_provider(config) -> MyDEXInstrumentProvider:
    """
    Get or create a provider for the complete effective provider configuration.

    Data and execution clients share one provider to avoid double-loading
    pool metadata from the chain.
    """
    provider_config = _effective_instrument_provider_config(config)
    key = msgspec.json.encode(provider_config, order="deterministic")

    if key not in _instrument_providers:
        _instrument_providers[key] = MyDEXInstrumentProvider(config=provider_config)

    return _instrument_providers[key]
