import hashlib
import json
from decimal import Decimal

from app.core.exceptions import (
    IdempotencyConflictException,
    IdempotencyInProgressException,
)


def request_fingerprint(operation: str, **payload) -> str:
    normalized = {
        key: format(value.quantize(Decimal("0.01")), ".2f")
        if isinstance(value, Decimal)
        else value
        for key, value in payload.items()
    }
    body = json.dumps(
        {"operation": operation, **normalized},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def ensure_same_request(record, operation: str, fingerprint: str) -> None:
    if record.operation != operation or record.request_hash != fingerprint:
        raise IdempotencyConflictException()


def ensure_completed(record) -> None:
    if record.status != "COMPLETED" or record.transaction_id is None:
        raise IdempotencyInProgressException()
