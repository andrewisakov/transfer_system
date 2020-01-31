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
        response = web.json_response({'access': False}, status=403)
    return response


@routes.post('/participant')
async def registration(request):
    """ Register new participant """
    session = await get_session(request)
    if session.get('email') == 'admin':
        data = await request.json()
        result = await Participant.create(request.app, data)
        if not result:
            response = web.json_response({'result': 'success'}, status=200)
        else:
            response = web.json_response({'result': result}, status=400)
    else:
        response = web.json_response({'result': 'Недостаточно полномочий!'})
    return response


@routes.post('/transfers')
async def transfer(request):
    """ Get participants transactions """
    session = await get_session(request)
    participant_id = session.get("email")
    if participant_id:
        data = await request.json()
        result = await Participant.get_transactions(request.app, participant_id, data)
        response = web.json_response(result, status=200)
    else:
        response = web.json_response({'result': 'Левая сессия!'}, status=403)
    return response


@routes.post('/transfer')
async def transfer(request):
    """ Make participant transaction """
    session = await get_session(request)
    participant_id = session.get("email")
    if participant_id:
        data = await request.json()
        result = await Participant.make_transaction(request.app, participant_id, data)
        response = web.json_response(result, status=200)
    else:
        response = web.json_response({'result': 'Левая сессия!'}, status=403)
    return response
