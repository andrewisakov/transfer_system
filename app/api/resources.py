import asyncio
import aiopg
import base64
import logging
from cryptography import fernet
from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from app.settings import DSN
from app.core.midware import authorize
from app.api.handlers import *
from app.core.models.adapters import xrates

secret = 'secret'


async def refresh_rates():
    while True:
        await xrates.fetch()
        # await xrates.parse()
        await asyncio.sleep(300)


async def create_engines(app):
    app['pg'] = await aiopg.create_pool(**DSN, minsize=10, maxsize=50)


async def dispose_engines(app):
    app['pg'].close()
    await app['pg'].wait_closed()


def main():
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    loop = asyncio.get_event_loop()
    app = web.Application(
        loop=loop,
        middlewares=[
            session_middleware(
                EncryptedCookieStorage(secret_key, max_age=300)),
            authorize,
        ])

    task = loop.create_task(refresh_rates())
    app.router.add_routes(routes)
    app.on_startup.append(create_engines)
    app.on_cleanup.append(dispose_engines)
    web.run_app(app)
