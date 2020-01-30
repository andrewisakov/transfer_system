import jwt
import hashlib
from app.core.init import SELECT_PARTICIPANT


class Participant:

    @classmethod
    async def create(self, account: dict):
        email = account.get('email')
        password = account.get('password')
        currency = account.get('currency')

    @classmethod
    async def get(cls, app, email: str, password: str):
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute(SELECT_PARTICIPANT, (
                    email,
                    hashlib.sha1(password.encode()).hexdigest(),
                ))
                participant = await c.fetchone()
                if participant:
                    return participant[0]
