# Custom Data Patterns in NautilusTrader

## Current Python registration surface

The V2 PyO3 model module exports `register_custom_data_class` from
`nautilus_trader.model`. Registration takes a single class argument: the class
must provide a `to_json` instance method and a `from_json(data)` classmethod,
plus `encode_record_batch_py` / `decode_record_batch_py` for Arrow
record-batch persistence. Registration requires both Arrow methods to exist,
even for message-bus-only types; retain stubs that raise when persistence is
unsupported. Registration is process-global, so
perform it once during application startup.

```python
import json

from nautilus_trader.model import register_custom_data_class

class MySignal:
    ts_event = 0
    ts_init = 0

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, data):
        instance = cls()
        instance.__dict__.update(data)
        return instance

    def encode_record_batch_py(self, items):
        raise NotImplementedError("Arrow encoding is not configured")

    @classmethod
    def decode_record_batch_py(cls, metadata, batch):
        raise NotImplementedError("Arrow decoding is not configured")

register_custom_data_class(MySignal)
```

`encode_record_batch_py(self, items)` receives a list of instances and returns a
PyArrow `RecordBatch`. `decode_record_batch_py(metadata, batch)` receives schema
metadata first and the record batch second, and returns a list of instances.
Define and version that schema in the owning component. Message-bus-only types
must retain both Arrow callback stubs so registration succeeds; catalog writes
must fail explicitly until Arrow persistence is implemented. Source:
`crates/model/src/python/data/mod.rs` (`register_custom_data_class` and its
encoder/decoder callbacks) at develop `77d785c69205c4326e6aadb46d03fb45357a78f2`.

## Current Rust custom-data surface

Rust custom data types derive their model implementation from the `#[custom_data]`
attribute macro in `nautilus-persistence-macros` (pinned source:
`crates/persistence/src/common/custom.rs`). Applied to a struct with named fields
— including required `ts_event` and `ts_init` `UnixNanos` fields — it implements
`nautilus_model::data::CustomDataTrait` (`type_name_static`, `from_json`),
`HasTsInit`, the Arrow schema and record-batch traits, and the catalog path
prefix. `#[custom_data(pyo3)]` additionally generates Python bindings;
`#[custom_data(pyo3, no_arrow)]` skips Arrow wiring for live-only types, and
`stub_module = "nautilus_trader.<module>"` emits pyo3-stub-gen metadata.

```rust
use nautilus_core::UnixNanos;
use nautilus_persistence_macros::custom_data;

#[custom_data(pyo3)]
pub struct MySignal {
    pub instrument_id: InstrumentId,
    pub value: f64,
    pub ts_event: UnixNanos,
    pub ts_init: UnixNanos,
}
```

Register Rust types once with
`nautilus_serialization::ensure_custom_data_registered::<T>()` (Arrow-backed)
or `nautilus_model::data::ensure_custom_data_json_registered::<T>()`
(`no_arrow` types); call `nautilus_model::data::register_rust_extractor::<T>()`
when the type must also flow through Python consumers.

## Required data contract

A custom signal type needs stable `ts_event` and `ts_init` Unix-nanosecond fields,
a deterministic `to_json`, and a matching `from_json(data)` classmethod. Include every routing key
(such as `instrument_id`) in the serialized form and round-trip it back to the
Nautilus model type. Test JSON and Arrow round trips separately; do not treat one
as proof of the other.

## Migration warning

Historical decorator-based custom-model examples are not current V2 APIs. Do not
import removed custom-model modules or claim automatic Arrow schema generation.
The current surfaces are the Python `register_custom_data_class` function above
and the Rust `#[custom_data]` attribute macro with its generated
`CustomDataTrait` implementation.
