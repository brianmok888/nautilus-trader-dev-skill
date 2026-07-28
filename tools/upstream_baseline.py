import os
from pathlib import Path

UPSTREAM_COMMIT = "6e59fd74eaacacbb7410936f1766bd89fcce6f59"


def default_upstream_root() -> Path:
    """Resolve the pinned upstream checkout without host-specific dated paths."""
    configured = os.environ.get("NT_UPSTREAM_ROOT")
    if configured:
        return Path(configured).expanduser()
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_home / "nautilus-trader-dev-skill" / "nautilus_trader"

# Moving refs used only by tools/check_upstream_freshness.py; they do not change
# the pinned reproducible baseline above.
UPSTREAM_REMOTE_REFS = ("origin/develop", "origin/master", "origin/nightly")
