from __future__ import annotations

import ast
import importlib.util
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import ModuleType
from typing import Protocol

import pytest
from nautilus_trader.model import ActorId

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/nt-evomap-integration/templates/advisory_actor.py"
FORBIDDEN_HANDLERS = {
    "on_bar",
    "on_book",
    "on_book_deltas",
    "on_data",
    "on_historical_bars",
    "on_historical_data",
    "on_quote",
    "on_signal",
    "on_trade",
}
FORBIDDEN_CALLS = {
    "cancel_order",
    "close_position",
    "modify_order",
    "open",
    "publish_data",
    "publish_signal",
    "queue_for_executor",
    "request_bars",
    "run_in_executor",
    "shutdown_system",
    "submit_order",
    "subscribe_bars",
}
FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "httpx",
    "langchain",
    "langgraph",
    "nautilus_trader.execution",
    "nautilus_trader.model.data",
    "onnxruntime",
    "requests",
    "socket",
    "urllib",
}
REQUIRED_TYPES = {
    "AdvisoryAuditRecord",
    "AdvisoryBridgeActor",
    "AdvisoryCheckpointAck",
    "AdvisoryDecision",
    "AdvisoryMailboxPort",
    "AdvisoryRequest",
    "AdvisoryResult",
}


class _MailboxPort(Protocol):
    def try_put_result(self, result) -> bool: ...

    def try_put_checkpoint_ack(self, ack) -> bool: ...

    def acknowledge_audit(self, checkpoint_id: str) -> bool: ...

    def try_peek_audit(self): ...

    def try_peek_checkpoint(self): ...

    def _acknowledge_checkpoint(self, expected): ...


class _Actor(Protocol):
    _mailbox: _MailboxPort

    @property
    def staged_result(self): ...

    @property
    def authority(self): ...

    @property
    def request_sequence_floor(self) -> int: ...

    def request_review(self, request) -> bool: ...

    def poll_result(self, now_ns: int): ...

    def approve(self, decision) -> bool: ...

    def poll_checkpoint_ack(self) -> bool: ...

    def on_reset(self) -> None: ...


class _RequestRecord(Protocol):
    request_id: str


class _AuditStore:
    def __init__(self) -> None:
        self.records = []

    def persist_next(self, mailbox: _MailboxPort):
        record = mailbox.try_peek_audit()
        assert record is not None
        self.records.append(record)
        assert mailbox.acknowledge_audit(record.checkpoint_id) is True
        return record


def persist_audit(mailbox: _MailboxPort):
    return _AuditStore().persist_next(mailbox)


class _CheckpointStore:
    def __init__(self) -> None:
        self.request_sequence_floor = 0

    def persist_terminal(self, module: ModuleType, mailbox: _MailboxPort) -> str:
        record = mailbox.try_peek_checkpoint()
        assert record is not None
        self.request_sequence_floor = max(
            self.request_sequence_floor,
            record.request_sequence,
        )
        ack = module.AdvisoryCheckpointAck(
            checkpoint_id=record.checkpoint_id,
        )
        assert mailbox.try_put_checkpoint_ack(ack) is True
        return record.reason


def _persist_terminal(
    module: ModuleType,
    mailbox: _MailboxPort,
    actor: _Actor,
    store: _CheckpointStore | None = None,
) -> str:
    checkpoint_store = _CheckpointStore() if store is None else store
    reason = checkpoint_store.persist_terminal(module, mailbox)
    assert actor.poll_checkpoint_ack() is True
    return reason


def _tree() -> ast.Module:
    return ast.parse(TEMPLATE.read_text(encoding="utf-8"), filename=str(TEMPLATE))


