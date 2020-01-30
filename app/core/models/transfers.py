from types import Dict, Str


class Transfer:
    async def check(cls, payer: Participant, details: Dict):
        details['amount']

    async def create(cls, api, payer: Participant, payee: Participant, details: Dict):
        if await cls.check(payer, details):
            pass
        else:
            pass
