import re
from decimal import Decimal
import datetime
import hashlib
from app.core.utils import check_datetime_format
from app.core.init import SELECT_PARTICIPANT, INSERT_PARTICIPANT, SELECT_TANSACTIONS
from .transfer import Transfer


class Participant:

    @classmethod
    async def get_by_id(cls, app, participant_id):
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute('select email, id, currency from participants where id=%(id)s', {'id': participant_id})
                return await c.fetchone()

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
    async def get(cls, app, email: str, password: str=None):
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                if password:
                    await c.execute(SELECT_PARTICIPANT, (
                        email,
                        hashlib.sha1(password.encode()).hexdigest(),
                    ))
                    participant = await c.fetchone()
                else:
                    await c.execute(
                        'select email, id, currency from participants where email=%s;',
                        (email, )
                    )
                    return await c.fetchone()
                if participant:
                    return participant[0]

    @classmethod
    async def make_transaction(cls, app, participant_id, data):
        errors = []
        payee = await cls.get(app, data.get('payee'))
        if not payee:
            errors.append({1001: 'Получатель не найден!'})

        amount = data.get('amount')
        if not amount:
            return {'errors': {'1010': 'Не указано поле amount!'}}

        amount = str(amount)
        m = re.match(r'\d+(\.\d{0-4})?', amount)
        if not m:
            return {'errors': {1002: 'Сумма платежа должна быть десятичным числом 0000000[.00[00]]!'}}

        amount = Decimal(amount[m.span()[0]:m.span()[1]])
        participant_id = int(participant_id)
        payer = await cls.get_by_id(app, participant_id)
        funds = await Transfer.get_funds(app, payer, amount)

        if (funds < amount) and (participant_id != payee[1]):
            errors.append({1003: 'Не достаточно средств!'})
        else:
            transfer_errors = await Transfer.create(app, payer, payee, amount, data.get('description'))
            if transfer_errors:
                errors += transfer_errors
            
        return {'result': 'success'} if not errors else {'errors': errors}

    @classmethod
    async def get_transactions(cls, app, participant_id, data):
        #TODO: По уму нужна пагинация, но пока без неё...
        errors = []

        date1 = data.get('date_from')
        if not date1:
            now = datetime.datetime.now()
            date1 = datetime.datetime(now.year, now.month, 1)
        else:
            m = check_datetime_format(date1)
            if not m:
                date1 = datetime.datetime.now().date()
                errors.append({2001: f'Дата начала - не дата/время! Но продолжаем с {date1}'})

        date2 = data.get('date_to')
        if not date2:
            date2 = datetime.datetime.now()
        else:
            m = check_datetime_format(date2)
            if not m:        
                date2 = datetime.datetime.now()
                errors.append({2002: f'Дата конца - не дата/время! Но продолжаем с {date2}'})

        participant_id = int(participant_id)
        participant = await cls.get_by_id(app, participant_id)
        result = []
        async with app['pg'].acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute(SELECT_TANSACTIONS,
                                {'date1': date1,
                                 'date2': date2,
                                 'currency': participant[2],
                                 'payer_id': participant[1]},
                                )

                result = [
                    {'date': r[0],
                     'currency': r[1],
                     'debt': str(r[2]),
                     'credt': r[3],
                     'email': r[4],
                     'description': r[5]} for r in await c.fetchall()]

        return {'results': result} if not errors else {'results': results, 'errors': errors}
