
from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.wallet_repo import WalletRepository
from app.core.exceptions import (
    WalletNotFoundException,
    WalletFrozenException,
    InsufficientBalanceException,
)
from app.schemas.wallet import WalletResponse


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

        wallet.balance += amount
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

        wallet.balance -= amount
        db.commit()
        db.refresh(wallet)

        return WalletResponse.model_validate(wallet)


wallet_service = WalletService()
