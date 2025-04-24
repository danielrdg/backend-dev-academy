from motor.motor_asyncio import AsyncIOMotorClient
from roteamento_ia_backend.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
