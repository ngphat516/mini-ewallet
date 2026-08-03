
from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.wallet_repo import WalletRepository
from app.core.exceptions import (
    WalletNotFoundException,
    WalletFrozenException,
    InsufficientBalanceException,
)
from app.schemas.wallet import WalletResponse
from app.services.transaction_service import transaction_service


class WalletService:
    def get_wallet(self, db: Session, user_id) -> WalletResponse:
        repo = WalletRepository(db)

        wallet = repo.get_by_user_id(user_id)
        if not wallet:
            raise WalletNotFoundException()

        return WalletResponse.model_validate(wallet)

    def create_wallet(self, db: Session, user_id) -> WalletResponse:
        repo = WalletRepository(db)

        wallet = repo.create(user_id=user_id)
        db.commit()

        return WalletResponse.model_validate(wallet)

    def deposit(self, db: Session, user_id, amount: Decimal) -> WalletResponse:
        repo = WalletRepository(db)

        wallet = repo.get_by_user_id_for_update(user_id)
        if not wallet:
            raise WalletNotFoundException()
        if wallet.status != "ACTIVE":
            raise WalletFrozenException()

        balance_before = wallet.balance
        wallet.balance += amount
        transaction_service.record_deposit(db, wallet, amount, balance_before)
        db.commit()
        db.refresh(wallet)

        return WalletResponse.model_validate(wallet)

    def withdraw(self, db: Session, user_id, amount: Decimal) -> WalletResponse:
        repo = WalletRepository(db)

        wallet = repo.get_by_user_id_for_update(user_id)
        if not wallet:
            raise WalletNotFoundException()
        if wallet.status != "ACTIVE":
            raise WalletFrozenException()
        if wallet.balance < amount:
            raise InsufficientBalanceException()

        balance_before = wallet.balance
        wallet.balance -= amount
        transaction_service.record_withdraw(db, wallet, amount, balance_before)
        db.commit()
        db.refresh(wallet)

        return WalletResponse.model_validate(wallet)


wallet_service = WalletService()
