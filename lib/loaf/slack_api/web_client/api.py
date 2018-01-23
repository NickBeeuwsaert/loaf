class API:
    def __init__(self, client):
        self.client = client

    async def test(self, **kwargs):
        return await self.client.api_call(
            'POST', 'api.test',
            data=kwargs
        )
