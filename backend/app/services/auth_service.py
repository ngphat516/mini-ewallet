
from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse, TokenResponse


class AuthService:
    def register(self, db: Session, data: RegisterRequest) -> UserResponse:
        repo = UserRepository(db)                    

        existing = repo.get_by_email(data.email)    
        if existing:
            raise UserAlreadyExistsException()         

        hashed = hash_password(data.password)          
                                                      

        new_user = repo.create(                        
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            password_hash=hashed,
        )

        db.commit()                                    

        return UserResponse.model_validate(new_user)    

    def login(self, db: Session, data: LoginRequest) -> TokenResponse:
        repo = UserRepository(db)

        user = repo.get_by_email(data.email)
        if not user:
            raise InvalidCredentialsException()

        if not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsException()

        access_token = create_access_token(str(user.user_id))
        refresh_token = create_refresh_token(str(user.user_id))

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


auth_service = AuthService()