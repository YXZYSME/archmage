# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Durable JSON Lines audit storage for policy and execution records."""

import json
import os
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Union

from .domain import AuditEvent, ReconciliationRecord


class JsonlAuditLogger:
    """Append structured records and sync them before returning."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        self._lock = Lock()

    def log(self, event: AuditEvent) -> None:
        self._append("policy_decision", event)

    def log_reconciliation(self, record: ReconciliationRecord) -> None:
        self._append("execution_result", record)

    def _append(
        self,
        record_type: str,
        record: Union[AuditEvent, ReconciliationRecord],
    ) -> None:
        payload: Dict[str, Any] = {
            "record_type": record_type,
            "record": asdict(record),
        }
        encoded = json.dumps(
            payload,
            default=self._serialize_value,
            separators=(",", ":"),
            sort_keys=True,
        )
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as audit_file:
                audit_file.write(encoded + "\n")
                audit_file.flush()
                os.fsync(audit_file.fileno())

    @staticmethod
    def _serialize_value(value: object) -> object:
        if isinstance(value, Enum):
            return value.value
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


# <!-- yxzys:sg:ai -->
