import uuid
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.db.sqlserver import Base


class Transaction(Base):
    __tablename__ = "Transactions"

    # SQL: txn_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID()
    txn_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=uuid.uuid4,
    )

    # SQL: reference_code VARCHAR(30) NOT NULL UNIQUE
    reference_code = Column(String(30), nullable=False, unique=True)

    # SQL: txn_type VARCHAR(10) NOT NULL CHECK (txn_type IN ('DEPOSIT','WITHDRAW','TRANSFER'))
    txn_type = Column(String(10), nullable=False)

    # SQL: from_wallet_id UNIQUEIDENTIFIER NULL REFERENCES Wallets(wallet_id)
    # -- ví bị trừ tiền: có giá trị với WITHDRAW/TRANSFER, NULL với DEPOSIT
    from_wallet_id = Column(
        UNIQUEIDENTIFIER, ForeignKey("Wallets.wallet_id"), nullable=True, index=True
    )

    # SQL: to_wallet_id UNIQUEIDENTIFIER NULL REFERENCES Wallets(wallet_id)
    # -- ví được cộng tiền: có giá trị với DEPOSIT/TRANSFER, NULL với WITHDRAW
    to_wallet_id = Column(
        UNIQUEIDENTIFIER, ForeignKey("Wallets.wallet_id"), nullable=True, index=True
    )

    # SQL: amount DECIMAL(18,2) NOT NULL CHECK (amount > 0)
    amount = Column(Numeric(18, 2), nullable=False)

    # SQL: fee DECIMAL(18,2) NOT NULL DEFAULT 0.00  -- phí giao dịch (trừ thêm vào bên from)
    fee = Column(Numeric(18, 2), nullable=False, server_default=text("0.00"))

    # SQL: from_balance_before/after, to_balance_before/after DECIMAL(18,2) NULL
    # -- lưu lại số dư trước/sau để phục vụ đối soát, không phụ thuộc query lại lịch sử
    from_balance_before = Column(Numeric(18, 2), nullable=True)
    from_balance_after = Column(Numeric(18, 2), nullable=True)
    to_balance_before = Column(Numeric(18, 2), nullable=True)
    to_balance_after = Column(Numeric(18, 2), nullable=True)

    # SQL: status VARCHAR(10) NOT NULL DEFAULT 'SUCCESS' CHECK (status IN ('SUCCESS','FAILED'))
    status = Column(String(10), nullable=False, server_default=text("'SUCCESS'"))

    # SQL: description NVARCHAR(255) NULL
    description = Column(String(255), nullable=True)

    # SQL: created_at DATETIME2 NOT NULL DEFAULT GETDATE()
    created_at = Column(DateTime, nullable=False, server_default=text("GETDATE()"))
