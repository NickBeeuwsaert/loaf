import asyncio
import operator
from functools import partial
from datetime import datetime, timedelta


from .event_emitter import EventEmitter, emit
from .decorator import reify
from .slack_api import RTMError


class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Message:
    def __init__(self, ts, user, message):
        self.ts = ts
        self.user = user
        self.message = message


class Conversation(EventEmitter):
    def __init__(self, team, id, name):
        self.id = id
        self.name = name

        self.team = team

    def add_message(self, message):
        try:
            user = message['user']
        except KeyError:
            user = User(None, message['username'])
        else:
            user = self.team.users[user]

        message = Message(
            message['ts'],
            user,
            message['text']
        )
        self.messages.append(message)
        self.emit('message', self, message)

    async def load_messages(self):
        oldest = (datetime.now() - timedelta(weeks=1)).timestamp()

        messages = []
        async for message in self.team.web_api.conversations.history(
            self.id,
            oldest=str(oldest)
        ):
            messages.append(message)
        
        for message in reversed(messages):
            self.add_message(message)

    @reify
    def messages(self):
        asyncio.ensure_future(self.load_messages())
        return []

    async def send_message(self, message):
        try:
            response = await self.team.rtm_api.send({
                'type': 'message',
                'channel': self.id,
                'text': message
            })
        except RTMError as e:
            # TODO: Error handling here
            # Show the user a message or something
            pass
        else:
            self.add_message({
                'user': self.team.me.id,
                **response
            })


class Team(EventEmitter):
    _active_conversation = None

    def __init__(self, id, name, me, *, web_api, rtm_api):
        self.id = id
        self.name = name
        self.me = me

        self.web_api = web_api
        self.rtm_api = rtm_api

    @property
    def active_conversation(self):
        return self._active_conversation

    @active_conversation.setter
    def active_conversation(self, conversation):
        self._active_conversation = conversation
        self.emit('switch_conversation', self, conversation)

    def switch_conversation(self, conversation):
        self.active_conversation = conversation

    @emit('conversations_changed')
    def add_conversation(self, conversation):
        @conversation.on('message')
        def handle_message(conversation, message):
            self.emit('message', self, conversation, message)

        self.conversations[conversation.id] = conversation
        if self.active_conversation is None:
            self.active_conversation = conversation

    @emit('users_changed')
    def add_user(self, user):
        self.users[user.id] = user

    def handle_message(self, message):
        channel = message['channel']
        try:
            conversation = self.conversations[channel]
        except KeyError:
            pass
        else:
            conversation.add_message(message)

    async def load_converstions(self):
        async for conversation in self.web_api.conversations.list():
            self.add_conversation(Conversation(
                self, conversation['id'], conversation['name']
            ))

    async def load_users(self):
        async for user in self.web_api.users.list():
            self.add_user(User(user['id'], user['name']))

    def send_message(self, message):
        if self.active_conversation is None:
            return
        return self.active_conversation.send_message(message)

    @reify
    @emit('conversations_changed')
    def conversations(self):
        return {}

    @reify
    @emit('users_changed')
    def users(self):
        return {
            self.me.id: self.me
        }


class TeamOverview(EventEmitter):
    _active_team = None

    @reify
    def teams(self):
        return {}

    @property
    def active_team(self):
        return self._active_team

    @active_team.setter
    def active_team(self, team):
        self._active_team = team
        self.emit('switch_team', team)

    @emit('teams_changed')
    def add_team(self, team):
        team.on('conversations_changed', lambda: self.emit('teams_changed'))
        team.on('message', partial(self.emit, 'message'))

        @team.on('switch_conversation')
        def switch_team(team, _):
            self.active_team = team

        self.teams[team.id] = team
        if self.active_team is None:
            self.active_team = team

    def send_message(self, message):
        if self.active_team is None:
            return

        return self.active_team.send_message(message)

    async def load_team(self, client):
        rtm_client, team_info = await asyncio.gather(
            client.rtm.connect(),
            client.auth.test()
        )
        getter = operator.itemgetter('user_id', 'user', 'team_id', 'team')
        user_id, user, team_id, team = getter(team_info)

        team = Team(
            team_id, team, User(user_id, user),
            web_api=client, rtm_api=rtm_client
        )
        await asyncio.gather(team.load_converstions(), team.load_users())

        rtm_client.on('message', team.handle_message)
        self.add_team(team)

        return team
