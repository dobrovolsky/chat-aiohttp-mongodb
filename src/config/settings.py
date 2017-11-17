import os
import logging
import pathlib
import warnings

from envparse import env

env_file_path = os.path.join(os.path.dirname(__file__), '.env')
log = logging.getLogger('app')
logging.basicConfig(filename='site.log',level=logging.DEBUG)

if not os.path.isfile(env_file_path):
    warnings.warn('.env file not found. Application using default values.', ResourceWarning)
else:
    env.read_envfile(env_file_path)

DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY', default='')

IS_SECURE = env.bool('IS_SECURE', default=False)
SITE_HOST = env.str('SITE_HOST', default='localhost')
SITE_PORT = env.int('SITE_PORT', default=8888)

USE_MONGO = env.bool('USE_MONGO', default=True)
MONGO_HOST = env.str('MONGO_HOST', default='localhost')
MONGO_PORT = env.int('MONGO_PORT', default=27017)
MONGO_DB_NAME = env.str('MONGO_DB_NAME', default='chat')

MONGO_MESSAGE_COLLECTION = env.str('MONGO_MESSAGE_COLLECTION', default='messages')
MONGO_USER_COLLECTION = env.str('MONGO_USER_COLLECTION', default='users')
MONGO_ROOM_COLLECTION = env.str('MONGO_ROOM_COLLECTION', default='rooms')

_base_dir = pathlib.Path(__file__).parent.parent
BASE_DIR = str(_base_dir)
STATIC_DIR = str(_base_dir.joinpath(env.str('STATIC', default='static')))
MEDIA_DIR = str(_base_dir.joinpath(env.str('MEDIA', default='media')))
TEMPLATES_DIR = str(_base_dir.joinpath(env.str('TEMPLATES', default='templates')))

MEDIA_URL = '/media/'

REDIS_HOST = env.str('REDIS_HOST', default='localhost')
REDIS_PORT = env.int('REDIS_PORT', default=6379)
REDIS_DB = env.int('REDIS_DB', default=0)