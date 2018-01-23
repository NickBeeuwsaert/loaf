class Users:
    def __init__(self, client):
        self.client = client

    def info(self, user, include_locale=None):
        return self.client.api_call(
            'GET', 'users.info', params=dict(
                user=user,
                include_locale=include_locale
            )
        )

    def identity(self):
        return self.client.api_call('GET', 'users.identity')

    async def list(self, include_locale=None, limit=None, presence=None):
        async for response in self.client.paginate_api_call(
            'GET', 'users.list', params=dict(
                include_locale=include_locale,
                limit=limit,
                presence=presence
            )
        ):
            for member in response['members']:
                yield member
