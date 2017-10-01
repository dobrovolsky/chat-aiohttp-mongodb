from typing import Dict, List

from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection

from ..config import settings


class MongoAdapter:
    """Adapter for MongoDB storage"""

    def __init__(self) -> None:
        self.collection = self.set_up_connection()

    @staticmethod
    def set_up_connection() -> AsyncIOMotorCollection:
        """Return connection to collection"""
        client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT)
        db = client[settings.MONGO_DB_NAME]
        collection = db[settings.MONGO_USER_COLLECTION]
        return collection

    async def add_user(self, user: 'User') -> None:
        """Method for adding user to db"""
        if user.is_valid() and not user._id:
            result = await self.collection.insert_one(user.loads())
            user.id = result.inserted_id

    async def update_user(self, user: 'User') -> None:
        """Update user in db"""
        if user.is_valid():
            data = user.loads()
            user_id = data.pop('_id')
            await self.collection.replace_one({'_id': user_id}, data)

    async def get_user(self, _id: str) -> Dict:
        """Get inforation about user"""
        return await self.collection.find_one({'_id': _id})

    async def get_users(self, filter: Dict) -> List[Dict]:
        cursor = self.collection.find(filter)
        data = []
        async for document in cursor:
            data.append(document)
        return data
