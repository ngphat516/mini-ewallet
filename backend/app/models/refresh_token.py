import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.db.sqlserver import Base


class RefreshToken(Base):
    __tablename__ = "RefreshTokens"
    token_id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey("Users.user_id"), nullable=False, index=True)
    session_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    family_id = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    device_name = Column(String(255), nullable=False, default="Unknown device")
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(20), nullable=True)
    replaced_by_token_id = Column(UNIQUEIDENTIFIER, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("GETUTCDATE()"))
    last_used_at = Column(DateTime, nullable=False, server_default=text("GETUTCDATE()"))