def _module() -> ModuleType:
    existing = sys.modules.get("nt_evomap_advisory_actor")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location("nt_evomap_advisory_actor", TEMPLATE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _call_name(call: ast.Call) -> str:
    function = call.func
    if isinstance(function, ast.Attribute):
        return function.attr
    if isinstance(function, ast.Name):
        return function.id
    return ""


def _request(
    module: ModuleType,
    request_id: str = "request-1",
    request_sequence: int = 1,
):
    return module.AdvisoryRequest(
        request_id=request_id,
        request_sequence=request_sequence,
        artifact_hash="artifact-hash",
        deadline_ns=100,
    )


def _result(
    module: ModuleType,
    request_id: str = "request-1",
    suggestion_id: str = "suggestion-1",
    suggestion_hash: str = "suggestion-hash",
    request_sequence: int = 1,
):
    return module.AdvisoryResult(
        request_id=request_id,
        request_sequence=request_sequence,
        suggestion_id=suggestion_id,
        artifact_hash="artifact-hash",
        suggestion_hash=suggestion_hash,
        received_ns=50,
    )


def _decision(
    module: ModuleType,
    request_id: str = "request-1",
    suggestion_id: str = "suggestion-1",
    suggestion_hash: str = "suggestion-hash",
    *,
    approved: bool = True,
    decided_ns: int = 60,
):
    return module.AdvisoryDecision(
        request_id=request_id,
        suggestion_id=suggestion_id,
        suggestion_hash=suggestion_hash,
        approved=approved,
        decided_ns=decided_ns,
    )


def _actor_with_mailbox(module: ModuleType, mailbox: _MailboxPort) -> _Actor:
    actor = module.AdvisoryBridgeActor(module.AdvisoryBridgeActorConfig())
    actor._mailbox = mailbox
    return actor


def test_ai_advisory_template_defines_required_boundary_types() -> None:
    definitions = {
        node.name
        for node in _tree().body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
    }

    assert REQUIRED_TYPES <= definitions


def test_ai_advisory_actor_declares_no_market_data_handlers() -> None:
    actor = next(
        node
        for node in _tree().body
        if isinstance(node, ast.ClassDef) and node.name == "AdvisoryBridgeActor"
    )
    methods = {node.name for node in actor.body if isinstance(node, ast.FunctionDef)}

    assert methods.isdisjoint(FORBIDDEN_HANDLERS)


def test_ai_advisory_template_contains_no_forbidden_capability_calls() -> None:
    tree = _tree()
    calls = {_call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)}
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )

    assert calls.isdisjoint(FORBIDDEN_CALLS)
    assert not {
        imported
        for imported in imports
        if any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for forbidden in FORBIDDEN_IMPORT_ROOTS
        )
    }


def test_advisory_config_preserves_v2_base_fields() -> None:
    module = _module()
    actor_id = ActorId("ADVISORY-001")

    config = module.AdvisoryBridgeActorConfig(
        actor_id=actor_id,
        log_events=False,
        log_commands=False,
        mailbox_capacity=8,
        poll_interval_ms=250,
    )

    assert config.actor_id == actor_id
    assert config.log_events is False
    assert config.log_commands is False
    assert config.mailbox_capacity == 8
    assert config.poll_interval_ms == 250
    assert config.request_sequence_floor == 0


def test_advisory_records_are_frozen_and_slotted() -> None:
    module = _module()
    records = (
        _request(module),
        _result(module),
        _decision(module),
        module.AdvisoryAuditRecord(
            request_id="request-1",
            request_sequence=1,
            suggestion_id="suggestion-1",
            suggestion_hash="suggestion-hash",
            outcome="staged",
            reason="ready_for_review",
            recorded_ns=50,
        ),
    )

    for record in records:
        assert hasattr(type(record), "__dataclass_fields__")
        assert not hasattr(record, "__dict__")
        def mutate(candidate=record) -> None:
            candidate.request_id = "changed"

        with pytest.raises((FrozenInstanceError, AttributeError)):
            mutate()


def test_advisory_mailbox_rejects_write_when_capacity_is_exhausted() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=1)
    first = _request(module)

    assert mailbox.try_put_request(first) is True
    assert mailbox.try_put_request(_request(module, "request-2", 2)) is False
    assert mailbox.try_take_request() == first


