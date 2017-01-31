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

from .item import Item

logger = sgtk.platform.get_logger(__name__)

class PublishTreeWidget(QtGui.QTreeWidgetItem):
    """
    Base class for all tree widgets
    """
    def __init__(self, parent):
        super(PublishTreeWidget, self).__init__(parent)


class PublishTreeWidgetTask(QtGui.QTreeWidgetItem):
    """
    Tree item for a task
    """

    def __init__(self, task, parent):
        """
        """
        super(PublishTreeWidgetTask, self).__init__(parent)
        self._task = task

        tree_widget = self.treeWidget()
        pd = Item(tree_widget)
        pd.set_header(self._task.plugin.name)
        pd.set_icon(self._task.plugin.icon_pixmap)
        #pd.set_status(pd.VALIDATION_ERROR)

        tree_widget = self.treeWidget()
        tree_widget.setItemWidget(self, 0, pd)

    @property
    def task(self):
        return self._task


class PublishTreeWidgetPlugin(QtGui.QTreeWidgetItem):
    """
    Tree item for a plugin
    """


    def __init__(self, plugin, parent):
        """
        """
        super(PublishTreeWidgetPlugin, self).__init__(parent)
        self._plugin = plugin

        tree_widget = self.treeWidget()

        pd = Item(tree_widget)
        pd.set_header(self._plugin.name)
        pd.set_icon(self._plugin.icon_pixmap)
        #pd.set_status(pd.VALIDATION_ERROR)

        tree_widget = self.treeWidget()
        tree_widget.setItemWidget(self, 0, pd)

    @property
    def plugin(self):
        return self._plugin



class PublishTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    Tree item for a publish item
    """

    def __init__(self, item, parent):
        super(PublishTreeWidgetItem, self).__init__(parent)
        self._item = item

        tree_widget = self.treeWidget()

        pd = Item(tree_widget)
        pd.set_header(self._item.name)
        pd.set_icon(self._item.icon_pixmap)
        #pd.set_status(pd.VALIDATION_ERROR)


        tree_widget.setItemWidget(self, 0, pd)

    @property
    def item(self):
        return self._item

