from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.MONGO_DB_NAME]
    
    @property
    def mentions(self):
        return self.db.mentions

db = Database()