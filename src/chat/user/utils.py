import hashlib
from motor import motor_asyncio

from chat.config import settings
from chat.main import loop


def get_hash(pswd):
    """Calculate password hash"""
    password = pswd + settings.SECRET_KEY
    for i in range(1000):
        password = hashlib.sha512(password.encode()).hexdigest()
    return password


def message_collection():
    """Return connection to user collection"""
    client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT, io_loop=loop)
    db = client[settings.MONGO_DB_NAME]
    collection = db[settings.MONGO_USER_COLLECTION]
    return collection

