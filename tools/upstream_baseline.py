import os
from pathlib import Path

UPSTREAM_COMMIT = "f725e184dbd2f7432b5c7b9458b4ef6d1f85fd5f"


def default_upstream_root() -> Path:
    """Resolve the pinned upstream checkout without host-specific dated paths."""
    configured = os.environ.get("NT_UPSTREAM_ROOT")
    if configured:
        return Path(configured).expanduser()
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_home / "nautilus-trader-dev-skill" / "nautilus_trader-pinned"

UPSTREAM_REMOTE_REFS = ("origin/develop",)
