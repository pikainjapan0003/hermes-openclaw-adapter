"""Concrete Phase 9 burn-evidence writer for the authorized audit chain.

The gate injects this adapter through its ``AuditChainWriter`` protocol.  This
module is the only Phase 9 component that imports the Phase 7 local writer;
the gate itself remains unaware of persistence details.  Successful receipts
are derived from the Phase 7 writer's fsync-and-readback result plus an
independent full-chain readback, never from optimistic defaults.
"""

from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
from typing import Any, Mapping, Protocol, cast

from app.hash_chain import entry_hash, verify_chain
from app.phase9_burn_evidence import build_phase9_burn_evidence
from app.phase9_gate import AuditChainReceipt, BurnRecord


class Phase9AuditChainWriterError(ValueError):
    """Payload-free failure at the Phase 9 audit-chain boundary."""


class _Phase7AuditWriterModule(Protocol):
    AUDIT_PATH: Path

    def read_audit_events(self) -> list[dict[str, Any]]: ...

    def append_audit_event(
        self, event: Mapping[str, Any]
    ) -> dict[str, Any]: ...


def _phase7_writer() -> _Phase7AuditWriterModule:
    """Load the one authorized persistence module without widening mypy scope."""

    return cast(
        _Phase7AuditWriterModule,
        importlib.import_module("app.audit_writer_local"),
    )


def _lower_sha256(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise Phase9AuditChainWriterError(f"{name} must be lowercase SHA-256")
    return value


def _stable_identifier(prefix: str, *parts: str) -> str:
    if any(
        not isinstance(part, str)
        or not part
        or any(character in part for character in "\x00\r\n")
        for part in parts
    ):
        raise Phase9AuditChainWriterError("audit identifier input is invalid")
    material = b"\x00".join(part.encode("utf-8") for part in parts)
    return f"{prefix}-{hashlib.sha256(material).hexdigest()}"


class LocalAuditChainWriter:
    """Append Phase 9 burn evidence through the authorized Phase 7 writer."""

    def append_burn_evidence(self, record: BurnRecord) -> AuditChainReceipt:
        if not isinstance(record, BurnRecord):
            raise Phase9AuditChainWriterError("burn evidence requires a BurnRecord")
        if record.attempt_number != 1:
            raise Phase9AuditChainWriterError("burn evidence attempt must be one")
        rehearsal_id = record.rehearsal_id
        if (
            not isinstance(rehearsal_id, str)
            or not rehearsal_id.strip()
            or any(character in rehearsal_id for character in "\x00\r\n")
        ):
            raise Phase9AuditChainWriterError("rehearsal identifier is invalid")
        approval_packet_hash = _lower_sha256(
            "approval_packet_hash", record.approval_packet_hash
        )
        action_hash = _lower_sha256("action_hash", record.action_hash)
        _lower_sha256("token_digest", record.token_digest)
        _lower_sha256("binding_hash", record.binding_hash)
        _lower_sha256("owner_instruction_digest", record.owner_instruction_digest)
        phase7_writer = _phase7_writer()

        try:
            before_entries = phase7_writer.read_audit_events()
            predecessor = entry_hash(before_entries[-1]) if before_entries else None
            audit_id = _stable_identifier("phase9-audit", rehearsal_id)
            event_id = _stable_identifier(
                "phase9-burn-event",
                rehearsal_id,
                approval_packet_hash,
                action_hash,
                str(record.attempt_number),
            )
            event = build_phase9_burn_evidence(
                record,
                audit_id=audit_id,
                event_id=event_id,
                task_id=_stable_identifier("phase9-task", action_hash),
                related_result_id=_stable_identifier(
                    "phase9-result", approval_packet_hash, action_hash
                ),
                prev_entry_hash=predecessor,
            )
            append_result = phase7_writer.append_audit_event(event)
        except Phase9AuditChainWriterError:
            raise
        except Exception as exc:
            raise Phase9AuditChainWriterError("audit-chain append failed") from exc

        expected_hash = entry_hash(event)
        result_hash = append_result.get("entry_hash")
        result_length = append_result.get("chain_length")
        result_path = append_result.get("path")
        if (
            not isinstance(result_hash, str)
            or result_hash != expected_hash
            or type(result_length) is not int
            or result_length != len(before_entries) + 1
            or append_result.get("verified") is not True
            or not isinstance(result_path, str)
        ):
            raise Phase9AuditChainWriterError("audit-chain append receipt is invalid")
        try:
            if (
                Path(result_path).resolve(strict=False)
                != Path(phase7_writer.AUDIT_PATH).resolve(strict=False)
            ):
                raise Phase9AuditChainWriterError(
                    "audit-chain append target is invalid"
                )
            final_entries = phase7_writer.read_audit_events()
        except Phase9AuditChainWriterError:
            raise
        except Exception as exc:
            raise Phase9AuditChainWriterError("audit-chain readback failed") from exc
        if (
            len(final_entries) < result_length
            or final_entries[result_length - 1] != event
            or not verify_chain(final_entries)
            or entry_hash(final_entries[result_length - 1]) != result_hash
        ):
            raise Phase9AuditChainWriterError("audit-chain readback is invalid")

        return AuditChainReceipt(
            event_id=event_id,
            entry_hash=result_hash,
            chain_length=result_length,
            durable=True,
            verified=True,
        )


__all__ = ["LocalAuditChainWriter", "Phase9AuditChainWriterError"]
