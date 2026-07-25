from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException

bearer_scheme = HTTPBearer()   


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UUID:
    
    token = credentials.credentials   
                                    
    payload = decode_token(token, expected_type="access")
    return UUID(payload["sub"])