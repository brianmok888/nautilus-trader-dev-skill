# Visualization in NautilusTrader

NautilusTrader provides Plotly-based, browser-viewable tearsheets. This Python workflow is migration/reference-only for non-AI systems; new strategy and research work follows the Rust-first path.

## Requirements

Install the visualization extra in the migration environment:

```bash
uv add "nautilus_trader[visualization]"
```

## Features

- **Interactive Tearsheets**: Zoom, hover, and filter charts in a self-contained HTML file.
- **Dark Mode Support**: Native dark and light themes for all charts.
- **Chart Registry**: Extensible system to add your own custom Plotly charts.
- **Plugin System**: Decoupled visualization architecture.

## Primary Metrics

The new tearsheets include critical performance metrics by default:
- **CAGR**: Compound Annual Growth Rate.
- **Calmar Ratio**: Annualized return relative to maximum drawdown.
- **Max Drawdown**: The largest peak-to-trough decline.

## Usage Example

```python
from nautilus_trader.analysis import TearsheetConfig, create_tearsheet

config = TearsheetConfig()
create_tearsheet(engine, output_path="tearsheet.html", config=config)
```

See [backtest_viz.py](../skills/nt-implement/templates/legacy_migration/backtest_viz.py) for a legacy Python migration reference.
