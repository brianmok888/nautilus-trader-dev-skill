# TEMPLATE_CLASSIFICATION: migration/reference-only; not a production default
"""
DEX Adapter Template: Configuration

Defines all three config classes required by NautilusTrader's adapter framework:
- InstrumentProviderConfig  → for pool/market discovery
- DataClientConfig          → for market data subscription
- ExecClientConfig          → for order execution

Replace 'MyDEX' with your actual DEX/venue name throughout.
"""

from frozendict import frozendict
from nautilus_trader.config import (
    InstrumentProviderConfig,
    LiveDataClientConfig,
    LiveExecClientConfig,
)
from pydantic import SecretStr


class UnsafeLiveDEXConfigError(ValueError):
    def __init__(self, field_name: str) -> None:
        super().__init__(
            f"{field_name} is required before setting sandbox_mode=False"
        )


# =============================================================================
# Instrument Provider Config
# =============================================================================

class MyDEXInstrumentProviderConfig(InstrumentProviderConfig, frozen=True):
    """
    Configuration for the MyDEX instrument provider.

    Parameters
    ----------
    rpc_url : str
        HTTP JSON-RPC endpoint (e.g. Infura, Alchemy, local node).
    chain_id : int
        EVM chain ID (1=mainnet, 42161=Arbitrum, etc.)
    pools : tuple[str, ...]
        Specific pool contract addresses to load. If empty, loads all known pools.
    sandbox_mode : bool
        If True, uses testnet RPC and skips chain calls in tests.
    """

    filters: frozendict[str, object] | None = None
    rpc_url: str = "http://127.0.0.1:8545"
    chain_id: int = 31337
    pools: tuple[str, ...] = ()  # Empty → load all known pools
    sandbox_mode: bool = True


# =============================================================================
# Data Client Config
# =============================================================================

class MyDEXDataClientConfig(LiveDataClientConfig, frozen=True):
    """
    Configuration for the MyDEX market data client.

    The data client polls the RPC node for pool state updates and emits
    QuoteTick / TradeTick / OrderBookDelta objects into the Nautilus stream.

    Parameters
    ----------
    rpc_url : str
        HTTP JSON-RPC endpoint.
    ws_rpc_url : str, optional
        WebSocket RPC endpoint for event subscriptions (preferred over polling).
    chain_id : int
        EVM chain ID.
    pool_addresses : list[str]
        Legacy direct pools used only when the standard base
        ``InstrumentProviderConfig`` default is retained.
    poll_interval_secs : float
        Seconds between RPC polls (if WS not available). Reduce for fresher data,
        but watch RPC rate limits.
    sandbox_mode : bool
        If True, uses mock/testnet data instead of mainnet.

    Notes
    -----
    A nested ``MyDEXInstrumentProviderConfig`` is authoritative for every
    provider field. These direct legacy fields apply only when the standard
    base ``InstrumentProviderConfig`` default is retained.
    """

    rpc_url: str = "http://127.0.0.1:8545"
    ws_rpc_url: str | None = None       # Optional: WebSocket RPC for event streaming
    chain_id: int = 31337
    pool_addresses: list[str] = []
    poll_interval_secs: float = 2.0     # Poll every 2 seconds (rate-limit friendly)
    sandbox_mode: bool = True


# =============================================================================
# Execution Client Config
# =============================================================================

class MyDEXExecClientConfig(LiveExecClientConfig, frozen=True):
    """
    Configuration for the MyDEX execution client.

    SECURITY NOTES:
    - Store `private_key` in environment variables, never in source files.
    - Use SecretStr to prevent key from appearing in logs and repr().

    Parameters
    ----------
    rpc_url : str
        HTTP JSON-RPC endpoint for sending transactions.
    private_key : SecretStr
        EVM wallet private key (hex, without 0x prefix or with).
        Load from: SecretStr(os.environ["WALLET_PRIVATE_KEY"])
    wallet_address : str
        Public wallet address (0x...) for balance queries.
    chain_id : int
        EVM chain ID.
    max_slippage_bps : int
        Maximum acceptable slippage in basis points (default 50 = 0.5%).
    gas_limit : int
        Gas limit per transaction. Actual gas estimated + 20% buffer applied.
    gas_price_gwei : int, optional
        Fixed gas price in Gwei. If None, uses network suggestion.
    sandbox_mode : bool
        If True, uses testnet or local fork. No real funds at risk.

    Notes
    -----
    A nested ``MyDEXInstrumentProviderConfig`` is authoritative for every
    provider field. These direct legacy fields apply only when the standard
    base ``InstrumentProviderConfig`` default is retained.
    """

    rpc_url: str = "http://127.0.0.1:8545"
    private_key: SecretStr = SecretStr("")   # ← load from env var
    wallet_address: str = "0x0000000000000000000000000000000000000000"
    chain_id: int = 31337
    max_slippage_bps: int = 50           # 0.50% max slippage
    gas_limit: int = 300_000             # Safe upper bound for DEX swaps
    gas_price_gwei: int | None = None    # None → use network suggestion
    sandbox_mode: bool = True

    def __post_init__(self) -> None:
        if self.sandbox_mode:
            return
        if self.private_key.get_secret_value() == "":
            raise UnsafeLiveDEXConfigError("private_key")
        if self.rpc_url == "http://127.0.0.1:8545":
            raise UnsafeLiveDEXConfigError("rpc_url")
