from decimal import Decimal
from app.core.init import GET_FUNDS, INSERT_TRANSFER
from app.core.models.adapters import xrates


class Transfer:
    @classmethod
    async def get_funds(cls, app, payer, amount: Decimal) -> Decimal:
        """ Получить остаток """
        debt_credt = Decimal('0.0000')
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute(GET_FUNDS, ({'payer_id': payer[1], 'currency': payer[2]}))
                debt_credt = await c.fetchone()
                debt_credt = debt_credt[0]
                debt_credt = debt_credt if debt_credt else Decimal('0.0000')
        return debt_credt

    @classmethod
    async def create(cls, app, payer: tuple, payee: tuple, amount_payer: Decimal, description=None) -> Decimal:
        errors = []
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                try:
                    await c.execute(INSERT_TRANSFER, {
                         'payer_id': payer[1],
                         'payee_id': payee[1],
                         'amount': amount_payer,
                         'currency': payer[2],
                         'description': description})
                    if payer[2] != payee[2]:
                        # Требуется пересчёт валют
                        amount_payee = await Transfer.recalcuale_amount(amount_payer, payer[2], payee[2])
                        await c.execute(INSERT_TRANSFER, {
                            'payer_id': payer[1],
                            'payee_id': payee[1],
                            'amount': amount_payee,
                            'currency': payee[2],
                            'description': description})
                except Exception as e:
                    errors.append({3001: str(e)})
        return errors

    @staticmethod
    async def recalcuale_amount(amount: Decimal, payer_currency, payee_currency):
        rates = await xrates.parse()
        base = rates.get('base')
        payee_k = 1 if payee_currency == base else rates.get('rates', {}).get(payee_currency)
        payer_k = 1 if payer_currency == base else rates.get('rates', {}).get(payer_currency)
        if payee_k and payer_k:
            amount /= payer_k 
            amount *= payee_k
        return amount.quantize(Decimal('1.0000'))