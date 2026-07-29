# TEMPLATE_CLASSIFICATION: AI/advisory Python; non-production; off execution-critical paths
# Copyright (C) 2025 Nautech Systems, Inc. All rights reserved.
# Nautech Systems, Inc. Proprietary and Confidential.
# Use subject to license terms.

"""Local EvoMap Proxy mailbox client prototype.

The agent-side integration talks to the local Proxy. The Proxy owns Hub sync,
retries, authentication, and low-level GEP/A2A protocol details.
"""

import json
from collections.abc import Callable
from typing import Any
from urllib import parse, request

Transport = Callable[[str, str, dict[str, Any] | None], dict[str, Any]]


class EvoMapProxyMailboxClient:
    """Thin gateway for local EvoMap Proxy mailbox endpoints."""

    def __init__(
        self,
        proxy_url: str = "http://127.0.0.1:19820",
        transport: Transport | None = None,
    ) -> None:
        """Initialize the client.

        Parameters
        ----------
        proxy_url : str, default "http://127.0.0.1:19820"
            Local EvoMap Proxy URL. Do not point strategy code at the Hub.
        transport : callable, optional
            Test seam for HTTP transport.
        """
        self.proxy_url = self._normalize_local_proxy_url(proxy_url)
        self._transport = transport or self._http_json

    @staticmethod
    def _normalize_local_proxy_url(proxy_url: str) -> str:
        parsed = parse.urlparse(proxy_url.rstrip("/"))
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
            "127.0.0.1",
            "localhost",
            "::1",
        }:
            raise ValueError("EvoMap client must target the local Proxy")
        return proxy_url.rstrip("/")

    def send_message(self, message_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Enqueue a local mailbox message for Proxy-managed sync."""
        return self._post("/mailbox/send", {"type": message_type, "payload": payload})

    def poll(
        self,
        message_type: str | None = None,
        channel: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Poll local mailbox messages by optional type/channel filters."""
        payload: dict[str, Any] = {"limit": limit}
        if message_type is not None:
            payload["type"] = message_type
        if channel is not None:
            payload["channel"] = channel
        return self._post("/mailbox/poll", payload)

    def ack(self, message_ids: list[str]) -> dict[str, Any]:
        """Acknowledge processed mailbox messages."""
        return self._post("/mailbox/ack", {"message_ids": message_ids})

    def status(self, message_id: str) -> dict[str, Any]:
        """Fetch local status for a mailbox message."""
        return self._get(f"/mailbox/status/{message_id}")

    def submit_assets(self, assets: list[dict[str, Any]]) -> dict[str, Any]:
        """Submit Gene/Capsule/EvolutionEvent assets through the Proxy."""
        return self._post("/asset/submit", {"assets": assets})

    def fetch_assets(self, asset_ids: list[str]) -> dict[str, Any]:
        """Fetch asset details through the Proxy."""
        return self._post("/asset/fetch", {"asset_ids": asset_ids})

    def search_assets(
        self,
        signals: list[str],
        mode: str = "semantic",
        limit: int = 5,
    ) -> dict[str, Any]:
        """Search advisory assets through the Proxy."""
        return self._post(
            "/asset/search",
            {"signals": signals, "mode": mode, "limit": limit},
        )

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._transport("POST", f"{self.proxy_url}{path}", payload)

    def _get(self, path: str) -> dict[str, Any]:
        return self._transport("GET", f"{self.proxy_url}{path}", None)

    @staticmethod
    def _http_json(method: str, url: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=5) as response:  # nosec: prototype local Proxy client
            body = response.read().decode("utf-8")
        return json.loads(body) if body else {}
