import asyncio
from .event_emitter import EventEmitter, fires
from .decorator import reify


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
        user = message['user']
        message = Message(
            message['ts'],
            self.team.users[user],
            message['text']
        )
        self.messages.append(message)
        self.fire('message', self, message)

    @reify
    def messages(self):
        return []

    async def send_message(self, message):
        response = await self.team.rtm_api.send({
            'type': 'message',
            'channel': self.id,
            'text': message
        })
        self.add_message({
            'user': self.team.me.id,
            **response
        })


class Team(EventEmitter):
    active_conversation = None

    def __init__(self, id, name, me, *, web_api, rtm_api):
        self.id = id
        self.name = name
        self.me = me

        self.web_api = web_api
        self.rtm_api = rtm_api

    def switch_conversation(self, conversation):
        self.active_conversation = conversation
        self.fire('switch_conversation', self, conversation)

    def on_message(self, conversation, message):
        self.fire('message', self, conversation, message)

    @fires('conversations_changed')
    def add_conversation(self, conversation):
        conversation.on('message', self.on_message)
        self.conversations[conversation.id] = conversation
        if self.active_conversation is None:
            self.active_conversation = conversation

    @fires('users_changed')
    def add_user(self, user):
        self.users[user.id] = user

    def on_receive_message(self, message):
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
    @fires('conversations_changed')
    def conversations(self):
        return {}

    @reify
    @fires('users_changed')
    def users(self):
        return {
            self.me.id: self.me
        }


class TeamOverview(EventEmitter):
    active_team = None

    @reify
    def teams(self):
        return {}

    def _on_switch_team(self, team, convo):
        self.active_team = team
        self.fire('switch_team', team)

    def _on_message(self, team, conversation, message):
        self.fire('message', team, conversation, message)

    def _on_conversations_changed(self):
        self.fire('teams_changed')

    @fires('teams_changed')
    def add_team(self, team):
        team.on('conversations_changed', self._on_conversations_changed)
        team.on('switch_conversation', self._on_switch_team)
        team.on('message', self._on_message)
        self.teams[team.id] = team
        if self.active_team is None:
            self.active_team = team

    def send_message(self, message):
        if self.active_team is None:
            return

        return self.active_team.send_message(message)

    async def load_team(self, client):
        rtm_client, team_info, my_info = await asyncio.gather(
            client.rtm.connect(),
            client.team.info(),
            client.auth.test()
        )
        me = User(my_info['user_id'], my_info['user'])
        team = Team(
            team_info['id'],
            team_info['name'],
            me=me,
            web_api=client,
            rtm_api=rtm_client
        )
        await asyncio.gather(team.load_converstions(), team.load_users())
        rtm_client.on('message', team.on_receive_message)
        self.add_team(team)

        return team
