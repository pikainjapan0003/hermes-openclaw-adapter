"""Fail-closed Phase 9 one-shot gate with injectable, non-runtime boundaries.

This first implementation package contains the braking system only.  The real
OpenClaw executor and version probe are intentionally unavailable and raise
``NotImplementedError``.  Tests may inject counters, a tmp-path burn ledger,
and synthetic snapshots; no route or runtime imports this module.

The mandatory gate/token-audit lock protects callers inside one process.  The
ledger's mandatory ``exclusive_lock`` supplies cross-process exclusion.  Both
layers are required; neither is a substitute for the other.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, ContextManager, NoReturn, Protocol, Sequence

from app.hash_chain import canonical_json
from app.phase9_abort import AbortScenario, RehearsalFreeze
from app.phase9_presence import PresenceInputs, PresenceResult, compute_owner_presence
from app.phase9_token import (
    ATTEMPT_NUMBER,
    IssuedToken,
    TokenPresentation,
    verify_token_presentation,
)


OPENCLAW_EXECUTION_MODE = "--local"
EXPECTED_OPENCLAW_VERSION = "OpenClaw 2026.6.1 (2e08f0f)"
PHASE9_AUDIT_SCOPE = "phase9-pre-call-burn-and-post-attempt"
COORDINATION_LOCK_TIMEOUT_SECONDS = 5.0
ALLOWED_AGENT_FLAGS = frozenset(
    {
        "--local",
        "-m",
        "--message",
        "--json",
        "--timeout",
        "--agent",
        "--model",
    }
)
FORBIDDEN_AGENT_FLAGS = frozenset(
    {
        "--deliver",
        "--channel",
        "--reply-channel",
        "--reply-to",
        "--reply-account",
    }
)
_VALUE_FLAGS = frozenset(
    {"-m", "--message", "--timeout", "--agent", "--model"}
)


class GateState(str, Enum):
    DENY_ALL = "DENY_ALL"
    CHECKING = "CHECKING"
    BURNING = "BURNING"
    ONE_SHOT_READY = "ONE_SHOT_READY"
    STARTING = "STARTING"
    CLOSED_DENY = "CLOSED_DENY"


class GateDenied(RuntimeError):
    """Payload-free terminal denial; the same rehearsal cannot be retried."""

    def __init__(self, code: str, scenario: AbortScenario) -> None:
        super().__init__(code)
        self.code = code
        self.scenario = scenario
        self.context: tuple[str, ...] = ()

    def add_context(self, detail: str) -> None:
        """Attach payload-free abort context without changing the denial."""

        self.context = (*self.context, detail)


def _find_in_flight_denial(error: BaseException) -> GateDenied | None:
    """Recover a denial masked by a failing context-manager exit."""

    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, GateDenied):
            return current
        current = current.__context__ or current.__cause__
    return None


@dataclass(frozen=True)
class ActionRequest:
    """Exact N=1 action whose canonical digest is token-bound."""

    action_name: str
    target: str
    message: str
    requested_cli_timeout_seconds: int
    gate_timeout_seconds: int
    agent_id: str | None = None
    model_id: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("action_name", "target", "message"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be non-empty")
        for field_name in (
            "requested_cli_timeout_seconds",
            "gate_timeout_seconds",
        ):
            value = getattr(self, field_name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{field_name} must be a positive integer")
        for field_name in ("agent_id", "model_id"):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field_name} must be non-empty when present")

    @property
    def effective_timeout_seconds(self) -> int:
        """Use the stricter of the CLI request and gate-owned timeout."""

        return min(
            self.requested_cli_timeout_seconds,
            self.gate_timeout_seconds,
        )

    def canonical_record(self) -> dict[str, object]:
        return {
            "action_name": self.action_name,
            "agent_id": self.agent_id,
            "cli_mode": OPENCLAW_EXECUTION_MODE,
            "delivery_enabled": False,
            "effective_timeout_seconds": self.effective_timeout_seconds,
            "message": self.message,
            "model_id": self.model_id,
            "output_mode": "json",
            "target": self.target,
        }

    def digest(self) -> str:
        return hashlib.sha256(canonical_json(self.canonical_record())).hexdigest()


def build_openclaw_argv(action: ActionRequest) -> tuple[str, ...]:
    """Build the frozen embedded-mode argv without invoking OpenClaw."""

    argv = [
        "openclaw",
        "agent",
        OPENCLAW_EXECUTION_MODE,
        "--message",
        action.message,
        "--json",
        "--timeout",
        str(action.effective_timeout_seconds),
    ]
    if action.agent_id is not None:
        argv.extend(("--agent", action.agent_id))
    if action.model_id is not None:
        argv.extend(("--model", action.model_id))
    result = tuple(argv)
    validate_openclaw_argv(result)
    return result


def validate_openclaw_argv(argv: Sequence[str]) -> None:
    """Reject unknown, delivery, channel, default-timeout, or Gateway argv."""

    if isinstance(argv, (str, bytes)) or tuple(argv[:2]) != ("openclaw", "agent"):
        raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
    seen: set[str] = set()
    index = 2
    while index < len(argv):
        token = argv[index]
        if not isinstance(token, str):
            raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
        flag = token.split("=", 1)[0]
        if flag in FORBIDDEN_AGENT_FLAGS or flag not in ALLOWED_AGENT_FLAGS:
            raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
        if "=" in token or flag in seen:
            raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
        seen.add(flag)
        if flag in _VALUE_FLAGS:
            index += 1
            if index >= len(argv) or not isinstance(argv[index], str) or not argv[index]:
                raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
            if flag == "--timeout":
                try:
                    if int(argv[index]) < 1:
                        raise ValueError
                except ValueError as exc:
                    raise GateDenied(
                        "ARGV_DENIED",
                        AbortScenario.FROZEN_INPUT_MISMATCH,
                    ) from exc
        index += 1

    if "--local" not in seen or "--json" not in seen or "--timeout" not in seen:
        raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
    if not ({"-m", "--message"} & seen) or {"-m", "--message"} <= seen:
        raise GateDenied("ARGV_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)


@dataclass(frozen=True)
class FileStateEntry:
    relative_path: str
    kind: str
    size: int
    mtime_ns: int
    content_sha256: str | None


@dataclass(frozen=True)
class FileSystemSnapshot:
    root_name: str
    entries: tuple[FileStateEntry, ...]
    digest: str


def snapshot_openclaw_state(root: Path) -> FileSystemSnapshot:
    """Read a bounded relative-path inventory; return digests, never contents."""

    try:
        resolved = root.resolve(strict=True)
        if not resolved.is_dir():
            raise OSError
        entries: list[FileStateEntry] = []
        for path in sorted(resolved.rglob("*"), key=lambda item: item.as_posix()):
            relative = path.relative_to(resolved).as_posix()
            stat = path.lstat()
            if path.is_symlink():
                kind = "symlink"
                content_digest = None
            elif path.is_dir():
                kind = "directory"
                content_digest = None
            elif path.is_file():
                kind = "file"
                content_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                kind = "other"
                content_digest = None
            entries.append(
                FileStateEntry(
                    relative_path=relative,
                    kind=kind,
                    size=stat.st_size,
                    mtime_ns=stat.st_mtime_ns,
                    content_sha256=content_digest,
                )
            )
        record = [entry.__dict__ for entry in entries]
        digest = hashlib.sha256(
            json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return FileSystemSnapshot(resolved.name, tuple(entries), digest)
    except (OSError, RuntimeError, ValueError) as exc:
        raise GateDenied(
            "OPENCLAW_STATE_SNAPSHOT_FAILED",
            AbortScenario.PREFLIGHT_DRIFT,
        ) from exc


def compare_snapshots(
    before: FileSystemSnapshot,
    after: FileSystemSnapshot,
) -> tuple[str, ...]:
    """Return every changed relative entry; an empty tuple means identical."""

    old = {entry.relative_path: entry for entry in before.entries}
    new = {entry.relative_path: entry for entry in after.entries}
    return tuple(
        name
        for name in sorted(set(old) | set(new))
        if old.get(name) != new.get(name)
    )


@dataclass(frozen=True)
class FreshChallenge:
    challenge_id: str
    rehearsal_id: str
    approval_packet_hash: str
    action_hash: str
    issued_at: datetime
    deadline: datetime


@dataclass(frozen=True)
class Phase9AuditAuthorizationRecord:
    """Non-secret citation; a separate verifier must authenticate the record."""

    record_id: str
    rehearsal_id: str
    scope: str
    owner_instruction_digest: str
    authorized_at: datetime
    valid_until: datetime


@dataclass(frozen=True)
class BurnRecord:
    rehearsal_id: str
    approval_packet_hash: str
    action_hash: str
    token_digest: str
    binding_hash: str
    burned_at: datetime
    attempt_number: int
    owner_presence_demonstrated: bool
    owner_verbatim_authorization_verified: bool
    owner_instruction_digest: str
    authorization_record_id: str

    def safe_record(self) -> dict[str, object]:
        return {
            "action_hash": self.action_hash,
            "approval_packet_hash": self.approval_packet_hash,
            "attempt_number": self.attempt_number,
            "authorization_record_id": self.authorization_record_id,
            "binding_hash": self.binding_hash,
            "burned_at": self.burned_at.astimezone(timezone.utc).isoformat(),
            "owner_presence_demonstrated": self.owner_presence_demonstrated,
            "owner_verbatim_authorization_verified": (
                self.owner_verbatim_authorization_verified
            ),
            "owner_instruction_digest": self.owner_instruction_digest,
            "rehearsal_id": self.rehearsal_id,
            "token_digest": self.token_digest,
        }


@dataclass(frozen=True)
class BurnReceipt:
    token_digest: str
    record_digest: str
    durable: bool
    verified: bool


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int | None
    timed_out: bool
    stdout_digest: str
    stderr_digest: str


@dataclass(frozen=True)
class GateRequest:
    issued_token: IssuedToken
    token_presentation: TokenPresentation
    action: ActionRequest
    system_display_strings: tuple[str, ...]
    initial_challenge_id: str
    session_active: bool
    phase9_audit_authorization: Phase9AuditAuthorizationRecord | None


@dataclass(frozen=True)
class GateResult:
    state: GateState
    completion_class: str
    argv: tuple[str, ...]
    effective_timeout_seconds: int
    burn_receipt: BurnReceipt
    execution_result: ExecutionResult
    presence: PresenceResult
    filesystem_before_digest: str
    filesystem_after_digest: str
    filesystem_changes: tuple[str, ...]
    trace: tuple[str, ...]
    retry_permitted: bool = False


class BooleanGateVerifier(Protocol):
    def verify(self, request: GateRequest) -> bool:
        """Return a freshly computed contract or preflight result."""


class AuditAuthorizationVerifier(Protocol):
    def verify(
        self,
        record: Phase9AuditAuthorizationRecord,
        *,
        rehearsal_id: str,
        action_hash: str,
        now: datetime,
    ) -> bool:
        """Authenticate the separately granted Phase 9 audit scope."""


class BurnLedger(Protocol):
    @property
    def target(self) -> Path:
        """Expose the injected persistence target for scope inspection."""

    def exclusive_lock(
        self,
        *,
        timeout_seconds: float,
    ) -> ContextManager[None]:
        """Provide cross-process exclusion; a process-local lock is insufficient."""

    def contains(self, token_digest: str) -> bool:
        """Return whether the durable replay barrier already contains a digest."""

    def commit(self, record: BurnRecord) -> BurnReceipt:
        """Durably append and verify one redacted burn record."""


class GateTokenAuditCoordinationLock(Protocol):
    """Process-local half of the gate/token-audit coordination boundary."""

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Acquire within the bounded timeout or return false."""

    def release(self) -> None:
        """Release a successfully acquired lock."""


