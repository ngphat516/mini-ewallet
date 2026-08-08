
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
from app.repositories.idempotency_repo import IdempotencyRepository
from app.services.idempotency_service import (
    request_fingerprint,
    ensure_same_request,
    ensure_completed,
)


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

    def deposit(self, db: Session, user_id, amount: Decimal, idempotency_key: str) -> WalletResponse:
        repo = WalletRepository(db)
        idem_repo = IdempotencyRepository(db)
        fingerprint = request_fingerprint("DEPOSIT", amount=amount)

        idempotency, is_owner = idem_repo.claim(
            user_id=user_id,
            key=idempotency_key,
            operation="DEPOSIT",
            request_hash=fingerprint,
        )
        ensure_same_request(idempotency, "DEPOSIT", fingerprint)
        if not is_owner:
            ensure_completed(idempotency)
            wallet = repo.get_by_user_id(user_id)
            if not wallet:
                raise WalletNotFoundException()
            return WalletResponse.model_validate(wallet).model_copy(
                update={"balance": idempotency.response_balance}
            )

        wallet = repo.get_by_user_id_for_update(user_id)
        if not wallet:
            raise WalletNotFoundException()
        if wallet.status != "ACTIVE":
            raise WalletFrozenException()

        balance_before = wallet.balance
        wallet.balance += amount
        transaction = transaction_service.record_deposit(db, wallet, amount, balance_before)
        response = WalletResponse.model_validate(wallet)
        idem_repo.complete(
            idempotency,
            transaction_id=transaction.txn_id,
            response_balance=response.balance,
        )
        db.commit()

        return response

    def withdraw(self, db: Session, user_id, amount: Decimal, idempotency_key: str) -> WalletResponse:
        repo = WalletRepository(db)
        idem_repo = IdempotencyRepository(db)
        fingerprint = request_fingerprint("WITHDRAW", amount=amount)

        idempotency, is_owner = idem_repo.claim(
            user_id=user_id,
            key=idempotency_key,
            operation="WITHDRAW",
            request_hash=fingerprint,
        )
        ensure_same_request(idempotency, "WITHDRAW", fingerprint)
        if not is_owner:
            ensure_completed(idempotency)
            wallet = repo.get_by_user_id(user_id)
            if not wallet:
                raise WalletNotFoundException()
            return WalletResponse.model_validate(wallet).model_copy(
                update={"balance": idempotency.response_balance}
            )

        wallet = repo.get_by_user_id_for_update(user_id)
        if not wallet:
            raise WalletNotFoundException()
        if wallet.status != "ACTIVE":
            raise WalletFrozenException()
        if wallet.balance < amount:
            raise InsufficientBalanceException()

        balance_before = wallet.balance
        wallet.balance -= amount
        transaction = transaction_service.record_withdraw(db, wallet, amount, balance_before)
        response = WalletResponse.model_validate(wallet)
        idem_repo.complete(
            idempotency,
            transaction_id=transaction.txn_id,
            response_balance=response.balance,
        )
        db.commit()

        return response


wallet_service = WalletService()
