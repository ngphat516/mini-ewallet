import uuid

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from app.db.sqlserver import Base


class IdempotencyKey(Base):
    __tablename__ = "IdempotencyKeys"

    idempotency_id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UNIQUEIDENTIFIER, ForeignKey("Users.user_id"), nullable=False, index=True
    )
    key = Column(String(64), nullable=False)
    operation = Column(String(20), nullable=False)
    request_hash = Column(String(64), nullable=False)
    status = Column(String(12), nullable=False, server_default=text("'PROCESSING'"))
    transaction_id = Column(
        UNIQUEIDENTIFIER, ForeignKey("Transactions.txn_id"), nullable=True
    )
    response_balance = Column(Numeric(18, 2), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("GETDATE()"))
