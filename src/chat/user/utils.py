import hashlib
from marshmallow.exceptions import ValidationError
from motor import motor_asyncio

from chat.config import settings
from chat.main import loop


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


def basic_string_validation(value, min_length=None, max_length=None, blank=False):
    """Provide basic validation for string"""
    if not isinstance(value, str):
        raise ValidationError('should be a string')
    if min_length and len(value) < min_length:
        raise ValidationError(f'string should be longer than {min_length}')
    if max_length and len(value) > max_length:
        raise ValidationError(f'string should be shorter than {max_length}')
    if not blank and not value:
        raise ValidationError(f'string should not be blank')


async def is_email_exists_in_db(email) -> bool:
    """Check email in db"""
    collection = get_message_collection()
    data = await collection.find_one({'email': email})
    return bool(data)