def test_advisory_result_is_staged_without_becoming_actionable() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    request = _request(module)

    assert actor.request_review(request) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert actor.staged_result == _result(module)
    assert actor.authority is module.AdvisoryAuthority.NONE


def test_advisory_approval_rejects_each_identity_mismatch() -> None:
    module = _module()
    mutations = (
        (_decision(module, request_id="wrong"), "request_id_mismatch"),
        (_decision(module, suggestion_id="wrong"), "suggestion_id_mismatch"),
        (_decision(module, suggestion_hash="wrong"), "suggestion_hash_mismatch"),
    )

    for decision, reason in mutations:
        mailbox = module.AdvisoryMailboxPort(capacity=4)
        actor = _actor_with_mailbox(module, mailbox)
        assert actor.request_review(_request(module)) is True
        assert mailbox.try_put_result(_result(module)) is True
        assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
        assert persist_audit(mailbox).reason == "ready_for_review"

        assert actor.approve(decision) is False
        assert actor.authority is module.AdvisoryAuthority.NONE
        assert persist_audit(mailbox).reason == reason


def test_advisory_approval_grants_only_offline_change_review_authority() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"

    assert actor.approve(_decision(module)) is True
    assert _persist_terminal(module, mailbox, actor) == "offline_change_review"
    assert actor.authority is module.AdvisoryAuthority.OFFLINE_CHANGE_REVIEW


def test_approved_review_releases_actor_for_next_request() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"

    assert actor.approve(_decision(module)) is True
    assert _persist_terminal(module, mailbox, actor) == "offline_change_review"
    assert actor.staged_result is None
    next_request = module.AdvisoryRequest(
        request_id="request-2",
        request_sequence=2,
        artifact_hash="artifact-hash",
        deadline_ns=300,
    )
    assert actor.request_review(next_request) is True


def test_rejected_review_releases_actor_for_next_request() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"

    assert actor.approve(_decision(module, approved=False)) is False
    assert _persist_terminal(module, mailbox, actor) == "operator_rejected"
    assert actor.staged_result is None
    assert actor.request_review(_request(module, "request-2", 2)) is True


def test_timed_out_review_releases_actor_for_next_request() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True

    assert actor.poll_result(now_ns=100) == module.AdvisoryResultStatus.TIMED_OUT
    assert _persist_terminal(module, mailbox, actor) == "request_timeout"
    assert actor.request_review(_request(module, "request-2", 2)) is True


def test_timeout_checkpoint_backpressure_keeps_request_pending() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_take_request().request_id == "request-1"
    occupied = module.AdvisoryAuditRecord(
        request_id="occupied",
        request_sequence=0,
        suggestion_id=None,
        suggestion_hash=None,
        outcome="occupied",
        reason="test_backpressure",
        recorded_ns=90,
    )
    assert mailbox._try_append_checkpoint(occupied) is True

    assert actor.poll_result(now_ns=100) == module.AdvisoryResultStatus.AUDIT_BLOCKED
    assert actor.request_review(_request(module, "request-2", 2)) is False
    assert mailbox._acknowledge_checkpoint(occupied) == occupied
    assert actor.poll_result(now_ns=101) == module.AdvisoryResultStatus.TIMED_OUT
    assert _persist_terminal(module, mailbox, actor) == "request_timeout"
    assert actor.request_review(_request(module, "request-2", 2)) is True


def test_advisory_checkpoint_backpressure_prevents_state_transition() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    occupied = module.AdvisoryAuditRecord(
        request_id="occupied",
        request_sequence=0,
        suggestion_id=None,
        suggestion_hash=None,
        outcome="occupied",
        reason="test_backpressure",
        recorded_ns=55,
    )
    assert mailbox._try_append_checkpoint(occupied) is True

    assert actor.approve(_decision(module)) is False
    assert actor.authority is module.AdvisoryAuthority.NONE
    assert actor.request_review(_request(module, "request-2", 2)) is False
    assert mailbox._acknowledge_checkpoint(occupied) == occupied
    assert actor.approve(_decision(module)) is True
    assert _persist_terminal(module, mailbox, actor) == "offline_change_review"
    assert actor.authority is module.AdvisoryAuthority.OFFLINE_CHANGE_REVIEW


