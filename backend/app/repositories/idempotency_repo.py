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

    def save_completed(
        self,
        *,
        user_id,
        key: str,
        operation: str,
        request_hash: str,
        transaction_id,
        response_balance=None,
    ) -> IdempotencyKey:
        record = IdempotencyKey(
            user_id=user_id,
            key=key,
            operation=operation,
            request_hash=request_hash,
            transaction_id=transaction_id,
            response_balance=response_balance,
        )
        self.db.add(record)
        try:
            self.db.flush()
            return record
        except IntegrityError:
            self.db.rollback()
            return self.get(user_id=user_id, key=key)
