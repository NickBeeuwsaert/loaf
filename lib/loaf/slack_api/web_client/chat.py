class Chat:
    def __init__(self, client):
        self.client = client

    def delete(self, ts):
        pass

    def get_permalink(self, channel, ts):
        return self.client.api_call(
            'GET', 'chat.getPermalink', params=dict(
                channel=channel,
                message_ts=ts
            )
        )

    def me_message(self, channel, text):
        return self.client.api_call(
            'POST', 'chat.meMessage', json=dict(
                channel=channel,
                text=text
            )
        )

    def post_message(self, channel, text):
        return self.client.api_call(
            'POST', 'chat.postMessage', json=dict(
                channel=channel,
                text=text
            )
        )