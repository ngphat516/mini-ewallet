# app/core/security.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

# ── Hash mật khẩu ─────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash mật khẩu trước khi lưu DB (một chiều, không giải mã được)"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """So sánh mật khẩu người dùng nhập với hash trong DB"""
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────
def create_access_token(user_id: str) -> str:
    """Token ngắn hạn (15 phút) dùng cho mọi request"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str, session_id: str, family_id: str | None = None) -> str:
    """Token dài hạn (7 ngày) chỉ dùng để xin access token mới"""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_EXPIRE_DAYS
    )
    payload = {
        "sub": user_id, "exp": expire, "type": "refresh",
        "jti": str(uuid4()), "sid": session_id, "fid": family_id or session_id,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def hash_token(token: str) -> str:
    """SHA-256 is safe because a signed refresh JWT has high entropy."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(token: str, expected_type: str = "access") -> dict:
    """Giải mã token, ném exception nếu hết hạn / giả mạo / sai loại"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn")

    if payload.get("type") != expected_type:
        raise UnauthorizedException("Sai loại token")
    return payload
