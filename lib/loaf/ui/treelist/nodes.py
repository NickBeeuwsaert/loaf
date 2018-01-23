import urwid
from urwid import ParentNode, TreeNode

from .widgets import TeamOverviewWidget, TeamWidget, ConversationWidget


class NodeMixin:
    @property
    def value(self):
        return self.get_value()

    @property
    def parent(self):
        return self.get_parent()

    @property
    def depth(self):
        return self.get_depth()



class ConversationNode(NodeMixin, TreeNode):
    def get_widget(self):
        return ConversationWidget(self)


class TeamNode(NodeMixin, ParentNode):
    def load_widget(self):
        return TeamWidget(self)

    def get_child_keys(self):
        return list(self.value.conversations.keys())

    def load_child_node(self, key):
        return ConversationNode(
            self.value.conversations[key],
            parent=self,
            depth=self.depth+1,
            key=key
        )


class TeamOverviewNode(NodeMixin, ParentNode):
    def load_widget(self):
        return TeamOverviewWidget(self)

    def get_child_keys(self):
        return list(self.value.teams.keys())

    def load_child_node(self, key):
        return TeamNode(
            self.value.teams[key],
            parent=self,
            depth=self.depth+1,
            key=key
        )
