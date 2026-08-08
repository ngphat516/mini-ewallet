

from uuid import UUID
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.db.sqlserver import get_db
from app.api.deps import get_current_user_id
from app.schemas.wallet import DepositRequest, WithdrawRequest, WalletResponse
from app.services.wallet_service import wallet_service

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return wallet_service.get_wallet(db, user_id)


@router.post("/deposit", response_model=WalletResponse)
def deposit(
    data: DepositRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=64),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return wallet_service.deposit(db, user_id, data.amount, idempotency_key)


@router.post("/withdraw", response_model=WalletResponse)
def withdraw(
    data: WithdrawRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=64),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return wallet_service.withdraw(db, user_id, data.amount, idempotency_key)
