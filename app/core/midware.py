from aiohttp import web
from aiohttp.web import middleware
from aiohttp_session import get_session


@middleware
async def authorize(request, handler):
    session = await get_session(request)
    if session.get("email") or request.path == '/login':
        return await handler(request)
    else:
        return web.Response(status=403)
