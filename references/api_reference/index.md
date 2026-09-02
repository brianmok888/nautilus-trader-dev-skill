# Python API (legacy v1 snapshot)

NT v2 compatibility note: this API reference tree is a legacy v1 Python-layout snapshot retained
migration/reference-only. NautilusTrader V2 exposes Python APIs through flat PyO3 re-export
surfaces (`nautilus_trader/<pkg>/__init__.pyi`) generated from the Rust crates; the deep
`nautilus_trader.<pkg>.<module>` paths documented here do not resolve in the current pinned
package. Use the pinned upstream `docs/developer_guide/` and `crates/` sources for current
APIs, and treat every page below as historical reference.

## Why Python?

Python was originally created decades ago as a simple scripting language with a clean straight
forward syntax. It has since evolved into a fully fledged general purpose object-oriented
programming language. Based on the TIOBE index, Python is currently the most popular programming language in the world.
Not only that, Python has become the *de facto lingua franca* of data science, machine learning, and artificial intelligence.
