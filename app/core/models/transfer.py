from decimal import Decimal
from app.core.init import GET_FUNDS


class Transfer:
    @classmethod
    async def get_funds(cls, app, payer_id, amount: Decimal) -> Decimal:
        """ Получить остаток """
        debt_credt = Decimal('0.0000')
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute(GET_FUNDS, ({'payer_id': payer_id}))
                debt_credt = await c.fetchall()
                if debt_credt:
                    debt_credt = debt_credt[0] - debt_credt[1]
        return debt_credt

    @classmethod
    async def create(cls, app, payer_id: int, payee: tuple, amount: Decimal) -> Decimal:
        pass
        # if await cls.check(payer, details):
        #     pass
        # else:
        #     pass
