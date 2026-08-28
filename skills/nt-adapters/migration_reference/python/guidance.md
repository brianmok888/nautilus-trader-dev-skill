# Migration/reference Python adapter guidance

NT v2 compatibility note: legacy Cython/v1 adapter guidance in this whole file is migration/reference-only; prefer Rust v2/PyO3 for new work.
> Migration/reference-only; not a production default. Rust owns production behavior.

## Python Usage

### Configure Existing Adapter

```python
from nautilus_trader.adapters.binance.config import (
    BinanceDataClientConfig,
    BinanceExecutionClientConfig,
)

data_config = BinanceDataClientConfig(
    api_key="...",
    api_secret="...",
    account_type=BinanceAccountType.USDT_FUTURE,
)

exec_config = BinanceExecutionClientConfig(
    api_key="...",
    api_secret="...",
    account_type=BinanceAccountType.USDT_FUTURE,
)
```

### Use InstrumentProvider

```python
# Instrument discovery happens automatically when adapter connects
# Access instruments via cache:
instruments = self.cache.instruments(venue=Venue("BINANCE"))
instrument = self.cache.instrument(InstrumentId.from_str("ETHUSDT-PERP.BINANCE"))
```

### Adapter Configuration Pattern

Each adapter follows the same config pattern:
- `{Adapter}DataClientConfig` — data feed configuration
- `{Adapter}ExecClientConfig` — execution configuration
- `{Adapter}InstrumentProviderConfig` — instrument discovery settings

## Python Extension

### Customize Instrument Provider

```python
from nautilus_trader.adapters.binance.providers import BinanceInstrumentProvider


class MyInstrumentProvider(BinanceInstrumentProvider):
    async def load_all_async(self, filters=None):
        await super().load_all_async(filters)
        # Add custom instrument filtering/transformation
```

### Legacy factory registration

```python
config.adapters.live.add(
    "BINANCE",
    BinanceLiveDataClientFactory,
    BinanceLiveExecClientFactory,
)
```