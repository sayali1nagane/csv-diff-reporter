"""Audit trail for diff operations — records what transformations were applied."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditEntry:
    operation: str
    detail: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict:
        return {
            "operation": self.operation,
            "detail": self.detail,
            "timestamp": self.timestamp,
        }


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def record(self, operation: str, detail: str = "") -> None:
        self.entries.append(AuditEntry(operation=operation, detail=detail))

    def all(self) -> List[AuditEntry]:
        return list(self.entries)

    def clear(self) -> None:
        self.entries.clear()

    def __len__(self) -> int:
        return len(self.entries)

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def build_audit_log(operations: Optional[List[tuple]] = None) -> AuditLog:
    """Create an AuditLog, optionally pre-populated with (operation, detail) tuples."""
    log = AuditLog()
    for op in (operations or []):
        if isinstance(op, tuple) and len(op) == 2:
            log.record(op[0], op[1])
        else:
            log.record(str(op))
    return log
