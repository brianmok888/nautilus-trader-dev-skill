# Serialization

## Python custom component data

Python actors and strategies exchange custom data with the current `DataType` and
`CustomData` model APIs. The payload type must already satisfy the system's model
and serialization contracts; do not invent a `Struct` base class or an ad-hoc
registration decorator.

```python
from nautilus_trader.model import CustomData, DataType

data_type = DataType(dict, metadata={"schema": "regime-v1"})
message = CustomData(data_type=data_type, data={"value": "risk-on"})
```

Publish and subscribe with the component message-bus APIs documented in the
pinned upstream `docs/concepts/message_bus.md`. Use an explicit metadata schema
version when producers and consumers evolve independently.

## Rust wire formats

The `nautilus-serialization` crate provides serde/MessagePack helpers,
feature-gated Arrow, and optional SBE market-data codecs. Enable only the wire
format owned by the component and prove encode/decode round trips plus version
compatibility at the boundary. SBE uses a pinned external codec dependency;
verify its actual supported message inventory before selecting it for a new
payload. Adding a Rust type alone does not register it globally.

Current develop removed Cap'n Proto, including its Cargo feature, schemas,
generated bindings, and compiler-install scripts. Earlier Cap'n Proto examples
are historical migration references and do not apply to the current pin. The
source boundary is recorded in `references/README.md`.
