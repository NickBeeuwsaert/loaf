class Conversations:
    def __init__(self, client):
        self.client = client

    async def list(self, exclude_archived=None, limit=None, types='public_channel,private_channel,mpim,im'):
        if isinstance(types, (list, tuple)):
            types = ', '.join(types)

        async for response in self.client.paginate_api_call(
            'GET', 'conversations.list', params=dict(
                exclude_archived=exclude_archived,
                limit=limit,
                types=types
            )
        ):
            for channel in response['channels']:
                yield channel

    async def history(
        self, channel,
        inclusive=None, latest=None, limit=None, oldest=None
    ):
        async for response in self.client.paginate_api_call(
            'GET', 'conversations.history', params=dict(
                channel=channel,
                inclusive=inclusive,
                latest=latest,
                limit=limit,
                oldest=oldest
            )
        ):
            for message in response['messages']:
                yield message

    async def replies(
        self, channel, ts,
        inclusive=None, latest=None, limit=None, oldest=None
    ):
        async for response in self.client.paginate_api_call(
            'GET', 'conversations.replies', params=dict(
                channel=channel,
                ts=ts,
                inclusive=inclusive,
                latest=latest,
                limit=limit,
                oldest=oldest
            )
        ):
            for message in response['messages']:
                yield message

    async def info(self, channel, include_locale=None):
        response = await self.client.api_call(
            'GET', 'conversations.info', params=dict(
                channel=channel,
                include_locale=include_locale
            )
        )

        return response['channel']

    def members(self):
        pass

    def archive(self): pass

    def close(self): pass

    def create(self): pass

    def invite(self): pass

    def join(self): pass

    def kick(self): pass

    def leave(self): pass

    def open(self): pass

    def rename(self): pass

    def set_purpose(self): pass

    def set_topic(self): pass

    def unarchive(self): pass