def test_advisory_poll_backpressure_retains_result_until_audit_accepts() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2, audit_capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    result = _result(module)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_append_audit(
        module.AdvisoryAuditRecord(
            request_id="occupied",
            request_sequence=0,
            suggestion_id=None,
            suggestion_hash=None,
            outcome="occupied",
            reason="test_backpressure",
            recorded_ns=45,
        ),
    ) is True
    assert mailbox.try_put_result(result) is True

    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.AUDIT_BLOCKED
    assert persist_audit(mailbox).reason == "test_backpressure"
    assert actor.poll_result(now_ns=51) == module.AdvisoryResultStatus.STAGED
    assert actor.staged_result == result


def test_timely_result_replay_is_rejected() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    result = _result(module)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"

    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=51) == module.AdvisoryResultStatus.REJECTED
    assert persist_audit(mailbox).reason == "result_replay"


def test_completed_result_replay_survives_capacity_and_lifecycle_reset() -> None:
    module = _module()
    checkpoint_store = _CheckpointStore()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = module.AdvisoryBridgeActor(
        module.AdvisoryBridgeActorConfig(
            mailbox_capacity=2,
            request_sequence_floor=0,
        ),
    )
    actor._mailbox = mailbox

    first_result = None
    for sequence in range(1, 4):
        request_id = f"request-{sequence}"
        request = module.AdvisoryRequest(
            request_id=request_id,
            request_sequence=sequence,
            artifact_hash="artifact-hash",
            deadline_ns=100,
        )
        result = module.AdvisoryResult(
            request_id=request_id,
            request_sequence=sequence,
            suggestion_id=f"suggestion-{sequence}",
            artifact_hash="artifact-hash",
            suggestion_hash=f"suggestion-hash-{sequence}",
            received_ns=50,
        )
        decision = _decision(
            module,
            request_id=request_id,
            suggestion_id=f"suggestion-{sequence}",
            suggestion_hash=f"suggestion-hash-{sequence}",
        )
        assert actor.request_review(request) is True
        queued_request: _RequestRecord | None = mailbox.try_take_request()
        assert queued_request is not None
        assert queued_request.request_id == request_id
        assert mailbox.try_put_result(result) is True
        assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
        assert persist_audit(mailbox).reason == "ready_for_review"
        assert actor.approve(decision) is True
        assert actor.authority is module.AdvisoryAuthority.NONE
        assert actor.request_review(
            _request(module, f"blocked-{sequence}", sequence + 10),
        ) is False
        assert _persist_terminal(module, mailbox, actor, checkpoint_store) == "offline_change_review"
        if sequence == 1:
            first_result = result

    actor.on_reset()
    assert first_result is not None
    assert actor.request_review(
        module.AdvisoryRequest(
            request_id="request-reused",
            request_sequence=1,
            artifact_hash="artifact-hash",
            deadline_ns=200,
        ),
    ) is False
    assert mailbox.try_put_result(first_result) is True
    assert actor.poll_result(now_ns=70) == module.AdvisoryResultStatus.REJECTED
    assert persist_audit(mailbox).reason == "result_replay"

    restarted = module.AdvisoryBridgeActor(
        module.AdvisoryBridgeActorConfig(
            mailbox_capacity=2,
            request_sequence_floor=checkpoint_store.request_sequence_floor,
        ),
    )
    restarted._mailbox = mailbox
    assert mailbox.try_put_result(first_result) is True
    assert restarted.poll_result(now_ns=80) == module.AdvisoryResultStatus.REJECTED
    assert persist_audit(mailbox).reason == "result_replay"


