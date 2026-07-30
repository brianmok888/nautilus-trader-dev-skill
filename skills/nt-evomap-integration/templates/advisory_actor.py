# TEMPLATE_CLASSIFICATION: AI/advisory Python; non-production; off execution-critical paths
"""NT V2 AI advisory mailbox bridge with no trading or network authority.

An external Python proxy owns all network and model work. This actor only stages
already-produced local mailbox records for offline configuration/change review.
It never publishes market data or signals and can never authorize trading.
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Final, Self, override

from nautilus_trader.common import DataActor, DataActorConfig, TimeEvent
from nautilus_trader.model import ActorId

_MAILBOX_TIMER: Final = "advisory-mailbox"


class AdvisoryAuthority(Enum):
    """Maximum authority granted by an approved advisory suggestion."""

    NONE = "none"
    OFFLINE_CHANGE_REVIEW = "offline_change_review"


class AdvisoryResultStatus(Enum):
    """Deterministic result-consumption outcomes."""

    EMPTY = "empty"
    STAGED = "staged"
    LATE = "late"
    REJECTED = "rejected"
    AUDIT_BLOCKED = "audit_blocked"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True, slots=True)
class AdvisoryRequest:
    """Bounded request exported to the external advisory proxy."""

    request_id: str
    request_sequence: int
    artifact_hash: str
    deadline_ns: int


@dataclass(frozen=True, slots=True)
class AdvisoryResult:
    """Non-actionable suggestion returned by the external advisory proxy."""

    request_id: str
    request_sequence: int
    suggestion_id: str
    artifact_hash: str
    suggestion_hash: str
    received_ns: int


@dataclass(frozen=True, slots=True)
class AdvisoryDecision:
    """Human decision for one exact staged suggestion."""

    request_id: str
    suggestion_id: str
    suggestion_hash: str
    approved: bool
    decided_ns: int


@dataclass(frozen=True, slots=True)
class AdvisoryAuditRecord:
    """Immutable decision provenance accepted before state changes."""

    request_id: str
    request_sequence: int
    suggestion_id: str | None
    suggestion_hash: str | None
    outcome: str
    reason: str
    recorded_ns: int

    @property
    def checkpoint_id(self) -> str:
        payload = json.dumps(
            {
                "outcome": self.outcome,
                "reason": self.reason,
                "recorded_ns": self.recorded_ns,
                "request_id": self.request_id,
                "request_sequence": self.request_sequence,
                "suggestion_hash": self.suggestion_hash,
                "suggestion_id": self.suggestion_id,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class AdvisoryCheckpointAck:
    checkpoint_id: str


class AdvisoryMailboxPort:
    """Bounded, non-blocking in-memory port shared with a local proxy adapter."""

    def __init__(self, capacity: int, *, audit_capacity: int | None = None) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        resolved_audit_capacity = capacity if audit_capacity is None else audit_capacity
        if resolved_audit_capacity <= 0:
            raise ValueError("audit_capacity must be positive")
        self._requests: deque[AdvisoryRequest] = deque(maxlen=capacity)
        self._results: deque[AdvisoryResult] = deque(maxlen=capacity)
        self._audits: deque[AdvisoryAuditRecord] = deque(
            maxlen=resolved_audit_capacity,
        )
        self._checkpoints: deque[AdvisoryAuditRecord] = deque(maxlen=capacity)
        self._checkpoint_acks: deque[AdvisoryCheckpointAck] = deque(maxlen=capacity)

    def try_put_request(self, request: AdvisoryRequest) -> bool:
        """Return immediately; never discard an older request to make room."""
        if len(self._requests) == self._requests.maxlen:
            return False
        self._requests.append(request)
        return True

    def try_take_request(self) -> AdvisoryRequest | None:
        """Return the oldest request without waiting."""
        return self._requests.popleft() if self._requests else None

    def try_put_result(self, result: AdvisoryResult) -> bool:
        """Return immediately; never discard an older result to make room."""
        if len(self._results) == self._results.maxlen:
            return False
        self._results.append(result)
        return True

    def try_take_result(self) -> AdvisoryResult | None:
        """Return the oldest result without waiting."""
        return self._results.popleft() if self._results else None

    def try_restore_result(self, result: AdvisoryResult) -> None:
        self._results.appendleft(result)

    def try_append_audit(self, record: AdvisoryAuditRecord) -> bool:
        """Fail closed when durable audit transfer is backpressured."""
        if len(self._audits) == self._audits.maxlen:
            return False
        self._audits.append(record)
        return True

    def try_peek_audit(self) -> AdvisoryAuditRecord | None:
        return self._audits[0] if self._audits else None

    def acknowledge_audit(self, checkpoint_id: str) -> bool:
        record = self.try_peek_audit()
        if record is None or record.checkpoint_id != checkpoint_id:
            return False
        self._audits.popleft()
        return True

    def _try_append_checkpoint(self, record: AdvisoryAuditRecord) -> bool:
        if len(self._checkpoints) == self._checkpoints.maxlen:
            return False
        self._checkpoints.append(record)
        return True

    def try_peek_checkpoint(self) -> AdvisoryAuditRecord | None:
        return self._checkpoints[0] if self._checkpoints else None

    def try_put_checkpoint_ack(self, ack: AdvisoryCheckpointAck) -> bool:
        if len(self._checkpoint_acks) == self._checkpoint_acks.maxlen:
            return False
        self._checkpoint_acks.append(ack)
        return True

    def try_take_checkpoint_ack(self) -> AdvisoryCheckpointAck | None:
        return self._checkpoint_acks.popleft() if self._checkpoint_acks else None

    def _acknowledge_checkpoint(
        self,
        expected: AdvisoryAuditRecord,
    ) -> AdvisoryAuditRecord | None:
        record = self.try_peek_checkpoint()
        if record != expected:
            return None
        return self._checkpoints.popleft()

    def clear_runtime_queues(self) -> None:
        """Clear bridge-owned request and result queues during lifecycle reset."""
        self._requests.clear()
        self._results.clear()

    def _clear_checkpoint_acks(self) -> None:
        self._checkpoint_acks.clear()


class AdvisoryBridgeActorConfig(DataActorConfig):
    """Importable NT V2 actor configuration for local advisory mailbox polling."""

    def __new__(
        cls,
        mailbox_capacity: int = 64,
        poll_interval_ms: int = 100,
        request_sequence_floor: int = 0,
        actor_id: ActorId | None = None,
        log_events: bool = True,
        log_commands: bool = True,
    ) -> Self:
        return super().__new__(cls)

    def __init__(
        self,
        mailbox_capacity: int = 64,
        poll_interval_ms: int = 100,
        request_sequence_floor: int = 0,
        actor_id: ActorId | None = None,
        log_events: bool = True,
        log_commands: bool = True,
    ) -> None:
        super().__init__()
        self.actor_id: ActorId | None = actor_id
        self.log_events: bool = log_events
        self.log_commands: bool = log_commands
        self.mailbox_capacity: int = mailbox_capacity
        self.poll_interval_ms: int = poll_interval_ms
        self.request_sequence_floor: int = request_sequence_floor


class AdvisoryBridgeActor(DataActor):
    """Stage local advisory records for offline review, never for execution."""

    def __init__(
        self,
        config: AdvisoryBridgeActorConfig,
    ) -> None:
        super().__init__(config)
        if config.mailbox_capacity <= 0:
            raise ValueError("mailbox_capacity must be positive")
        if config.poll_interval_ms <= 0:
            raise ValueError("poll_interval_ms must be positive")
        if config.request_sequence_floor < 0:
            raise ValueError("request_sequence_floor must not be negative")
        self._config: AdvisoryBridgeActorConfig = config
        self._mailbox: AdvisoryMailboxPort = AdvisoryMailboxPort(config.mailbox_capacity)
        self._pending_request: AdvisoryRequest | None = None
        self._staged_result: AdvisoryResult | None = None
        self._staged_identity: tuple[int, str, str, str] | None = None
        self._completed_request_sequence: int = config.request_sequence_floor
        self._pending_checkpoint: AdvisoryAuditRecord | None = None
        self._pending_authority: AdvisoryAuthority = AdvisoryAuthority.NONE
        self._decision_finalized: bool = False
        self._authority: AdvisoryAuthority = AdvisoryAuthority.NONE

    @property
    def staged_result(self) -> AdvisoryResult | None:
        """Return the current non-actionable suggestion, if any."""
        return self._staged_result

    @property
    def authority(self) -> AdvisoryAuthority:
        """Return offline review authority; trading authority is unrepresentable."""
        return self._authority

    @property
    def request_sequence_floor(self) -> int:
        return self._completed_request_sequence

    @override
    def on_start(self) -> None:
        """Register one short callback that only drains the local mailbox."""
        self.clock.set_timer(
            name=_MAILBOX_TIMER,
            interval=timedelta(milliseconds=self._config.poll_interval_ms),
            callback=self._on_mailbox_tick,
        )

    @override
    def on_stop(self) -> None:
        """Stop local polling without waiting for the external proxy."""
        self.clock.cancel_timer(_MAILBOX_TIMER)

    @override
    def on_reset(self) -> None:
        """Clear staged state and return to no-authority operation."""
        self._mailbox.clear_runtime_queues()
        if self._pending_checkpoint is None:
            self._mailbox._clear_checkpoint_acks()
            self._pending_request = None
            self._staged_result = None
            self._staged_identity = None
            self._pending_authority = AdvisoryAuthority.NONE
            self._decision_finalized = False
        self._authority = AdvisoryAuthority.NONE

    @override
    def on_dispose(self) -> None:
        """Release local records; framework disposal clears clock callbacks."""
        self.on_reset()

    def request_review(self, request: AdvisoryRequest) -> bool:
        """Queue one review request without blocking or replacing older work."""
        if self._pending_request is not None:
            return False
        if request.request_sequence <= self._completed_request_sequence:
            return False
        if not self._mailbox.try_put_request(request):
            return False
        self._pending_request = request
        self._staged_result = None
        self._staged_identity = None
        self._decision_finalized = False
        self._authority = AdvisoryAuthority.NONE
        return True

    def poll_result(self, now_ns: int) -> AdvisoryResultStatus:
        """Consume at most one local result and stage it only after audit."""
        if self._pending_checkpoint is not None:
            return AdvisoryResultStatus.AUDIT_BLOCKED
        result = self._mailbox.try_take_result()
        if result is None:
            request = self._pending_request
            if request is not None and now_ns >= request.deadline_ns:
                record = AdvisoryAuditRecord(
                    request_id=request.request_id,
                    request_sequence=request.request_sequence,
                    suggestion_id=None,
                    suggestion_hash=None,
                    outcome="rejected",
                    reason="request_timeout",
                    recorded_ns=now_ns,
                )
                if not self._mailbox._try_append_checkpoint(record):
                    return AdvisoryResultStatus.AUDIT_BLOCKED
                self._decision_finalized = True
                self._pending_checkpoint = record
                return AdvisoryResultStatus.TIMED_OUT
            return AdvisoryResultStatus.EMPTY
        identity = (
            result.request_sequence,
            result.request_id,
            result.suggestion_id,
            result.suggestion_hash,
        )
        if (
            result.request_sequence <= self._completed_request_sequence
            or identity == self._staged_identity
        ):
            return self._reject_result(result, "result_replay", now_ns)
        request = self._pending_request
        if request is None:
            return self._reject_result(result, "unknown_request", now_ns)
        if now_ns >= request.deadline_ns:
            return self._reject_result(result, "late_result", now_ns)
        if result.request_id != request.request_id:
            return self._reject_result(result, "request_id_mismatch", now_ns)
        if result.request_sequence != request.request_sequence:
            return self._reject_result(result, "request_sequence_mismatch", now_ns)
        if result.artifact_hash != request.artifact_hash:
            return self._reject_result(result, "artifact_hash_mismatch", now_ns)
        record = AdvisoryAuditRecord(
            request_id=result.request_id,
            request_sequence=result.request_sequence,
            suggestion_id=result.suggestion_id,
            suggestion_hash=result.suggestion_hash,
            outcome="staged",
            reason="ready_for_review",
            recorded_ns=now_ns,
        )
        if not self._mailbox.try_append_audit(record):
            self._mailbox.try_restore_result(result)
            return AdvisoryResultStatus.AUDIT_BLOCKED
        self._staged_result = result
        self._staged_identity = identity
        return AdvisoryResultStatus.STAGED

    def approve(self, decision: AdvisoryDecision) -> bool:
        """Approve only the exact staged suggestion for offline change review."""
        result = self._staged_result
        reason = self._decision_rejection_reason(decision, result)
        request = self._pending_request
        if reason is None and self._decision_finalized:
            reason = "decision_replay"
        if reason is None and request is not None and decision.decided_ns >= request.deadline_ns:
            reason = "decision_late"
        outcome = "approved" if reason is None and decision.approved else "rejected"
        record = AdvisoryAuditRecord(
            request_id=decision.request_id,
            request_sequence=result.request_sequence if result is not None else 0,
            suggestion_id=decision.suggestion_id,
            suggestion_hash=decision.suggestion_hash,
            outcome=outcome,
            reason=reason or (
                "offline_change_review" if decision.approved else "operator_rejected"
            ),
            recorded_ns=decision.decided_ns,
        )
        terminal = reason is None or reason == "decision_late"
        append = (
            self._mailbox._try_append_checkpoint
            if terminal
            else self._mailbox.try_append_audit
        )
        if not append(record):
            return False
        if reason is None:
            self._decision_finalized = True
            self._pending_checkpoint = record
            self._pending_authority = (
                AdvisoryAuthority.OFFLINE_CHANGE_REVIEW
                if decision.approved
                else AdvisoryAuthority.NONE
            )
            return decision.approved
        if reason == "decision_late":
            self._decision_finalized = True
            self._pending_checkpoint = record
        return False

    def poll_checkpoint_ack(self) -> bool:
        ack = self._mailbox.try_take_checkpoint_ack()
        pending = self._pending_checkpoint
        if ack is None or pending is None:
            return False
        if ack.checkpoint_id != pending.checkpoint_id:
            return False
        removed = self._mailbox._acknowledge_checkpoint(pending)
        if removed is None:
            return False
        self._completed_request_sequence = max(
            self._completed_request_sequence,
            removed.request_sequence,
        )
        self._authority = self._pending_authority
        self._pending_checkpoint = None
        self._pending_authority = AdvisoryAuthority.NONE
        self._complete_request()
        return True

    def _on_mailbox_tick(self, event: TimeEvent) -> None:
        """Drain at most one already-local result in the event-loop callback."""
        if not self.poll_checkpoint_ack():
            _ = self.poll_result(now_ns=event.ts_event)

    def _reject_result(
        self,
        result: AdvisoryResult,
        reason: str,
        now_ns: int,
    ) -> AdvisoryResultStatus:
        record = AdvisoryAuditRecord(
            request_id=result.request_id,
            request_sequence=result.request_sequence,
            suggestion_id=result.suggestion_id,
            suggestion_hash=result.suggestion_hash,
            outcome="rejected",
            reason=reason,
            recorded_ns=now_ns,
        )
        append = (
            self._mailbox._try_append_checkpoint
            if reason == "late_result"
            else self._mailbox.try_append_audit
        )
        if not append(record):
            self._mailbox.try_restore_result(result)
            return AdvisoryResultStatus.AUDIT_BLOCKED
        if reason == "late_result":
            self._decision_finalized = True
            self._pending_checkpoint = record
            return AdvisoryResultStatus.LATE
        return AdvisoryResultStatus.REJECTED

    def _complete_request(self) -> None:
        self._pending_request = None
        self._staged_result = None

    @staticmethod
    def _decision_rejection_reason(
        decision: AdvisoryDecision,
        result: AdvisoryResult | None,
    ) -> str | None:
        if result is None:
            return "no_staged_result"
        if decision.request_id != result.request_id:
            return "request_id_mismatch"
        if decision.suggestion_id != result.suggestion_id:
            return "suggestion_id_mismatch"
        if decision.suggestion_hash != result.suggestion_hash:
            return "suggestion_hash_mismatch"
        return None
