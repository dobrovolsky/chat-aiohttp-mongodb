import asyncio

import jinja2
import aiohttp_jinja2

import uvloop
from aiohttp import web
from aioredis import create_pool
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage

from chat.config import setup_routes, settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logger = settings.log
loop = asyncio.get_event_loop()

async def get_app():
    app = web.Application(debug=settings.DEBUG)
    setup_routes(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATES_DIR))
    redis_pool = await create_pool((settings.REDIS_HOST, settings.REDIS_PORT), db=settings.REDIS_DB)
    setup(app, RedisStorage(redis_pool))
    return app

if __name__ == '__main__':
    app = loop.run_until_complete(get_app())
    web.run_app(app, host=settings.SITE_HOST, port=settings.SITE_PORT, loop=loop)

