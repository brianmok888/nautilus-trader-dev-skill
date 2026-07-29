# TEMPLATE_CLASSIFICATION: legacy executable; migration/reference-only; not a production default
# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode
# references in this file are retained for migration/reference-only context.
# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.

from nautilus_trader.analysis import TearsheetConfig, create_tearsheet
from nautilus_trader.backtest.engine import BacktestEngine

# 1. Run your backtest
engine = BacktestEngine()
# ... engine setup and run ...

config = TearsheetConfig()
create_tearsheet(engine, output_path="tearsheet.html", config=config)
