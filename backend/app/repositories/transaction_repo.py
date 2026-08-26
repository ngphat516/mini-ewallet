import uuid
from decimal import Decimal
from sqlalchemy import text, or_
from sqlalchemy.orm import Session
from app.models.transaction import Transaction


def generate_reference_code() -> str:
    # VARCHAR(30) trong DB -> "TXN" + 24 ký tự hex vẫn còn dư chỗ
    return f"TXN{uuid.uuid4().hex[:24].upper()}"


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, txn_id) -> Transaction | None:
        return self.db.query(Transaction).filter(Transaction.txn_id == txn_id).first()

    def get_by_reference_code(self, reference_code: str) -> Transaction | None:
        return (
            self.db.query(Transaction)
            .filter(Transaction.reference_code == reference_code)
            .first()
        )

    def list_by_wallet(
        self,
        wallet_id,
        skip: int = 0,
        limit: int = 20,
        txn_type: str | None = None,
    ) -> list[Transaction]:
        query = self.db.query(Transaction).filter(
            or_(Transaction.from_wallet_id == wallet_id, Transaction.to_wallet_id == wallet_id)
        )
        if txn_type:
            query = query.filter(Transaction.txn_type == txn_type)
        return (
            query.order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_wallet(self, wallet_id, txn_type: str | None = None) -> int:
        query = self.db.query(Transaction).filter(
            or_(Transaction.from_wallet_id == wallet_id, Transaction.to_wallet_id == wallet_id)
        )
        if txn_type:
            query = query.filter(Transaction.txn_type == txn_type)
        return query.count()

    def create(
        self,
        *,
        txn_type: str,
        amount: Decimal,
        from_wallet_id=None,
        to_wallet_id=None,
        from_balance_before: Decimal | None = None,
        from_balance_after: Decimal | None = None,
        to_balance_before: Decimal | None = None,
        to_balance_after: Decimal | None = None,
        fee: Decimal = Decimal("0.00"),
        status: str = "SUCCESS",
        description: str | None = None,
        reference_code: str | None = None,
    ) -> Transaction:
        transaction = Transaction(
            reference_code=reference_code or generate_reference_code(),
            txn_type=txn_type,
            amount=amount,
            fee=fee,
            status=status,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            from_balance_before=from_balance_before,
            from_balance_after=from_balance_after,
            to_balance_before=to_balance_before,
            to_balance_after=to_balance_after,
            description=description,
        )
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def call_transfer_procedure(
        self,
        *,
        from_wallet_id,
        to_wallet_id,
        amount: Decimal,
        reference_code: str,
        fee: Decimal = Decimal("0.00"),
        description: str | None = None,
    ) -> None:
        # sp_Transfer tự lo khóa 2 ví theo thứ tự wallet_id (chống deadlock),
        # kiểm tra trạng thái/số dư và ghi Transactions — xem 01_schema.sql.
        self.db.execute(
            text(
                "EXEC sp_Transfer "
                "@from_wallet_id = :from_wallet_id, "
                "@to_wallet_id = :to_wallet_id, "
                "@amount = :amount, "
                "@fee = :fee, "
                "@description = :description, "
                "@reference_code = :reference_code"
            ),
            {
                "from_wallet_id": str(from_wallet_id),
                "to_wallet_id": str(to_wallet_id),
                "amount": amount,
                "fee": fee,
                "description": description,
                "reference_code": reference_code,
            },
        )
