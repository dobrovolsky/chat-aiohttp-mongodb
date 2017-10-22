import hashlib
from motor import motor_asyncio

from config import settings
from main import loop


def get_hash(pswd):
    """Calculate password hash"""
    password = pswd + settings.SECRET_KEY
    for i in range(1000):
        password = hashlib.sha512(password.encode()).hexdigest()
    return password


def get_message_collection():
    """Return connection to user collection"""
    client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT, io_loop=loop)
    db = client[settings.MONGO_DB_NAME]
    collection = db[settings.MONGO_USER_COLLECTION]
    return collection

def get_room_collection():
    """Return connection to user collection"""
    client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT, io_loop=loop)
    db = client[settings.MONGO_DB_NAME]
    collection = db[settings.MONGO_ROOM_COLLECTION]
    return collection

async def is_email_exists_in_db(email) -> bool:
    """Check email in db"""
    collection = get_message_collection()
    data = await collection.find_one({'email': email})
    return bool(data)
