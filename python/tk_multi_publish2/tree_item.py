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
        self._item_widget = Item(tree_widget)
        self._item_widget.set_header(self._task.plugin.name)
        self._item_widget.set_icon(self._task.plugin.icon_pixmap)

        tree_widget = self.treeWidget()
        tree_widget.setItemWidget(self, 0, self._item_widget)

    def __str__(self):
        return self._task.plugin.name

    @property
    def task(self):
        return self._task

    def validate(self):
        self._item_widget.set_status(self._item_widget.PROCESSING)
        try:
            self._task.validate()
        except Exception, e:
            self._item_widget.set_status(self._item_widget.VALIDATION_ERROR)
        else:
            self._item_widget.set_status(self._item_widget.PUBLISH_COMPLETE)


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

        self._item_widget = Item(tree_widget)
        self._item_widget.set_header(self._plugin.name)
        self._item_widget.set_icon(self._plugin.icon_pixmap)

        tree_widget = self.treeWidget()
        tree_widget.setItemWidget(self, 0, self._item_widget)

    def __str__(self):
        return self._plugin.name

    @property
    def plugin(self):
        return self._plugin

    def validate(self):
        pass

class PublishTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    Tree item for a publish item
    """

    def __init__(self, item, parent):
        super(PublishTreeWidgetItem, self).__init__(parent)
        self._item = item

        tree_widget = self.treeWidget()

        self._item_widget = Item(tree_widget)
        self._item_widget.set_header("<b>%s</b><br>%s" % (self._item.name, self._item.display_type))
        self._item_widget.set_icon(self._item.icon_pixmap)

        tree_widget.setItemWidget(self, 0, self._item_widget)


    def __str__(self):
        return "%s %s" % (self._item.display_type, self._item.name)

    @property
    def item(self):
        return self._item

    def validate(self):
        pass
