
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.sqlserver import get_db
from app.api.deps import get_current_user_id
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse, TokenResponse, RefreshTokenRequest, SessionResponse, MessageResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return auth_service.login(db, data, request.headers.get("user-agent", "Unknown device"), request.client.host if request.client else None)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    return auth_service.refresh(db, data.refresh_token, request.headers.get("user-agent", "Unknown device"), request.client.host if request.client else None)


@router.post("/logout", response_model=MessageResponse)
def logout(data: RefreshTokenRequest, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user_id)):
    auth_service.logout(db, user_id, data.refresh_token)
    return {"message": "Logged out"}


@router.post("/logout-all", response_model=MessageResponse)
def logout_all(db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user_id)):
    auth_service.logout_all(db, user_id)
    return {"message": "All sessions revoked"}


@router.get("/sessions", response_model=list[SessionResponse])
def sessions(db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user_id)):
    return auth_service.sessions(db, user_id)


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
def revoke_session(session_id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user_id)):
    auth_service.revoke_session(db, user_id, session_id)
    return {"message": "Session revoked"}


@router.get("/me", response_model=UserResponse)
def get_me(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return auth_service.get_me(db, user_id)
