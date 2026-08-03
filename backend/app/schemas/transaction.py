
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from uuid import UUID
from datetime import datetime


class TransferRequest(BaseModel):
    to_account_number: str = Field(..., min_length=12, max_length=12)
    amount: Decimal = Field(..., max_digits=18, decimal_places=2)
    description: str | None = Field(None, max_length=255)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        return v

    @field_validator("to_account_number")
    @classmethod
    def account_number_must_be_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Số tài khoản chỉ được chứa chữ số")
        return v


class TransactionResponse(BaseModel):
    txn_id: UUID
    reference_code: str
    txn_type: str
    from_wallet_id: UUID | None
    to_wallet_id: UUID | None
    amount: Decimal
    fee: Decimal
    from_balance_before: Decimal | None
    from_balance_after: Decimal | None
    to_balance_before: Decimal | None
    to_balance_after: Decimal | None
    status: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionHistoryResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[TransactionResponse]
