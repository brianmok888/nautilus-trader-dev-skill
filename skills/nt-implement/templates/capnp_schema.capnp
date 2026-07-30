@0x85d36655c630fbdf;

struct Int128 {
  lo @0 :UInt64;
  hi @1 :UInt64;
}

struct UInt128 {
  lo @0 :UInt64;
  hi @1 :UInt64;
}

struct TradingSignal {
  timestamp @0 :UInt64;
  instrumentId @1 :Text;
  valueRaw @2 :Int128;
  metadata @3 :Text;

  enum Side {
    none @0;
    buy @1;
    sell @2;
  }

  side @4 :Side;
  valuePrecision @5 :UInt8;
}

struct CustomMarketData {
  timestamp @0 :UInt64;
  priceRaw @1 :Int128;
  quantityRaw @2 :UInt128;
  venueOrderId @3 :Text;
  pricePrecision @4 :UInt8;
  quantityPrecision @5 :UInt8;
}
