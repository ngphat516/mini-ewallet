from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **values):
        token = RefreshToken(**values)
        self.db.add(token)
        self.db.flush()
        return token

    def get_by_hash_for_update(self, token_hash):
        # SQL Server ignores generic FOR UPDATE; UPDLOCK holds this row until commit.
        return self.db.query(RefreshToken).with_hint(
            RefreshToken, "WITH (UPDLOCK, ROWLOCK)", dialect_name="mssql"
        ).filter(RefreshToken.token_hash == token_hash).first()

    def active_sessions(self, user_id, now):
        rows = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None), RefreshToken.expires_at > now,
        ).order_by(RefreshToken.last_used_at.desc()).all()
        latest = {}
        for row in rows:
            latest.setdefault(row.session_id, row)
        return list(latest.values())

    def session_created_at(self, user_id, session_id):
        return self.db.query(func.min(RefreshToken.created_at)).filter(
            RefreshToken.user_id == user_id, RefreshToken.session_id == session_id,
        ).scalar()

    def revoke_session(self, user_id, session_id, now, reason):
        return self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.session_id == session_id, RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now, "revoked_reason": reason}, synchronize_session=False)

    def revoke_all(self, user_id, now, reason):
        return self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now, "revoked_reason": reason}, synchronize_session=False)
