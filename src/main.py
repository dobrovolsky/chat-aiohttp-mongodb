import asyncio

import aiohttp_jinja2
import jinja2
import uvloop
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_pool

from auth.middleware import user_data
from config import setup_routes, settings


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


async def get_app():
    redis_pool = await create_pool((settings.REDIS_HOST, settings.REDIS_PORT), db=settings.REDIS_DB)
    web_app = web.Application(debug=settings.DEBUG, middlewares=[session_middleware(RedisStorage(redis_pool)),
                                                                 user_data])
    web_app['ws_connections'] = {}
    web_app.on_shutdown.append(on_shutdown)
    setup_routes(web_app)
    aiohttp_jinja2.setup(web_app, loader=jinja2.FileSystemLoader(settings.TEMPLATES_DIR))
    return web_app


async def on_shutdown(app):
    for user_id, ws in app['ws_connections'].items():
        ws.close()

if __name__ == '__main__':
    app = loop.run_until_complete(get_app())
    web.run_app(app, host=settings.SITE_HOST, port=settings.SITE_PORT, loop=loop)