"""Hook to call whenever a publish tree node is clicked (Qt tree item).

`.tk_multi_publish2` related wordings and phrases used:

- "tree node", or "node" for short:

    - An instance of a subclass of
      `.tk_multi_publish2.publish_tree_widget.tree_node_base.TreeNodeBase`

      - Which itself subclasses `.QTreeWidgetItem`

- "widget" of the node

    - Behaves like a delegate, but not actually using the Qt delegate system
      from model/view architecture

    - An instance of a subclass of
      `.tk_multi_publish2.publish_tree_widget.custom_widget_base.CustomWidgetBase`

      - Which itself subclasses `.QFrame`

- Publish "api" associated with the node, if any:

    - `.tk_multi_publish2.api.item.PublishItem` for a `.TreeNodeItem`
    - `.tk_multi_publish2.api.task.PublishTask` for a `.TreeNodeTask`
    - otherwise `None`, i.e. for `.TreeNodeContext` and `.TreeNodeSummary`

"""

from typing import TypeVar, Union
import sgtk
from sgtk.platform.qt import QtCore, QtGui

HookBaseClass = sgtk.get_hook_baseclass()

TreeNode = TypeVar("TreeNode", bound=QtGui.QTreeWidgetItem)
CustomTreeWidget = TypeVar("CustomTreeWidget", bound=QtGui.QFrame)
API = Union[TypeVar("PublishItem"), TypeVar("PublishTask"), None]


class TreeNodeClicked(HookBaseClass):
    @staticmethod
    def flipped_state(check_state: QtCore.Qt.CheckState) -> QtCore.Qt.CheckState:
        """Flips a unchecked state to checked and any other state to unchecked."""
        return (
            QtCore.Qt.Checked
            if check_state == QtCore.Qt.Unchecked
            else QtCore.Qt.Unchecked
        )

    def single(
        self,
        node: TreeNode,
        widget: CustomTreeWidget,
        api: API,
        buttons: QtCore.Qt.MouseButtons,
        modifiers: QtCore.Qt.KeyboardModifiers,
    ):  # type: (...) -> None
        """Single click callback on a `.TreeNodeBase` (a `.QtGui.QTreeWidgetItem`)."""

    def double(
        self,
        node: TreeNode,
        widget: CustomTreeWidget,
        api: API,
        buttons: QtCore.Qt.MouseButtons,
        modifiers: QtCore.Qt.KeyboardModifiers,
    ):  # type: (...) -> None
        """Double click callback on a `.TreeNodeBase` (a `.QtGui.QTreeWidgetItem`)."""
        if buttons == QtCore.Qt.LeftButton:
            # Ensure expansion states are correctly updated
            node.setExpanded(node.isExpanded())
