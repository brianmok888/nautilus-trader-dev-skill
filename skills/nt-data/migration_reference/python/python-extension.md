# Python Extension

> **Migration/reference-only.** This Python material is not a
> production default. New production work uses the Rust guidance in the
> root `nt-data` skill. The only active Python lane is AI/advisory work
> outside this repository.


### Custom DataClient

```python
from nautilus_trader.data.client import MarketDataClient

class MyDataClient(MarketDataClient):
    def __init__(self, ...):
        super().__init__(...)

    async def _connect(self):
        # Establish connection to data source
        pass

    async def _disconnect(self):
        # Clean up connection
        pass

    async def _subscribe_trade_ticks(self, instrument_id):
        # Subscribe to trade feed
        pass

    def _handle_trade_tick(self, tick):
        # Forward tick to data engine
        self._handle_data(tick)
```

### Custom Arrow Serializers

Register custom Arrow schemas for custom data types:

```python
import pyarrow as pa
from nautilus_trader.serialization.arrow.serializer import register_arrow

# If using @customdataclass, serialization is auto-generated
# For manual registration:
register_arrow(
    data_cls=MyCustomData,
    schema=pa.schema([...]),
    serializer=my_serializer_func,
    deserializer=my_deserializer_func,
)
```
