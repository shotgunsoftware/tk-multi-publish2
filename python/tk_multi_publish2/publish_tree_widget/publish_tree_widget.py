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

    def set_plugin_manager(self, plugin_manager):
        self._plugin_manager = plugin_manager

    def _build_item_tree_r(self, item):
        """
        Build the tree of items
        """
        if len(item.tasks) == 0 and len(item.children) == 0:
            # orphan. Don't create it
            return None

        ui_item = TreeNodeItem(item, parent=self)
        ui_item.setExpanded(True)

        for task in item.tasks:
            task = TreeNodeTask(task, parent=self)

        for child in item.children:
            self._build_item_tree_r(child)

        return ui_item

    def build_tree(self):
        """
        Rebuilds the tree
        """
        # first build the items tree
        logger.debug("Building tree.")
        self.clear()
        for item in self._plugin_manager.top_level_items:
            ui_item = self._build_item_tree_r(item)
            if ui_item:
                self.addTopLevelItem(ui_item)


