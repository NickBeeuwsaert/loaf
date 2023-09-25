import urwid
import asyncio
from datetime import datetime

from ..decorator import reify
from .treelist.nodes import TeamOverviewNode


class MessageWidget(urwid.WidgetWrap):
    def __init__(self, ts, user, message):
        super().__init__(urwid.AttrMap(
            urwid.Columns([
                ('weight', 10, urwid.Text(('timestamp', str(datetime.fromtimestamp(float(ts) // 1))))),
                ('weight', 10, urwid.Text(('username', user.name))),
                ('weight', 80, urwid.Text(message))
            ], dividechars=2),
            None, 'selected'
        ))


class MessageEdit(urwid.Edit):
    signals = ['send']

    def keypress(self, size, key):
        key = super().keypress(size, key)
        text = self.edit_text
        if key == 'enter' and text:
            urwid.emit_signal(self, 'send', text)
            self.set_edit_text('')


class LoafWidget(urwid.WidgetWrap):
    def __init__(self, team_overview):
        self.main_loop = None
        self.team_overview = team_overview

        team_overview.on('teams_changed', lambda: urwid.emit_signal(
            self.sidebar.body,
            'modified'
        ))
        team_overview.on('switch_team', lambda team: urwid.emit_signal(
            self.sidebar.body,
            'modified'
        ))

        @team_overview.on('switch_team')
        def switch_team(team):
            self.messages_box.set_title(
                f'#{team.active_conversation.name}'
            )
            self.messages.body[:] = [
                MessageWidget(msg.ts, msg.user, msg.message)
                for msg in team.active_conversation.messages
            ]

        @team_overview.on('message')
        def message(team, conversation, message):
            # Only handle the message if it was in the currently active channel
            if team is not self.team_overview.active_team:
                return

            if conversation is not team.active_conversation:
                return

            self.messages.body.append(
                MessageWidget(message.ts, message.user, message.message)
            )

            # For now just snap the messages to the bottom of the
            # listbox
            self.messages.set_focus(len(self.messages.body) - 1)
            if self.main_loop != None:
                asyncio.get_event_loop().call_soon(self.main_loop.draw_screen)

        super().__init__(self.widget)

    @reify
    def widget(self):
        return urwid.Columns([
            ('weight', 20, urwid.LineBox(self.sidebar)),
            ('weight', 80, urwid.Pile([
                self.messages_box,
                (5, urwid.LineBox(
                    urwid.Filler(self.message),
                    title='Message',
                    title_align='left'
                ))
            ]))
        ])

    @reify
    def messages_box(self):
        return urwid.LineBox(self.messages)

    @reify
    def messages(self):
        return urwid.ListBox(urwid.SimpleFocusListWalker([]))

    def send_message(self, message):
        # Schedule the message in the asyncio event loop
        # TODO: Find a cleaner way to do this
        asyncio.ensure_future(self.team_overview.send_message(message))

    @reify
    def message(self):
        edit = MessageEdit()
        urwid.connect_signal(edit, 'send', self.send_message)
        return edit

    @reify
    def sidebar(self):
        return urwid.TreeListBox(
            urwid.TreeWalker(TeamOverviewNode(self.team_overview))
        )

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key in ('esc', ):
            raise urwid.ExitMainLoop()
        return key
