from pathlib import Path

UPSTREAM_COMMIT = "6e59fd74eaacacbb7410936f1766bd89fcce6f59"
DEFAULT_UPSTREAM_ROOT = Path("/tmp/nautilus_trader_upstream_audit_20260728")

# Moving refs used only by tools/check_upstream_freshness.py; they do not change
# the pinned reproducible baseline above.
UPSTREAM_REMOTE_REFS = ("origin/develop", "origin/master", "origin/nightly")
