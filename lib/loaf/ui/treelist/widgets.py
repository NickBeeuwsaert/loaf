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
    def selectable(self):
        return True

    def mouse_event(self, size, event, widget, x, y, focus):
        if event == 'mouse press':
            self.node.parent.value.active_conversation = self.value

    def get_display_text(self):
        parent_value = self.node.parent.value
        value = self.node.value

        text = f'#{value.name}'
        if parent_value.active_conversation is value:
            return ('selected', text)
        else:
            return text


class TeamWidget(TreeWidgetMixin, TreeWidget):
    def get_display_text(self):
        value = self.value
        return value.alias or value.name


class TeamOverviewWidget(TreeWidgetMixin, TreeWidget):
    def get_display_text(self):
        return 'Teams'
