class Channels:
    def __init__(self, client):
        self.client = client

    def archive(self):
        pass

    def create(self):
        pass

    async def history(
        self,
        channel,
        count=None,
        inclusive=None,
        latest=None,
        oldest=None,
        unreads=None
    ):
        """Retrieve messages in a channel"""
        return await self.client.api_call(
            'GET', 'channels.history', params=dict(
                channel=channel,
                count=count,
                inclusive=inclusive,
                latest=latest,
                oldest=oldest,
                unreads=unreads
            )
        )

    async def info(self, channel, include_locale=False):
        response = await self.client.api_call(
            'GET', 'channels.info', params=dict(
                channel=channel,
                include_locale=include_locale
            )
        )

        return response['channel']

    def invite(self):
        pass

    def join(self):
        pass

    def kick(self):
        pass

    def leave(self):
        pass

    async def list(
        self,
        exclude_archived=False,
        exclude_members=True,
        limit=None
    ):
        async for response in self.client.paginate_api_call(
            'GET', 'channels.list', params=dict(
                exclude_archived=exclude_archived,
                exclude_members=exclude_members,
                limit=limit
            )
        ):
            for channel in response['channels']:
                yield channel

    def mark(self):
        pass

    def rename(self):
        pass

    def replies(self):
        pass

    def set_purpose(self):
        pass

    def set_topic(self):
        pass

    def unarchive(self):
        pass
