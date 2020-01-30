import jwt
import hashlib
from app.core.init import SELECT_PARTICIPANT, INSERT_PARTICIPANT


class Participant:

    @classmethod
    async def create(cls, app, account):
        errors = []
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                try:
                    await c.execute(
                        INSERT_PARTICIPANT,
                        (
                            account.get('email'),
                            hashlib.sha1(
                                account.get('password').encode()).hexdigest(),
                            account.get('currency')
                        ))
                except Exception as e:
                    errors.append(e.pgerror)
        return errors

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
