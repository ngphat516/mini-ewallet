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

        return (
            self.db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
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
