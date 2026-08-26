from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, UserInactiveException
from app.db.sqlserver import get_db
from app.repositories.user_repo import UserRepository

bearer_scheme = HTTPBearer()   


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UUID:
    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise UnauthorizedException()

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise UnauthorizedException()
    if not user.is_active:
        raise UserInactiveException()
    return user_id
