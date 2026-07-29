# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [development]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Canonical JSON validation and encoding for security-relevant identities."""

import json
import math
from typing import Any, Set


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic JSON bytes after rejecting ambiguous Python values."""

    _validate_json_value(value, active_containers=set())
    try:
        document = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (RecursionError, TypeError, ValueError) as error:
        raise ValueError("value must contain only canonical JSON types") from error
    return document.encode("utf-8")


def _validate_json_value(value: Any, active_containers: Set[int]) -> None:
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("floating-point values must be finite")
        return

    if isinstance(value, list):
        identity = id(value)
        if identity in active_containers:
            raise ValueError("cyclic JSON arrays are not supported")
        active_containers.add(identity)
        try:
            for item in value:
                _validate_json_value(item, active_containers)
        finally:
            active_containers.remove(identity)
        return

    if isinstance(value, dict):
        identity = id(value)
        if identity in active_containers:
            raise ValueError("cyclic JSON objects are not supported")
        active_containers.add(identity)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("JSON object keys must be strings")
                _validate_json_value(item, active_containers)
        finally:
            active_containers.remove(identity)
        return

    raise ValueError(f"unsupported JSON value type: {type(value).__name__}")
