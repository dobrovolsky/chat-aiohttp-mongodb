import hashlib

from chat.config import settings


def get_hash(pswd):
    """Calculate password hash"""
    password = pswd + settings.SECRET_KEY
    for i in range(1000):
        password = hashlib.sha512(password.encode()).hexdigest()
    return password

