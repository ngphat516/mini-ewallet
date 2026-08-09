
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime



class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=9, max_length=15)
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("phone")
    @classmethod
    def phone_must_be_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Số điện thoại chỉ được chứa chữ số")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ số")
        return v



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)



class UserResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    phone: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SessionResponse(BaseModel):
    session_id: UUID
    device_name: str
    ip_address: str | None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_current: bool = False

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
