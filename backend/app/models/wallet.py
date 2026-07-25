import uuid
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.db.sqlserver import Base


class Wallet(Base):
    __tablename__ = "Wallets"

    # SQL: wallet_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID()
    wallet_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=uuid.uuid4,
    )

    # SQL: user_id UNIQUEIDENTIFIER NOT NULL UNIQUE FOREIGN KEY REFERENCES Users(user_id)
    user_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("Users.user_id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # SQL: account_number VARCHAR(12) NOT NULL UNIQUE
    account_number = Column(String(12), nullable=False, unique=True)

    # SQL: balance DECIMAL(18,2) NOT NULL DEFAULT 0
    balance = Column(Numeric(18, 2), nullable=False, default=Decimal("0"))

    # SQL: currency VARCHAR(3) NOT NULL DEFAULT 'VND'
    currency = Column(String(3), nullable=False, server_default=text("'VND'"))

    # SQL: status VARCHAR(20) NOT NULL DEFAULT 'active'  -- active | frozen | closed
    status = Column(String(20), nullable=False, server_default=text("'ACTIVE'"))

    # SQL: created_at/updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
    created_at = Column(DateTime, nullable=False, server_default=text("GETDATE()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("GETDATE()"))
