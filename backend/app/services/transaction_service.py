
from decimal import Decimal
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.repositories.wallet_repo import WalletRepository
from app.repositories.transaction_repo import TransactionRepository, generate_reference_code
from app.core.exceptions import (
    WalletNotFoundException,
    WalletFrozenException,
    InsufficientBalanceException,
    TransactionNotFoundException,
    RecipientWalletNotFoundException,
    RecipientWalletFrozenException,
    SameWalletTransferException,
)
from app.schemas.transaction import TransactionResponse, TransactionHistoryResponse
from app.repositories.idempotency_repo import IdempotencyRepository
from app.services.idempotency_service import (
    request_fingerprint,
    ensure_same_request,
    ensure_completed,
)


class TransactionService:
    # ── Ghi sổ cho DEPOSIT/WITHDRAW ──────────────────
    # Được wallet_service gọi ngay trong CÙNG transaction DB với việc cập nhật
    # số dư, để balance và lịch sử giao dịch luôn khớp nhau.
    def record_deposit(
        self, db: Session, wallet: Wallet, amount: Decimal, balance_before: Decimal
    ):
        repo = TransactionRepository(db)
        return repo.create(
            txn_type="DEPOSIT",
            amount=amount,
            to_wallet_id=wallet.wallet_id,
            to_balance_before=balance_before,
            to_balance_after=wallet.balance,
        )

    def record_withdraw(
        self, db: Session, wallet: Wallet, amount: Decimal, balance_before: Decimal
    ):
        repo = TransactionRepository(db)
        return repo.create(
            txn_type="WITHDRAW",
            amount=amount,
            from_wallet_id=wallet.wallet_id,
            from_balance_before=balance_before,
            from_balance_after=wallet.balance,
        )

    # ── Chuyển tiền giữa 2 ví (theo số tài khoản) ───
    # Toàn bộ việc khóa ví, kiểm tra trạng thái/số dư và cập nhật số dư + ghi
    # Transactions do stored procedure sp_Transfer đảm nhiệm nguyên tử ở tầng DB
    # (xem 01_schema.sql) — Python chỉ resolve wallet_id và dịch lỗi trả về.
    def transfer(
        self,
        db: Session,
        user_id,
        to_account_number: str,
        amount: Decimal,
        idempotency_key: str,
        description: str | None = None,
    ) -> TransactionResponse:
        wallet_repo = WalletRepository(db)
        repo = TransactionRepository(db)
        idem_repo = IdempotencyRepository(db)
        fingerprint = request_fingerprint(
            "TRANSFER",
            to_account_number=to_account_number,
            amount=amount,
            description=description,
        )

        idempotency, is_owner = idem_repo.claim(
            user_id=user_id,
            key=idempotency_key,
            operation="TRANSFER",
            request_hash=fingerprint,
        )
        ensure_same_request(idempotency, "TRANSFER", fingerprint)
        if not is_owner:
            ensure_completed(idempotency)
            return TransactionResponse.model_validate(
                repo.get_by_id(idempotency.transaction_id)
            )

        sender = wallet_repo.get_by_user_id(user_id)
        if not sender:
            raise WalletNotFoundException()

        recipient = wallet_repo.get_by_account_number(to_account_number)
        if not recipient:
            raise RecipientWalletNotFoundException()

        if sender.wallet_id == recipient.wallet_id:
            raise SameWalletTransferException()

        reference_code = generate_reference_code()

        try:
            repo.call_transfer_procedure(
                from_wallet_id=sender.wallet_id,
                to_wallet_id=recipient.wallet_id,
                amount=amount,
                reference_code=reference_code,
                description=description,
            )
        except DBAPIError as exc:
            db.rollback()
            error_message = str(exc.orig) if exc.orig else str(exc)
            if "SOURCE_WALLET_UNAVAILABLE" in error_message:
                raise WalletFrozenException()
            if "DEST_WALLET_UNAVAILABLE" in error_message:
                raise RecipientWalletFrozenException()
            if "INSUFFICIENT_BALANCE" in error_message:
                raise InsufficientBalanceException()
            raise

        transaction = repo.get_by_reference_code(reference_code)
        idem_repo.complete(
            idempotency,
            transaction_id=transaction.txn_id,
        )
        db.commit()
        return TransactionResponse.model_validate(transaction)

    # ── Lịch sử giao dịch của ví đang đăng nhập ─────
    def get_history(
        self,
        db: Session,
        user_id,
        skip: int = 0,
        limit: int = 20,
        txn_type: str | None = None,
    ) -> TransactionHistoryResponse:
        wallet_repo = WalletRepository(db)
        wallet = wallet_repo.get_by_user_id(user_id)
        if not wallet:
            raise WalletNotFoundException()

        repo = TransactionRepository(db)
        items = repo.list_by_wallet(wallet.wallet_id, skip=skip, limit=limit, txn_type=txn_type)
        total = repo.count_by_wallet(wallet.wallet_id, txn_type=txn_type)

        return TransactionHistoryResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[TransactionResponse.model_validate(t) for t in items],
        )

    # ── Chi tiết 1 giao dịch (chỉ chủ ví liên quan mới xem được) ─
    def get_transaction(self, db: Session, user_id, txn_id) -> TransactionResponse:
        wallet_repo = WalletRepository(db)
        wallet = wallet_repo.get_by_user_id(user_id)
        if not wallet:
            raise WalletNotFoundException()

        repo = TransactionRepository(db)
        transaction = repo.get_by_id(txn_id)
        if not transaction or wallet.wallet_id not in (
            transaction.from_wallet_id,
            transaction.to_wallet_id,
        ):
            raise TransactionNotFoundException()

        return TransactionResponse.model_validate(transaction)


transaction_service = TransactionService()