class VersionProbe(Protocol):
    def probe_version(self) -> str:
        """Return the freshly observed OpenClaw identity."""


class Snapshotter(Protocol):
    def snapshot(self) -> FileSystemSnapshot:
        """Return the current read-only OpenClaw-state snapshot."""


class PresenceChannel(Protocol):
    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        """Collect fresh evidence without returning any raw secret."""


class Executor(Protocol):
    @property
    def test_double(self) -> bool:
        """True only for an in-memory or controlled fake executor."""

    def execute(
        self,
        argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        """Issue exactly one injected foreground attempt."""


class OwnerAuthorizedOpenClawExecutor:
    """Placeholder for a later package with separate execution authorization."""

    test_double = False

    def execute(
        self,
        argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        del argv, timeout_seconds
        raise NotImplementedError("需 Owner 執行授權")


class OwnerAuthorizedOpenClawVersionProbe:
    """Placeholder: this package must not execute even the version subcommand."""

    def probe_version(self) -> str:
        raise NotImplementedError("需 Owner 執行授權")


class DirectorySnapshotter:
    """Read-only snapshotter with an injectable root for tmp-path tests."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def snapshot(self) -> FileSystemSnapshot:
        return snapshot_openclaw_state(self._root)


def _normalize_authorization(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def verify_owner_authorization_text(
    candidate: str,
    *,
    action_name: str,
    target: str,
    system_display_strings: Sequence[str],
) -> str:
    """Check bindings and literal-copy exclusion; never claim human authorship."""

    normalized = _normalize_authorization(candidate)
    if not normalized:
        raise GateDenied("OWNER_AUTHORIZATION_DENIED", AbortScenario.OWNER_STOP_OR_DISCONNECT)
    if _normalize_authorization(action_name) not in normalized:
        raise GateDenied("OWNER_AUTHORIZATION_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
    if _normalize_authorization(target) not in normalized:
        raise GateDenied("OWNER_AUTHORIZATION_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)
    displayed = {_normalize_authorization(value) for value in system_display_strings}
    if normalized in displayed:
        raise GateDenied("OWNER_AUTHORIZATION_DENIED", AbortScenario.RAW_TOKEN_EXPOSURE)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class Phase9Gate:
    """One-use gate whose current real-runtime path remains unavailable."""

    def __init__(
        self,
        *,
        rehearsal_id: str,
        contract_verifier: BooleanGateVerifier,
        preflight_verifier: BooleanGateVerifier,
        audit_authorization_verifier: AuditAuthorizationVerifier | None,
        burn_ledger: BurnLedger,
        version_probe: VersionProbe,
        snapshotter: Snapshotter,
        presence_channel: PresenceChannel,
        executor: Executor,
        clock: Callable[[], datetime],
        gate_token_audit_coordination_lock: GateTokenAuditCoordinationLock,
        challenge_bytes: Callable[[int], bytes] = secrets.token_bytes,
    ) -> None:
        self.rehearsal_id = rehearsal_id
        self.contract_verifier = contract_verifier
        self.preflight_verifier = preflight_verifier
        self.audit_authorization_verifier = audit_authorization_verifier
        self.burn_ledger = burn_ledger
        self.version_probe = version_probe
        self.snapshotter = snapshotter
        self.presence_channel = presence_channel
        self.executor = executor
        self.clock = clock
        self.challenge_bytes = challenge_bytes
        self.gate_token_audit_coordination_lock = gate_token_audit_coordination_lock
        self.freeze = RehearsalFreeze(rehearsal_id)
        self.state = GateState.DENY_ALL
        self.trace: list[str] = []
        self.coordination_lock_poisoned = False

    def _closed_denial(self, code: str, scenario: AbortScenario) -> GateDenied:
        self.freeze.reject()
        self.state = GateState.CLOSED_DENY
        self.trace.append("CLOSED_DENY")
        return GateDenied(code, scenario)

    def _deny(self, code: str, scenario: AbortScenario) -> NoReturn:
        raise self._closed_denial(code, scenario)

    def _utc_now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None or value.utcoffset() is None:
            self._deny("CLOCK_UNVERIFIED", AbortScenario.PREFLIGHT_DRIFT)
        return value.astimezone(timezone.utc)

    def _second_challenge(self, request: GateRequest, now: datetime) -> FreshChallenge:
        nonce = self.challenge_bytes(32)
        if not isinstance(nonce, bytes) or len(nonce) != 32:
            self._deny("CHALLENGE_FAILED", AbortScenario.OOB_ISOLATION_DRIFT)
        binding = request.issued_token.binding
        material = b"\0".join(
            (
                nonce,
                self.rehearsal_id.encode("utf-8"),
                binding.approval_packet_hash.encode("ascii"),
                binding.action_hash.encode("ascii"),
            )
        )
        challenge_id = hashlib.sha256(material).hexdigest()
        if challenge_id == request.initial_challenge_id:
            self._deny("CHALLENGE_REUSED", AbortScenario.OOB_ISOLATION_DRIFT)
        return FreshChallenge(
            challenge_id=challenge_id,
            rehearsal_id=self.rehearsal_id,
            approval_packet_hash=binding.approval_packet_hash,
            action_hash=binding.action_hash,
            issued_at=now,
            deadline=now + timedelta(seconds=60),
        )

    def _audit_authorized(self, request: GateRequest, now: datetime) -> bool:
        record = request.phase9_audit_authorization
        verifier = self.audit_authorization_verifier
        if record is None or verifier is None:
            return False
        if (
            record.scope != PHASE9_AUDIT_SCOPE
            or record.rehearsal_id != self.rehearsal_id
            or record.valid_until <= now
            or record.authorized_at > now
        ):
            return False
        return verifier.verify(
            record,
            rehearsal_id=self.rehearsal_id,
            action_hash=request.action.digest(),
            now=now,
        )

    def run(
        self,
        request: GateRequest,
        *,
        presented_raw_token: str,
        owner_authorization_text: str,
    ) -> GateResult:
        """Evaluate, burn, and call one injected test executor at most once."""

        if self.freeze.frozen or self.state is not GateState.DENY_ALL:
            self._deny("REHEARSAL_FROZEN", AbortScenario.SECOND_START_OR_RETRY)
        if request.issued_token.binding.rehearsal_id != self.rehearsal_id:
            self._deny("FROZEN_INPUT_MISMATCH", AbortScenario.FROZEN_INPUT_MISMATCH)

        self.state = GateState.CHECKING
        self.trace.append("1:DENY_ALL_TO_CHECKING")
        if not self.contract_verifier.verify(request):
            self._deny("CONTRACT_DENIED", AbortScenario.CLI_INTERFACE_UNVERIFIED)
        self.trace.append("2:CONTRACTS_VERIFIED")

        action_hash = request.action.digest()
        binding = request.issued_token.binding
        if (
            binding.action_hash != action_hash
            or request.token_presentation.action_hash != action_hash
        ):
            self._deny("FROZEN_INPUT_MISMATCH", AbortScenario.FROZEN_INPUT_MISMATCH)
        self.trace.append("3:HASHES_RECOMPUTED")
        self.trace.append("4:PHASE9_CONTRACT_ACCEPTED")

        try:
            instruction_digest = verify_owner_authorization_text(
                owner_authorization_text,
                action_name=request.action.action_name,
                target=request.action.target,
                system_display_strings=request.system_display_strings,
            )
        except GateDenied as exc:
            self._deny(exc.code, exc.scenario)
        self.trace.append("5:OWNER_PROCEDURE_CHECKED")

        token_result = verify_token_presentation(
            issued_token=request.issued_token,
            presented_raw_value=presented_raw_token,
            presentation=request.token_presentation,
            now=self._utc_now(),
            session_active=request.session_active,
        )
        if not token_result.valid:
            self._deny("TOKEN_DENIED", AbortScenario.TOKEN_INVALID_OR_REPLAYED)
        self.trace.append("6:TOKEN_VERIFIED")

        if not self.preflight_verifier.verify(request):
            self._deny("PREFLIGHT_DENIED", AbortScenario.PREFLIGHT_DRIFT)
        try:
            observed_version = self.version_probe.probe_version()
        except NotImplementedError:
            self._deny("EXECUTION_AUTHORIZATION_MISSING", AbortScenario.CLI_INTERFACE_UNVERIFIED)
        if observed_version != EXPECTED_OPENCLAW_VERSION:
            self._deny("OPENCLAW_VERSION_DRIFT", AbortScenario.CLI_INTERFACE_UNVERIFIED)
        try:
            argv = build_openclaw_argv(request.action)
            before = self.snapshotter.snapshot()
        except GateDenied as exc:
            self._deny(exc.code, exc.scenario)
        authorization_check_time = self._utc_now()
        if not self._audit_authorized(request, authorization_check_time):
            self._deny("PHASE9_AUDIT_AUTHORIZATION_MISSING", AbortScenario.PRECALL_AUDIT_FAILURE)
        if self.executor.test_double is not True:
            self._deny("EXECUTION_AUTHORIZATION_MISSING", AbortScenario.CLI_INTERFACE_UNVERIFIED)
        self.trace.append("7:PREFLIGHT_REVALIDATED")

        challenge = self._second_challenge(request, self._utc_now())
        presence_inputs = self.presence_channel.collect_after_second_challenge(challenge)
        self.trace.append("8:SECOND_CHALLENGE_COMPLETED")
        presence = compute_owner_presence(
            presence_inputs,
            now=self._utc_now(),
            final_challenge_issued_at=challenge.issued_at,
        )
        if not presence.owner_synchronously_present:
            self._deny("OWNER_PRESENCE_DENIED", AbortScenario.OOB_ISOLATION_DRIFT)
        self.trace.append("9:SIX_PREDICATES_RECOMPUTED")

        authorization_record = request.phase9_audit_authorization
        if authorization_record is None:
            self._deny(
                "PHASE9_AUDIT_AUTHORIZATION_MISSING",
                AbortScenario.PRECALL_AUDIT_FAILURE,
            )
        # Only this non-secret digest is retained.  The equality check above
        # detects literal copying; it does not prove who authored the sentence.
        if len(instruction_digest) != 64:
            self._deny("OWNER_AUTHORIZATION_DENIED", AbortScenario.FROZEN_INPUT_MISMATCH)

        coordination_lock_release_required = False
        receipt: BurnReceipt | None = None
        pending_denial: GateDenied | None = None
        # Both lock layers protect the pre-call audit burn boundary.  Any
        # acquisition, ledger-context, or release failure therefore maps to
        # PRECALL_AUDIT_FAILURE and closes the rehearsal before execution.
        try:
            try:
                # Set before acquire so a non-conforming lock that acquires and
                # then raises still receives a best-effort release in finally.
                coordination_lock_release_required = True
                coordination_lock_acquired = (
                    self.gate_token_audit_coordination_lock.acquire(
                        timeout=COORDINATION_LOCK_TIMEOUT_SECONDS
                    )
                )
            except Exception:
                pending_denial = self._closed_denial(
                    "COORDINATION_LOCK_FAILED",
                    AbortScenario.PRECALL_AUDIT_FAILURE,
                )
            else:
                if not coordination_lock_acquired:
                    coordination_lock_release_required = False
                    pending_denial = self._closed_denial(
                        "COORDINATION_LOCK_UNAVAILABLE",
                        AbortScenario.PRECALL_AUDIT_FAILURE,
                    )

            if pending_denial is None:
                try:
                    with self.burn_ledger.exclusive_lock(
                        timeout_seconds=COORDINATION_LOCK_TIMEOUT_SECONDS
                    ):
                        if self.burn_ledger.contains(binding.nonce_digest):
                            self._deny(
                                "TOKEN_ALREADY_BURNED",
                                AbortScenario.TOKEN_INVALID_OR_REPLAYED,
                            )
                        burn = BurnRecord(
                            rehearsal_id=self.rehearsal_id,
                            approval_packet_hash=binding.approval_packet_hash,
                            action_hash=action_hash,
                            token_digest=binding.nonce_digest,
                            binding_hash=binding.digest(),
                            burned_at=self._utc_now(),
                            attempt_number=ATTEMPT_NUMBER,
                            owner_presence_demonstrated=(
                                presence.owner_presence_demonstrated
                            ),
                            owner_verbatim_authorization_verified=(
                                presence.owner_verbatim_authorization_verified
                            ),
                            owner_instruction_digest=instruction_digest,
                            authorization_record_id=authorization_record.record_id,
                        )
                        self.state = GateState.BURNING
                        receipt = self.burn_ledger.commit(burn)
                        if (
                            receipt.token_digest != binding.nonce_digest
                            or not receipt.durable
                            or not receipt.verified
                            or not self.burn_ledger.contains(binding.nonce_digest)
                        ):
                            self._deny(
                                "BURN_VERIFY_FAILED",
                                AbortScenario.PRECALL_AUDIT_FAILURE,
                            )
                except GateDenied as exc:
                    pending_denial = exc
                except Exception as exc:
                    masked_denial = _find_in_flight_denial(exc)
                    if masked_denial is not None:
                        masked_denial.add_context("LEDGER_LOCK_EXIT_FAILED")
                        pending_denial = masked_denial
                    else:
                        code = (
                            "BURN_VERIFY_FAILED"
                            if receipt is not None
                            else "BURN_WRITE_FAILED"
                        )
                        pending_denial = self._closed_denial(
                            code,
                            AbortScenario.PRECALL_AUDIT_FAILURE,
                        )
        finally:
            if coordination_lock_release_required:
                try:
                    self.gate_token_audit_coordination_lock.release()
                except Exception:
                    self.coordination_lock_poisoned = True
                    self.trace.append("COORDINATION_LOCK_POISONED")
                    if pending_denial is not None:
                        pending_denial.add_context("COORDINATION_LOCK_RELEASE_FAILED")
                    else:
                        pending_denial = self._closed_denial(
                            "COORDINATION_LOCK_RELEASE_FAILED",
                            AbortScenario.PRECALL_AUDIT_FAILURE,
                        )
                        pending_denial.add_context("COORDINATION_LOCK_POISONED")
        if pending_denial is not None:
            raise pending_denial
        if receipt is None:
            self._deny("BURN_VERIFY_FAILED", AbortScenario.PRECALL_AUDIT_FAILURE)
        self.trace.append("10:BURN_DURABLE_AND_VERIFIED")

        self.state = GateState.ONE_SHOT_READY
        self.trace.append("11:ONE_SHOT_CAPABILITY_CREATED")
        try:
            validate_openclaw_argv(argv)
        except GateDenied as exc:
            self._deny(exc.code, exc.scenario)
        if request.action.digest() != action_hash:
            self._deny("FROZEN_INPUT_MISMATCH", AbortScenario.FROZEN_INPUT_MISMATCH)
        self.trace.append("12:ARGV_REVALIDATED")

        self.state = GateState.STARTING
        self.trace.append("13:ONE_SHOT_CONSUMED")
        try:
            execution_result = self.executor.execute(
                argv,
                timeout_seconds=request.action.effective_timeout_seconds,
            )
        finally:
            self.freeze.freeze()
            self.state = GateState.CLOSED_DENY
            self.trace.append("14:CLOSED_DENY")

        after = self.snapshotter.snapshot()
        changes = compare_snapshots(before, after)
        completion = "SIDE_EFFECT_DRIFT" if changes else "COMPLETED"
        self.trace.append("15:POST_ATTEMPT_EVIDENCE_COMPUTED")
        return GateResult(
            state=self.state,
            completion_class=completion,
            argv=argv,
            effective_timeout_seconds=request.action.effective_timeout_seconds,
            burn_receipt=receipt,
            execution_result=execution_result,
            presence=presence,
            filesystem_before_digest=before.digest,
            filesystem_after_digest=after.digest,
            filesystem_changes=changes,
            trace=tuple(self.trace),
        )