def test_crash_before_checkpoint_ack_restores_only_durable_floor() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = module.AdvisoryBridgeActor(
        module.AdvisoryBridgeActorConfig(request_sequence_floor=4),
    )
    actor._mailbox = mailbox
    request = _request(module, "request-5", 5)
    result = _result(module, request_id="request-5", request_sequence=5)

    assert actor.request_review(request) is True
    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    assert actor.approve(_decision(module, request_id="request-5")) is True
    assert actor.request_sequence_floor == 4
    assert mailbox.try_peek_checkpoint().reason == "offline_change_review"

    restarted = module.AdvisoryBridgeActor(
        module.AdvisoryBridgeActorConfig(request_sequence_floor=4),
    )
    assert restarted.request_review(request) is True


def test_pending_checkpoint_blocks_timeout_and_survives_reset() -> None:
    module = _module()
    checkpoint_store = _CheckpointStore()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    assert actor.approve(_decision(module)) is True
    terminal = mailbox.try_peek_checkpoint()
    assert terminal.reason == "offline_change_review"

    assert actor.poll_result(now_ns=101) == module.AdvisoryResultStatus.AUDIT_BLOCKED
    assert mailbox.try_peek_checkpoint() == terminal
    actor.on_reset()
    assert actor.request_review(_request(module)) is False
    assert mailbox.try_peek_checkpoint() == terminal
    assert _persist_terminal(module, mailbox, actor, checkpoint_store) == "offline_change_review"
    assert actor.authority is module.AdvisoryAuthority.OFFLINE_CHANGE_REVIEW


def test_checkpoint_ack_must_match_exact_terminal_record() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    assert actor.approve(_decision(module)) is True
    terminal = mailbox.try_peek_checkpoint()
    assert terminal is not None

    stale_mailbox = module.AdvisoryMailboxPort(capacity=2)
    stale_actor = _actor_with_mailbox(module, stale_mailbox)
    assert stale_actor.request_review(_request(module, request_id="stale-request")) is True
    assert stale_mailbox.try_put_result(
        _result(
            module,
            request_id="stale-request",
            suggestion_id="stale-suggestion",
            suggestion_hash="stale-hash",
        ),
    ) is True
    assert stale_actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(stale_mailbox).reason == "ready_for_review"
    assert stale_actor.approve(
        _decision(
            module,
            request_id="stale-request",
            suggestion_id="stale-suggestion",
            suggestion_hash="stale-hash",
        ),
    ) is True
    stale_terminal = stale_mailbox.try_peek_checkpoint()
    assert stale_terminal is not None
    assert stale_terminal.request_sequence == terminal.request_sequence
    assert stale_terminal.outcome == terminal.outcome
    assert stale_terminal.checkpoint_id != terminal.checkpoint_id
    assert mailbox.try_put_checkpoint_ack(
        module.AdvisoryCheckpointAck(checkpoint_id=stale_terminal.checkpoint_id),
    ) is True

    assert actor.poll_checkpoint_ack() is False
    assert mailbox.try_peek_checkpoint() == terminal
    assert actor.authority is module.AdvisoryAuthority.NONE


def test_terminal_checkpoint_is_independent_from_provenance_audit_fifo() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2, audit_capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED

    assert actor.approve(_decision(module)) is True

    assert mailbox.try_peek_audit().reason == "ready_for_review"
    assert mailbox.try_peek_checkpoint().reason == "offline_change_review"
    assert not hasattr(mailbox, "try_take_checkpoint")
    assert _persist_terminal(module, mailbox, actor) == "offline_change_review"
    assert persist_audit(mailbox).reason == "ready_for_review"


def test_duplicate_decision_cannot_replace_pending_terminal_checkpoint() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    assert actor.approve(_decision(module)) is True
    terminal = mailbox.try_peek_checkpoint()
    assert terminal is not None

    assert actor.approve(_decision(module, decided_ns=61)) is False

    assert mailbox.try_peek_checkpoint() == terminal
    assert persist_audit(mailbox).reason == "decision_replay"


