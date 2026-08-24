import random
from sqlalchemy.orm import Session
from app.models.wallet import Wallet


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def _generate_account_number(self) -> str:
        while True:
            number = "".join(str(random.randint(0, 9)) for _ in range(12))
            exists = self.db.query(Wallet).filter(
                Wallet.account_number == number
            ).first()
            if not exists:
                return number

    def get_by_id(self, wallet_id) -> Wallet | None:
        return self.db.query(Wallet).filter(Wallet.wallet_id == wallet_id).first()

    def get_by_user_id(self, user_id) -> Wallet | None:
        return self.db.query(Wallet).filter(Wallet.user_id == user_id).first()

    def get_by_user_id_for_update(self, user_id) -> Wallet | None:
        # SQL Server không hỗ trợ FOR UPDATE; dùng WITH (UPDLOCK, ROWLOCK)
        # để khóa row ví cho tới khi commit, chống mất cập nhật (lost update).
        return (
            self.db.query(Wallet)
            .with_hint(Wallet, "WITH (UPDLOCK, ROWLOCK)", dialect_name="mssql")
            .filter(Wallet.user_id == user_id)
            .first()
        )

    def get_by_account_number(self, account_number: str) -> Wallet | None:
        return (
            self.db.query(Wallet)
            .filter(Wallet.account_number == account_number)
            .first()
        )

    def create(self, user_id) -> Wallet:
        wallet = Wallet(
            user_id=user_id,
            account_number=self._generate_account_number(),   
        )
        self.db.add(wallet)
        self.db.flush()
        return wallet
