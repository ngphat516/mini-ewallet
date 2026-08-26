from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.repositories.wallet_repo import WalletRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, hash_token,
)
from app.core.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException,
    UnauthorizedException, RefreshTokenReuseException, UserInactiveException,
    PhoneAlreadyExistsException,
)
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse, TokenResponse, SessionResponse


def utcnow_naive() -> datetime:
    # SQL Server DATETIME2 is stored as UTC without timezone information.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AuthService:
    def register(self, db: Session, data: RegisterRequest) -> UserResponse:
        repo = UserRepository(db)
        if repo.get_by_email(data.email):
            raise UserAlreadyExistsException()
        if repo.get_by_phone(data.phone):
            raise PhoneAlreadyExistsException()

        try:
            user = repo.create(data.full_name, data.email, data.phone, hash_password(data.password))
            WalletRepository(db).create(user_id=user.user_id)
            db.commit()
        except IntegrityError:
            # The DB constraint is the final safeguard against concurrent registration.
            db.rollback()
            raise UserAlreadyExistsException("Email or phone number is already registered")
        return UserResponse.model_validate(user)

    def login(self, db: Session, data: LoginRequest, device_name: str, ip_address: str | None) -> TokenResponse:
        user = UserRepository(db).get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsException()
        if not user.is_active:
            raise UserInactiveException()

        session_id = uuid4()
        refresh_token = create_refresh_token(str(user.user_id), str(session_id))
        payload = decode_token(refresh_token, "refresh")
        RefreshTokenRepository(db).create(
            user_id=user.user_id,
            session_id=session_id,
            family_id=session_id,
            token_hash=hash_token(refresh_token),
            device_name=(device_name or "Unknown device")[:255],
            ip_address=ip_address,
            expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc).replace(tzinfo=None),
        )
        db.commit()
        return TokenResponse(
            access_token=create_access_token(str(user.user_id)),
            refresh_token=refresh_token,
        )

    def refresh(self, db: Session, raw_token: str, device_name: str, ip_address: str | None) -> TokenResponse:
        payload = decode_token(raw_token, "refresh")
        repo = RefreshTokenRepository(db)
        stored = repo.get_by_hash_for_update(hash_token(raw_token))
        if not stored or str(stored.user_id) != payload.get("sub") or str(stored.session_id) != payload.get("sid"):
            raise UnauthorizedException("Refresh token khong hop le")

        now = utcnow_naive()
        user = UserRepository(db).get_by_id(stored.user_id)
        if not user or not user.is_active:
            repo.revoke_all(stored.user_id, now, "ACCOUNT_DISABLED")
            db.commit()
            raise UserInactiveException()

        if stored.revoked_at is not None:
            if stored.revoked_reason == "ROTATED":
                repo.revoke_session(stored.user_id, stored.session_id, now, "REUSE_DETECTED")
                db.commit()
                raise RefreshTokenReuseException()
            raise UnauthorizedException("Phien dang nhap da bi thu hoi")
        if stored.expires_at <= now:
            stored.revoked_at, stored.revoked_reason = now, "EXPIRED"
            db.commit()
            raise UnauthorizedException("Refresh token da het han")

        new_token = create_refresh_token(str(stored.user_id), str(stored.session_id), str(stored.family_id))
        new_payload = decode_token(new_token, "refresh")
        replacement = repo.create(
            user_id=stored.user_id,
            session_id=stored.session_id,
            family_id=stored.family_id,
            token_hash=hash_token(new_token),
            device_name=(device_name or stored.device_name)[:255],
            ip_address=ip_address or stored.ip_address,
            expires_at=datetime.fromtimestamp(new_payload["exp"], timezone.utc).replace(tzinfo=None),
            last_used_at=now,
        )
        stored.revoked_at, stored.revoked_reason = now, "ROTATED"
        stored.replaced_by_token_id = replacement.token_id
        stored.last_used_at = now
        db.commit()
        return TokenResponse(access_token=create_access_token(str(stored.user_id)), refresh_token=new_token)

    def logout(self, db: Session, user_id: UUID, raw_token: str) -> None:
        repo = RefreshTokenRepository(db)
        stored = repo.get_by_hash_for_update(hash_token(raw_token))
        if stored and stored.user_id == user_id:
            repo.revoke_session(user_id, stored.session_id, utcnow_naive(), "LOGOUT")
            db.commit()

    def logout_all(self, db: Session, user_id: UUID) -> None:
        RefreshTokenRepository(db).revoke_all(user_id, utcnow_naive(), "LOGOUT_ALL")
        db.commit()

    def sessions(self, db: Session, user_id: UUID):
        repo = RefreshTokenRepository(db)
        return [SessionResponse(
            session_id=row.session_id,
            device_name=row.device_name,
            ip_address=row.ip_address,
            created_at=repo.session_created_at(user_id, row.session_id),
            last_used_at=row.last_used_at,
            expires_at=row.expires_at,
        ) for row in repo.active_sessions(user_id, utcnow_naive())]

    def revoke_session(self, db: Session, user_id: UUID, session_id: UUID) -> None:
        RefreshTokenRepository(db).revoke_session(user_id, session_id, utcnow_naive(), "USER_REVOKED")
        db.commit()

    def get_me(self, db: Session, user_id: UUID) -> UserResponse:
        user = UserRepository(db).get_by_id(user_id)
        if not user:
            raise UnauthorizedException()
        return UserResponse.model_validate(user)


auth_service = AuthService()
