from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.idempotency import IdempotencyKey


class IdempotencyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, *, user_id, key: str) -> IdempotencyKey | None:
        return (
            self.db.query(IdempotencyKey)
            .filter(IdempotencyKey.user_id == user_id, IdempotencyKey.key == key)
            .first()
        )

    def claim(
        self,
        *,
        user_id,
        key: str,
        operation: str,
        request_hash: str,
    ) -> tuple[IdempotencyKey, bool]:
        """Atomically claim a key before any financial side effect.

        The unique constraint makes concurrent inserts serialize. The loser waits
        for the owner transaction, rolls back its failed insert, then reads the
        completed record. PROCESSING and the financial changes share one DB
        transaction, so a failed operation also releases the key via rollback.
        """
        record = IdempotencyKey(
            user_id=user_id,
            key=key,
            operation=operation,
            request_hash=request_hash,
            status="PROCESSING",
        )
        self.db.add(record)
        try:
            self.db.flush()
            return record, True
        except IntegrityError:
            self.db.rollback()
            existing = self.get(user_id=user_id, key=key)
            if existing is None:
                raise
            return existing, False

    def complete(
        self,
        record: IdempotencyKey,
        *,
        transaction_id,
        response_balance=None,
    ) -> None:
        record.transaction_id = transaction_id
        record.response_balance = response_balance
        record.status = "COMPLETED"
        self.db.flush()
