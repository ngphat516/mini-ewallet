# app/db/sqlserver.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings   # ← lại là settings Singleton quen thuộc

# Engine: quản lý POOL kết nối tới SQL Server.
# Tạo 1 lần duy nhất khi module được import (Singleton kiểu module-level)
engine = create_engine(
    settings.SQLSERVER_URL,    # ← chuỗi @property ghép trong config.py
    pool_size=5,               # giữ sẵn 5 kết nối trong pool
    max_overflow=10,           # cao điểm cho phép mở thêm tối đa 10
    pool_pre_ping=True,        # trước khi dùng, "ping" thử kết nối còn sống không
                               # (tránh lỗi kết nối chết sau khi SQL Server restart)
)

# Session factory: mỗi request sẽ lấy 1 session riêng từ đây
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class cho các model trong models/ kế thừa
Base = declarative_base()

# Dependency cho FastAPI: mở session đầu request, đóng cuối request
def get_db():
    db = SessionLocal()
    try:
        yield db      # trao session cho endpoint dùng
    finally:
        db.close()    # LUÔN đóng, kể cả khi endpoint văng exception