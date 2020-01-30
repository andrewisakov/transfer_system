import aiohttp
import datetime
import xmltodict
import json


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
        return {**xmltodict.parse(self.data), **{'base': 'RUB'}}


class ExchangeRates(BaseAdapter):
    URL = 'https://api.exchangeratesapi.io/{}'

    @property
    def date(self):
        return str(datetime.datetime.today().date())

    async def parse(self):
        return json.loads(self.data)
