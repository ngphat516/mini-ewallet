

from uuid import UUID
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.db.sqlserver import get_db
from app.api.deps import get_current_user_id
from app.schemas.transaction import (
    TransferRequest,
    TransactionResponse,
    TransactionHistoryResponse,
)
from app.services.transaction_service import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/transfer", response_model=TransactionResponse)
def transfer(
    data: TransferRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=64),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return transaction_service.transfer(
        db,
        user_id,
        to_account_number=data.to_account_number,
        amount=data.amount,
        description=data.description,
        idempotency_key=idempotency_key,
    )


@router.get("/me", response_model=TransactionHistoryResponse)
def get_my_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, description="DEPOSIT | WITHDRAW | TRANSFER"),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return transaction_service.get_history(db, user_id, skip=skip, limit=limit, txn_type=type)


@router.get("/{txn_id}", response_model=TransactionResponse)
def get_transaction(
    txn_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return transaction_service.get_transaction(db, user_id, txn_id)