def test_checkpoint_id_binds_the_complete_terminal_record() -> None:
    module = _module()

    def terminal_for(request_id: str, suggestion_id: str):
        mailbox = module.AdvisoryMailboxPort(capacity=2)
        actor = _actor_with_mailbox(module, mailbox)
        assert actor.request_review(_request(module, request_id)) is True
        assert mailbox.try_put_result(
            _result(module, request_id=request_id, suggestion_id=suggestion_id),
        ) is True
        assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
        assert persist_audit(mailbox).reason == "ready_for_review"
        assert actor.approve(
            _decision(module, request_id=request_id, suggestion_id=suggestion_id),
        ) is True
        return mailbox.try_peek_checkpoint()

    first = terminal_for("request-a", "suggestion-a")
    second = terminal_for("request-b", "suggestion-b")

    assert first != second
    assert first.checkpoint_id != second.checkpoint_id


def test_failed_checkpoint_removal_does_not_advance_sequence_floor() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    assert actor.approve(_decision(module)) is True
    terminal = mailbox.try_peek_checkpoint()
    assert terminal is not None
    assert mailbox._acknowledge_checkpoint(terminal) == terminal
    assert mailbox.try_put_checkpoint_ack(
        module.AdvisoryCheckpointAck(checkpoint_id=terminal.checkpoint_id),
    ) is True

    assert actor.poll_checkpoint_ack() is False
    assert actor.request_sequence_floor == 0
    assert actor.authority is module.AdvisoryAuthority.NONE


def test_reset_preserves_ack_for_pending_durable_checkpoint() -> None:
    module = _module()
    checkpoint_store = _CheckpointStore()
    mailbox = module.AdvisoryMailboxPort(capacity=2)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"
    assert actor.approve(_decision(module)) is True
    assert checkpoint_store.persist_terminal(module, mailbox) == "offline_change_review"

    actor.on_reset()

    assert actor.poll_checkpoint_ack() is True
    assert actor.request_sequence_floor == 1
    assert actor.authority is module.AdvisoryAuthority.OFFLINE_CHANGE_REVIEW


def test_late_approval_ends_request_and_releases_actor() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"

    late = module.AdvisoryDecision(
        request_id="request-1",
        suggestion_id="suggestion-1",
        suggestion_hash="suggestion-hash",
        approved=True,
        decided_ns=100,
    )
    assert actor.approve(late) is False
    assert _persist_terminal(module, mailbox, actor) == "decision_late"
    assert actor.authority is module.AdvisoryAuthority.NONE
    assert actor.staged_result is None
    assert actor.request_review(_request(module, "request-2", 2)) is True


def test_rejected_advisory_decision_is_terminal_and_releases_actor() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert persist_audit(mailbox).reason == "ready_for_review"

    rejected = module.AdvisoryDecision(
        request_id="request-1",
        suggestion_id="suggestion-1",
        suggestion_hash="suggestion-hash",
        approved=False,
        decided_ns=60,
    )
    assert actor.approve(rejected) is False
    assert _persist_terminal(module, mailbox, actor) == "operator_rejected"
    assert actor.authority is module.AdvisoryAuthority.NONE
    assert actor.staged_result is None
    assert actor.request_review(_request(module, "request-2", 2)) is True


def test_advisory_result_at_or_after_deadline_is_rejected_as_late() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True

    assert actor.poll_result(now_ns=100) == module.AdvisoryResultStatus.LATE
    assert _persist_terminal(module, mailbox, actor) == "late_result"
    assert actor.staged_result is None


def test_advisory_result_for_timed_out_request_remains_rejected_on_replay() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    result = _result(module)
    assert actor.request_review(_request(module)) is True

    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=101) == module.AdvisoryResultStatus.LATE
    assert _persist_terminal(module, mailbox, actor) == "late_result"
    next_request = module.AdvisoryRequest(
        request_id="request-2",
        request_sequence=2,
        artifact_hash="artifact-hash",
        deadline_ns=300,
    )
    assert actor.request_review(next_request) is True
    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=200) == module.AdvisoryResultStatus.REJECTED
    assert persist_audit(mailbox).reason == "result_replay"
    assert actor.staged_result is None
