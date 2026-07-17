# test_connections.py
# Đặt file này ở backend/ (ngang hàng thư mục app/), chạy: python test_connections.py
# Mục đích: kiểm tra 3 đường kết nối SQL Server, MongoDB, Redis đều thông.

import asyncio


def test_sqlserver():
    from sqlalchemy import text
    from app.db.sqlserver import engine
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DB_NAME()")).scalar()
        print(f"✅ SQL Server OK — đang ở DB: {result}")


async def test_mongo():
    from app.db.mongodb import connect_mongo, get_mongo_db, close_mongo
    connect_mongo()
    info = await get_mongo_db().command("ping")
    print(f"✅ MongoDB OK — ping: {info}")
    close_mongo()


async def test_redis():
    from app.db.redis import get_redis
    r = get_redis()
    await r.set("test_key", "hello", ex=10)
    val = await r.get("test_key")
    print(f"✅ Redis OK — đọc lại: {val}")


if __name__ == "__main__":
    failed = False

    try:
        test_sqlserver()
    except Exception as e:
        failed = True
        print(f"❌ SQL Server LỖI: {type(e).__name__}: {e}")

    try:
        asyncio.run(test_mongo())
    except Exception as e:
        failed = True
        print(f"❌ MongoDB LỖI: {type(e).__name__}: {e}")

    try:
        asyncio.run(test_redis())
    except Exception as e:
        failed = True
        print(f"❌ Redis LỖI: {type(e).__name__}: {e}")

    print("-" * 40)
    print("→ CHƯA đạt, sửa mục ❌ ở trên" if failed else "→ Cả 3 đường đều thông, đủ chuẩn merge ✅")