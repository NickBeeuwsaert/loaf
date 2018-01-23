class Team:
    def __init__(self, client):
        self.client = client

    async def info(self):
        result = await self.client.api_call('GET', 'team.info')
        return result['team']
