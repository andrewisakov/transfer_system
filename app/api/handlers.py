import hashlib
from time import time
from aiohttp import web
from aiohttp_session import get_session
from app.core.models.participant import Participant


routes = web.RouteTableDef()


def set_session(session, user_id, request):
    session['email'] = str(user_id)
    session['last_visit'] = time()


@routes.post('/login')
async def login(request):
    login_data = await request.json()
    email = login_data.get('email')
    password = login_data.get('password')
    participant = await Participant.get(request.app, email, password)
    if participant:
        session = await get_session(request)
        set_session(session, str(participant), request)
        response = web.json_response({'access': True}, status=200)
    else:
        response = web.json_response({'access': 'False'}, status=403)
    return response


@routes.post('/participant')
async def registration(request):
    return web.Response()


@routes.get('/participant')
async def transfer(request):
    return web.Response()


@routes.post('/transfer')
async def transfer(request):
    return web.Response()
