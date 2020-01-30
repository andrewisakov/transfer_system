import aiohttp
import datetime
import xmltodict
import json
from decimal import Decimal


class BaseAdapter:
    URL = None

    async def fetch(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL.format(self.date)) as resp:
                if resp.status == 200:
                    self.data = await resp.text()
                else:
                    self.data = None


class CBR(BaseAdapter):
    URL = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req={}'

    @property
    def date(self):
        return '/'.join(str(datetime.datetime.today().date()).split('-')[::-1])

    async def parse(self):
        self.data = xmltodict.parse(self.data)
        vc = self.data.get('ValCurs')
        vc = self.data.get('ValCurs', {}).get('Valute', {})
        self.data = {v['CharCode']: Decimal(
            v['Value'].replace(',', '.')) for v in vc}
        self.data = {**{'rates': self.data}, **{'base': 'RUB', 'date': '-'.join(self.date.split('/')[::-1])}}
        return self.data


class ExchangeRates(BaseAdapter):
    URL = 'https://api.exchangeratesapi.io/{}'

    @property
    def date(self):
        return str(datetime.datetime.today().date())

    async def parse(self):
        vc = json.loads(self.data)
        rates = {k: Decimal(str(v)) for k, v in vc.get('rates', {}).items()}
        vc['rates'] = rates
        self.data = vc
        return self.data


xrates = ExchangeRates()
