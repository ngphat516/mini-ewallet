# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from app.core.exceptions import AppException, app_exception_handler
from app.db.mongodb import connect_mongo, close_mongo, get_mongo_db
from app.db.sqlserver import engine  
from app.db.redis import get_redis 
from app.api.v1.auth import router as auth_router
# ── Khối 2: định nghĩa lifespan (phải có TRƯỚC khi tạo app,
#    vì dòng tạo app cần trao nó vào) ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 [LIFESPAN] Đang kết nối MongoDB...")
    connect_mongo()
    print("✅ [LIFESPAN] Xong. App sẵn sàng nhận request.")
    yield
    print("🛑 [LIFESPAN] App tắt, đóng MongoDB...")
    close_mongo()


# ── Khối 3: KHAI SINH — một lần duy nhất, lifespan trao ngay tại đây ──
app = FastAPI(title="Mini E-Wallet", lifespan=lifespan)

# ── Khối 4: nối dây vào app duy nhất đó ──
app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth_router)
@app.get("/health")
async def health_check():
    status = {}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["sqlserver"] = "ok"
    except Exception as e:
        status["sqlserver"] = f"lỗi: {type(e).__name__}"
    try:
        await get_mongo_db().command("ping")
        status["mongodb"] = "ok"
    except Exception as e:
        status["mongodb"] = f"lỗi: {type(e).__name__}"
    try:
        await get_redis().ping()
        status["redis"] = "ok"
    except Exception as e:
        status["redis"] = f"lỗi: {type(e).__name__}"
    return status