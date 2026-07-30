# TEMPLATE_CLASSIFICATION: AI/advisory Python; non-production; off execution-critical paths
# Copyright (C) 2025 Nautech Systems, Inc. All rights reserved.
# Nautech Systems, Inc. Proprietary and Confidential.
# Use subject to license terms.

"""Local EvoMap Proxy mailbox client prototype.

The agent-side integration talks to the local Proxy. The Proxy owns Hub sync,
retries, authentication, and low-level GEP/A2A protocol details.
"""

import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib import parse, request

Transport = Callable[[str, str, dict[str, Any] | None], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class AdvisoryTerminalRecord:
    checkpoint_id: str
    request_id: str
    request_sequence: int
    suggestion_id: str | None
    suggestion_hash: str | None
    outcome: str
    reason: str
    recorded_ns: int


@dataclass(frozen=True, slots=True)
class AdvisoryCheckpointAck:
    checkpoint_id: str


class AdvisoryCheckpointStore:
    def __init__(self, database: Path) -> None:
        self._database = database
        self._initialize()

    def persist_terminal(
        self,
        record: AdvisoryTerminalRecord,
    ) -> AdvisoryCheckpointAck:
        payload = json.dumps(
            asdict(record),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        with sqlite3.connect(self._database) as connection:
            connection.execute(
                "INSERT OR IGNORE INTO advisory_terminal_checkpoint "
                "(checkpoint_id, record_json) VALUES (?, ?)",
                (record.checkpoint_id, payload),
            )
            stored = connection.execute(
                "SELECT record_json FROM advisory_terminal_checkpoint "
                "WHERE checkpoint_id = ?",
                (record.checkpoint_id,),
            ).fetchone()
            if stored is None or stored[0] != payload:
                raise sqlite3.IntegrityError(
                    "checkpoint_id already binds a different record",
                )
            connection.execute(
                "UPDATE advisory_state SET request_sequence_floor = MAX("
                "request_sequence_floor, ?) WHERE singleton = 1",
                (record.request_sequence,),
            )
        return AdvisoryCheckpointAck(checkpoint_id=record.checkpoint_id)

    def request_sequence_floor(self) -> int:
        with sqlite3.connect(self._database) as connection:
            row = connection.execute(
                "SELECT request_sequence_floor FROM advisory_state "
                "WHERE singleton = 1",
            ).fetchone()
        return 0 if row is None else int(row[0])

    def terminal_record(self, checkpoint_id: str) -> AdvisoryTerminalRecord | None:
        with sqlite3.connect(self._database) as connection:
            row = connection.execute(
                "SELECT record_json FROM advisory_terminal_checkpoint "
                "WHERE checkpoint_id = ?",
                (checkpoint_id,),
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(row[0])
        return AdvisoryTerminalRecord(**payload)

    def _initialize(self) -> None:
        with sqlite3.connect(self._database) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS advisory_terminal_checkpoint ("
                "checkpoint_id TEXT PRIMARY KEY, record_json TEXT NOT NULL)",
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS advisory_state ("
                "singleton INTEGER PRIMARY KEY CHECK (singleton = 1), "
                "request_sequence_floor INTEGER NOT NULL)",
            )
            connection.execute(
                "INSERT OR IGNORE INTO advisory_state "
                "(singleton, request_sequence_floor) VALUES (1, 0)",
            )


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
