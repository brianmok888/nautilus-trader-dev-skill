# TEMPLATE_CLASSIFICATION: legacy executable; migration/reference-only; not a production default
# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode
# references in this file are retained for migration/reference-only context.
# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
from nautilus_trader.adapters.kraken.config import KrakenDataClientConfig
from nautilus_trader.adapters.kraken.config import KrakenExecClientConfig
from nautilus_trader.adapters.kraken.config import KrakenInstrumentProviderConfig
from nautilus_trader.config import TradingNodeConfig

# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
def get_kraken_config(
    api_key: str,
    api_secret: str,
    instrument_ids: list[str] = None
) -> TradingNodeConfig:
    """
    Create a TradingNodeConfig for Kraken (v1.222.0+).
    """
    
    # 1. Instrument Provider
    # Configures how instruments are loaded from Kraken
    instrument_provider = KrakenInstrumentProviderConfig(
        load_ids=frozenset(instrument_ids) if instrument_ids else None,
        load_all=False if instrument_ids else True,
    )
    
    # 2. Data Client
    # Handles WebSocket market data connection
    data_client = KrakenDataClientConfig(
        api_key=api_key,
        api_secret=api_secret,
        # subscription_type="book" or "ticker" etc. handled per subscription
    )
    
    # 3. Execution Client
    # Handles order execution and account management
    exec_client = KrakenExecClientConfig(
        api_key=api_key,
        api_secret=api_secret,
    )
    
# NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.
    return TradingNodeConfig(
        trader_id="KRAKEN-NODE-001",
        data_clients={"KRAKEN": data_client},
        exec_clients={"KRAKEN": exec_client},
        instrument_providers={"KRAKEN": instrument_provider},
    )
