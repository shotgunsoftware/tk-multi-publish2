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

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import sgtk
from sgtk.platform.qt import QtCore, QtGui

HookBaseClass = sgtk.get_hook_baseclass()

TreeNode = TypeVar("TreeNode", bound=QtGui.QTreeWidgetItem)
CustomTreeWidget = TypeVar("CustomTreeWidget", bound=QtGui.QFrame)
PublishItem = TypeVar("PublishItem", bound="tk_multi_publish2.api.PublishItem")
PublishTask = TypeVar("PublishTask", bound="tk_multi_publish2.api.PublishTask")
if TYPE_CHECKING and (publish2_app := sgtk.platform.current_bundle()):
    tk_multi_publish2 = publish2_app.import_module("tk_multi_publish2")


class TreeNodeClicked(HookBaseClass):
    """Hook called when a publish tree node is clicked (QTreeWidgetItem)."""

    def single(
        self,
        node: TreeNode,
        widget: CustomTreeWidget,
        api: PublishItem | PublishTask | None,
        buttons: QtCore.Qt.MouseButtons,
        modifiers: QtCore.Qt.KeyboardModifiers,
    ) -> None:
        """Single click callback on a `.TreeNodeBase` (a `.QtGui.QTreeWidgetItem`).

        By default, nothing additional is implemented and it's just Qt's built-in
        behavior.
        """

    def double(
        self,
        node: TreeNode,
        widget: CustomTreeWidget,
        api: PublishItem | PublishTask | None,
        buttons: QtCore.Qt.MouseButtons,
        modifiers: QtCore.Qt.KeyboardModifiers,
    ) -> None:
        """Double click callback on a `.TreeNodeBase` (a `.QTreeWidgetItem`).

        Default implementation ensures expansion state is correctly set whenever
        left/main mouse button is clicked (behavior from v2.10.8)
        """
        if buttons == QtCore.Qt.LeftButton:
            # Ensure expansion states are correctly updated
            node.setExpanded(node.isExpanded())
