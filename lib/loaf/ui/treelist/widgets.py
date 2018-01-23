import urwid
from urwid import TreeWidget, AttrWrap


class TreeWidgetMixin:
    @property
    def node(self):
        return self.get_node()

    @property
    def value(self):
        return self.node.get_value()


class ConversationWidget(TreeWidgetMixin, TreeWidget):
    def __init__(self, node):
        super().__init__(node)
        self._w = urwid.AttrWrap(self._w, None, 'selected')

    def selectable(self):
        return True

    def mouse_event(self, size, event, widget, x, y, focus):
        if event == 'mouse press':
            self.node.parent.value.switch_conversation(self.value)

    def get_display_text(self):
        return self.value.name


class TeamWidget(TreeWidgetMixin, TreeWidget):
    def get_display_text(self):
        return self.value.name


class TeamOverviewWidget(TreeWidgetMixin, TreeWidget):
    def get_display_text(self):
        return 'Teams'
