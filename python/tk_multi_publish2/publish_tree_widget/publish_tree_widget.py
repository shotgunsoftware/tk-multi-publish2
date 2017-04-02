# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import sgtk
import collections
from sgtk.platform.qt import QtCore, QtGui
from .tree_node import TreeNodeContext, TreeNodeTask, TreeNodeItem

logger = sgtk.platform.get_logger(__name__)


class PublishTreeWidget(QtGui.QTreeWidget):
    """
    Main widget
    """

    def __init__(self, parent):
        """
        :param parent: The parent QWidget for this control
        """
        super(PublishTreeWidget, self).__init__(parent)
        self._plugin_manager = None

        self._dragged_items = None

    def set_plugin_manager(self, plugin_manager):
        self._plugin_manager = plugin_manager

    def _build_item_tree_r(self, item, tree_parent):
        """
        Build the tree of items
        """
        if len(item.tasks) == 0 and len(item.children) == 0:
            # orphan. Don't create it
            return None

        ui_item = TreeNodeItem(item, tree_parent)
        ui_item.setExpanded(True)

        for task in item.tasks:
            task = TreeNodeTask(task, ui_item)

        for child in item.children:
            self._build_item_tree_r(child, ui_item)

        return ui_item

    def build_tree(self):
        """
        Rebuilds the tree
        """

        # group items by context
        items_by_context = collections.defaultdict(list)
        for item in self._plugin_manager.top_level_items:
            items_by_context[item.context].append(item)

        logger.debug("Building tree.")
        self.clear()

        for (context, items) in items_by_context.iteritems():
            context_item = TreeNodeContext(context, self)
            context_item.setExpanded(True)
            self.addTopLevelItem(context_item)
            for item in items:
                self._build_item_tree_r(item, tree_parent=context_item)

    def dropEvent(self, event):

        for item in self._dragged_items:
            print(item)
            item.create_widget()

        super(PublishTreeWidget, self).dropEvent(event)


    def mouseReleaseEvent(self, event):
        super(PublishTreeWidget, self).mouseReleaseEvent(event)
        self._dragged_items = self.selectedItems()


    def dragEnterEvent(self, event):



        self._dragged_items = self.selectedItems()
        super(PublishTreeWidget, self).dragEnterEvent(event)
