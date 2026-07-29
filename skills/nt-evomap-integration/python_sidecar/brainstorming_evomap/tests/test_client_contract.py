# Copyright (C) 2025 Nautech Systems, Inc. All rights reserved.
# Nautech Systems, Inc. Proprietary and Confidential.
# Use subject to license terms.

"""Contract tests for EvoMap Capsule Client."""

import pytest

from brainstorming_evomap import evomap_capsule_client as _client_mod


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
