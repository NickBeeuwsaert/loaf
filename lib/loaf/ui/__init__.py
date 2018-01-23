import urwid

from ..decorator import reify
from .treelist.nodes import TeamOverviewNode


class MessageWidget(urwid.WidgetWrap):
    def __init__(self, user, message):
        super().__init__(urwid.AttrMap(
            urwid.Columns([
                ('weight', 10, urwid.Text(('bold', user.name))),
                ('weight', 90, urwid.Text(message))
            ], dividechars=2),
            None, 'selected'
        ))


class MessageEdit(urwid.Edit):
    signals = ['send']

    def keypress(self, size, key):
        if key != 'esc':
            return super().keypress(size, key)

        urwid.emit_signal(self, 'send')


class LoafWidget(urwid.WidgetWrap):
    def __init__(self, team_overview):
        self.team_overview = team_overview
        self.team_overview.on('teams_changed', self._team_added)
        self.team_overview.on('switch_team', self._on_switch_team)
        self.team_overview.on('message', self._on_message)
        super().__init__(self.widget)

    def _on_message(self, team, conversation, message):
        # Only handle the message if it was in the currently active channel
        if team is not self.team_overview.active_team:
            return

        if conversation is not team.active_conversation:
            return

        self.messages.body.append(
            MessageWidget(message.user, message.message)
        )

    def _team_added(self):
        self.sidebar.body._modified()

    def _on_switch_team(self, team):
        self.messages.body[:] = [
            MessageWidget(msg.user, msg.message)
            for msg in team.active_conversation.messages
        ]

    @reify
    def widget(self):
        return urwid.Columns([
            ('weight', 20, urwid.LineBox(self.sidebar)),
            ('weight', 80, urwid.Pile([
                urwid.LineBox(self.messages),
                (5, urwid.LineBox(urwid.Filler(self.message)))
            ]))
        ])

    @reify
    def messages(self):
        return urwid.ListBox(urwid.SimpleFocusListWalker([]))

    @reify
    def message(self):
        edit = MessageEdit(multiline=True)
        return edit

    @reify
    def sidebar(self):
        return urwid.TreeListBox(
            urwid.TreeWalker(TeamOverviewNode(self.team_overview))
        )
    
    def keypress(self, size, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        super().keypress(size, key)
