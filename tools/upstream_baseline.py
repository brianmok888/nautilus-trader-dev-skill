import os
from pathlib import Path

UPSTREAM_COMMIT = "8ecab1ce90d9790b1e18e162842decbae4d9de57"


def default_upstream_root() -> Path:
    """Resolve the pinned upstream checkout without host-specific dated paths."""
    configured = os.environ.get("NT_UPSTREAM_ROOT")
    if configured:
        return Path(configured).expanduser()
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_home / "nautilus-trader-dev-skill" / "nautilus_trader-pinned"

UPSTREAM_REMOTE_REFS = ("origin/develop",)
