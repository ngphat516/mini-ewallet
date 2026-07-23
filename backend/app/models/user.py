import uuid
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.db.sqlserver import Base

class User(Base):
    __tablename__ = "Users"              

    # SQL: user_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID()
    user_id = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=uuid.uuid4,                
    )

    # SQL: full_name NVARCHAR(100) NOT NULL
    full_name = Column(String(100), nullable=False)

    # SQL: email VARCHAR(150) NOT NULL UNIQUE
    email = Column(String(150), nullable=False, unique=True, index=True)

    # SQL: phone VARCHAR(15) NOT NULL UNIQUE
    phone = Column(String(15), nullable=False, unique=True)

    # SQL: password_hash VARCHAR(255) NOT NULL  
    password_hash = Column(String(255), nullable=False)

    # SQL: is_active BIT NOT NULL DEFAULT 1 / is_verified BIT NOT NULL DEFAULT 0
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # SQL: created_at/updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
    created_at = Column(DateTime, nullable=False, server_default=text("GETDATE()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("GETDATE()"))