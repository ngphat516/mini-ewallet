
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from uuid import UUID
from datetime import datetime


class DepositRequest(BaseModel):
    amount: Decimal = Field(..., max_digits=18, decimal_places=2)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        return v


class WithdrawRequest(DepositRequest):
    pass


class WalletResponse(BaseModel):
    wallet_id: UUID
    user_id: UUID
    account_number: str
    balance: Decimal
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
