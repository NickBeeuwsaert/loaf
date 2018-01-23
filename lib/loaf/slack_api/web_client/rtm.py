from ..rtm_client import RTMClient


class RTM:
    def __init__(self, client):
        self.client = client

    def start(
        self,
        batch_presence_aware=None, include_locale=None, mpim_aware=None,
        no_latest=None, no_unreads=None, simple_latest=None
    ):
        return self.client.api_call(
            'GET', 'rtm.start', params=dict(

            )
        )

    async def connect(self, batch_presence_aware=False):
        response = await self.client.api_call(
            'GET', 'rtm.connect', params=dict(
                batch_presence_aware=batch_presence_aware
            )
        )

        ws = await self.client.session.ws_connect(response['url'])
        hello = await ws.receive_json()

        assert hello['type'] == 'hello'
        
        return RTMClient(ws, loop=self.client.loop)
