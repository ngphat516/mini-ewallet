
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None

def connect_mongo():
    """Gọi 1 lần khi app khởi động"""
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)

def close_mongo():
    """Gọi khi app tắt"""
    if client:
        client.close()

def get_mongo_db():
    return client[settings.MONGODB_DB]