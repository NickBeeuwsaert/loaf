import asyncio
from urllib.parse import urljoin

import aiohttp

from ...decorator import reify
from .channels import Channels
from .api import API
from .users import Users
from .rtm import RTM
from .chat import Chat
from .conversations import Conversations
from .team import Team
from .auth import Auth


class SlackError(Exception):
    pass


class WebClient:
    channels = reify(Channels)
    api = reify(API)
    rtm = reify(RTM)
    # apps = reify(Apps)
    auth = reify(Auth)
    # bots = reify(Bots)
    chat = reify(Chat)
    conversations = reify(Conversations)
    # dialog = reify(Dialog)
    # dnd = reify(DND)
    # emoji = reify(Emoji)
    # files = reify(Files)
    # groups = reify(Groups)
    # im = reify(IM)
    # migration = reify(Migration)
    # mpim = reify(MPIM)
    # oauth = reify(OAuth)
    # pins = reify(Pins)
    # reactions = reify(Reactions)
    # reminders = reify(Reminders)
    # search = reify(Search)
    # stars = reify(Stars)
    team = reify(Team)
    # usergroups = reify(Usergroups)
    users = reify(Users)

    def __init__(
        self, token,
        *,
        endpoint="https://slack.com/api/",
        loop=None,
        session_class=aiohttp.ClientSession
    ):
        self._num_calls = 0
        if loop is None:
            loop = asyncio.get_event_loop()

        self.token = token
        self.endpoint = endpoint
        self.session_class = session_class
        self.loop = loop

    @reify
    def session(self):
        return self.session_class(loop=self.loop)

    async def api_call(
        self, http_method, method,
        headers=None,
        data=None,
        params=None,
        **kwargs
    ):
        self._num_calls += 1
        if headers is None:
            headers = {}

        headers.update({'Authorization': f'Bearer {self.token}'})

        # massage params into a format that both
        # aiohttp and the Slack API will like
        # the only value-type accepted is either str or int
        # so we filter out any values set to None (tell the slack API to use
        # default values) and convert any boolean types to integers
        # the slack API will also accept the strings 'true' and 'false'
        # but its easier just to convert to a integer
        if params is not None:
            params = {
                key: value if not isinstance(value, bool) else int(value)
                for key, value in params.items()
                if value is not None
            }

        result = await (await self.session.request(
            http_method, urljoin(self.endpoint, method),
            headers=headers,
            params=params,
            **kwargs
        )).json()

        ok = result.pop('ok')

        if ok is False:
            # TODO: Create a map of errors to raise
            raise SlackError(result)

        return result

    async def paginate_api_call(
        self, http_method, method, *,
        params=None, **kwargs
    ):
        if params is None:
            params = {}
        cursor = params.pop('cursor', None)

        while True:
            response = await self.api_call(
                http_method, method,
                params=dict(cursor=cursor, **params),
                **kwargs
            )

            yield response

            try:
                cursor = response['response_metadata']['next_cursor']
            except KeyError:
                cursor = None

            if not cursor:
                return
