# Copyright (C) 2025 Nautech Systems, Inc. All rights reserved.
# Nautech Systems, Inc. Proprietary and Confidential.
# Use subject to license terms.

"""Contract tests for EvoMap Capsule Client."""

import sqlite3

import pytest

from brainstorming_evomap import evomap_capsule_client as _client_mod


def _terminal_record(
    *,
    request_id: str = "request-1",
    request_sequence: int = 7,
    suggestion_id: str | None = "suggestion-1",
    suggestion_hash: str | None = "suggestion-hash",
    outcome: str = "approved",
    reason: str = "offline_change_review",
    recorded_ns: int = 50,
):
    provisional = _client_mod.AdvisoryTerminalRecord(
        checkpoint_id="",
        request_id=request_id,
        request_sequence=request_sequence,
        suggestion_id=suggestion_id,
        suggestion_hash=suggestion_hash,
        outcome=outcome,
        reason=reason,
        recorded_ns=recorded_ns,
    )
    return _client_mod.AdvisoryTerminalRecord(
        checkpoint_id=_client_mod.terminal_checkpoint_id(provisional),
        request_id=request_id,
        request_sequence=request_sequence,
        suggestion_id=suggestion_id,
        suggestion_hash=suggestion_hash,
        outcome=outcome,
        reason=reason,
        recorded_ns=recorded_ns,
    )


def test_client_exposes_proxy_mailbox_methods():
    """Client must expose local Proxy mailbox and asset methods."""
    client = _client_mod.EvoMapProxyMailboxClient(proxy_url="http://127.0.0.1:19820")

    for name in [
        "send_message",
        "poll",
        "ack",
        "status",
        "submit_assets",
        "fetch_assets",
        "search_assets",
    ]:
        assert hasattr(client, name), f"Client missing required method: {name}"


def test_client_uses_local_proxy_url_by_default():
    """Default transport target must be the local Proxy, not evomap.ai."""
    client = _client_mod.EvoMapProxyMailboxClient()

    assert client.proxy_url == "http://127.0.0.1:19820"




def test_client_rejects_non_local_proxy_url():
    """Client must not let agent-side code point directly at the Hub."""
    with pytest.raises(ValueError, match="local Proxy"):
        _client_mod.EvoMapProxyMailboxClient(proxy_url="https://evomap.ai")


def test_client_posts_mailbox_send_to_local_proxy():
    """send_message posts to /mailbox/send with message type and payload."""
    calls = []

    def fake_transport(method, url, payload=None):
        calls.append((method, url, payload))
        return {"message_id": "msg_1", "status": "pending"}

    client = _client_mod.EvoMapProxyMailboxClient(transport=fake_transport)
    response = client.send_message("asset_submit", {"asset": {"id": "g1"}})

    assert response == {"message_id": "msg_1", "status": "pending"}
    assert calls == [
        (
            "POST",
            "http://127.0.0.1:19820/mailbox/send",
            {"type": "asset_submit", "payload": {"asset": {"id": "g1"}}},
        )
    ]


def test_submit_assets_uses_asset_submit_endpoint():
    """submit_assets sends assets through /asset/submit."""
    calls = []

    def fake_transport(method, url, payload=None):
        calls.append((method, url, payload))
        return {"message_id": "msg_2", "status": "pending"}

    client = _client_mod.EvoMapProxyMailboxClient(transport=fake_transport)
    response = client.submit_assets([{"type": "Gene", "id": "g1"}])

    assert response["status"] == "pending"
    assert calls == [
        (
            "POST",
            "http://127.0.0.1:19820/asset/submit",
            {"assets": [{"type": "Gene", "id": "g1"}]},
        )
    ]


def test_terminal_checkpoint_persists_record_and_floor_before_ack(tmp_path):
    database = tmp_path / "advisory.sqlite3"
    store = _client_mod.AdvisoryCheckpointStore(database)
    record = _terminal_record()

    ack = store.persist_terminal(record)

    assert ack == _client_mod.AdvisoryCheckpointAck(
        checkpoint_id=record.checkpoint_id,
    )
    reopened = _client_mod.AdvisoryCheckpointStore(database)
    assert reopened.request_sequence_floor() == 7
    assert reopened.terminal_record(record.checkpoint_id) == record


def test_terminal_checkpoint_rolls_back_precommit_failure(tmp_path):
    database = tmp_path / "advisory.sqlite3"
    store = _client_mod.AdvisoryCheckpointStore(database)
    record = _terminal_record()

    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TRIGGER interrupt_before_floor BEFORE UPDATE ON advisory_state "
            "BEGIN SELECT RAISE(ABORT, 'simulated crash'); END",
        )

    with pytest.raises(sqlite3.IntegrityError, match="simulated crash"):
        store.persist_terminal(record)

    reopened = _client_mod.AdvisoryCheckpointStore(database)
    assert reopened.request_sequence_floor() == 0
    assert reopened.terminal_record(record.checkpoint_id) is None


def test_terminal_checkpoint_is_idempotent_after_commit_before_ack_delivery(tmp_path):
    database = tmp_path / "advisory.sqlite3"
    store = _client_mod.AdvisoryCheckpointStore(database)
    record = _terminal_record()

    assert store.persist_terminal(record).checkpoint_id == record.checkpoint_id
    assert store.persist_terminal(record).checkpoint_id == record.checkpoint_id

    with sqlite3.connect(database) as connection:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM advisory_terminal_checkpoint",
        ).fetchone()[0]
    assert row_count == 1
    assert store.request_sequence_floor() == 7


def test_terminal_checkpoint_rejects_digest_reuse_for_a_different_record(tmp_path):
    database = tmp_path / "advisory.sqlite3"
    store = _client_mod.AdvisoryCheckpointStore(database)
    first = _terminal_record()
    conflicting = _client_mod.AdvisoryTerminalRecord(
        checkpoint_id=first.checkpoint_id,
        request_id="request-2",
        request_sequence=8,
        suggestion_id="suggestion-2",
        suggestion_hash="different-hash",
        outcome="approved",
        reason="offline_change_review",
        recorded_ns=60,
    )
    assert store.persist_terminal(first).checkpoint_id == first.checkpoint_id

    with pytest.raises(sqlite3.IntegrityError):
        store.persist_terminal(conflicting)

    assert store.terminal_record(first.checkpoint_id) == first
    assert store.request_sequence_floor() == 7


def test_terminal_checkpoint_rejects_mismatched_digest_on_first_write(tmp_path):
    database = tmp_path / "advisory.sqlite3"
    store = _client_mod.AdvisoryCheckpointStore(database)
    valid_checkpoint_id = _terminal_record().checkpoint_id
    assert valid_checkpoint_id != "checkpoint-from-another-record"
    record = _client_mod.AdvisoryTerminalRecord(
        checkpoint_id="checkpoint-from-another-record",
        request_id="request-1",
        request_sequence=7,
        suggestion_id="suggestion-1",
        suggestion_hash="suggestion-hash",
        outcome="approved",
        reason="offline_change_review",
        recorded_ns=50,
    )

    with pytest.raises(sqlite3.IntegrityError):
        store.persist_terminal(record)

    assert store.terminal_record("checkpoint-from-another-record") is None
    assert store.request_sequence_floor() == 0
