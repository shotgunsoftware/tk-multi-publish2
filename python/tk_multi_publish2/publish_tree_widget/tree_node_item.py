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
from .custom_widget_item import CustomTreeWidgetItem

logger = sgtk.platform.get_logger(__name__)

from .tree_node_base import TreeNodeBase


class TreeNodeItem(TreeNodeBase):
    """
    Tree item for a publish item
    """

    def __init__(self, item, parent):
        """
        :param item:
        :param parent: The parent QWidget for this control
        """
        self._item = item
        super(TreeNodeItem, self).__init__(parent)
        self.setFlags(
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable
        )

    def _create_widget(self, parent):
        """
        Create the widget that is used to visualise the node
        """
        # create an item widget and associate it with this QTreeWidgetItem
        widget = CustomTreeWidgetItem(self, parent)
        # update with any saved state
        widget.set_header("<b>%s</b><br>%s" % (self._item.name, self._item.display_type))
        widget.set_icon(self._item.icon)
        widget.set_checkbox_value(self.data(0, self.CHECKBOX_ROLE))
        return widget

    def __repr__(self):
        return "<TreeNodeItem %s>" % str(self)

    def __str__(self):
        return "%s %s" % (self._item.display_type, self._item.name)

    @property
    def item(self):
        """
        Associated item instance
        """
        return self._item

    def get_publish_instance(self):
        """
        Returns the low level item or task instance
        that this object represents

        :returns: task or item instance
        """
        return self.item


class TopLevelTreeNodeItem(TreeNodeItem):
    """
    Tree item for a publish item
    """

    def __init__(self, item, parent):
        """
        :param item:
        :param parent: The parent QWidget for this control
        """
        super(TopLevelTreeNodeItem, self).__init__(item, parent)
        # top level items can be dragged
        self.setFlags(
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled
        )

    def synchronize_context(self):
        """
        Updates the context for the underlying item given the
        current position in the tree
        """
        # our parent node is always a context node
        self.item.context = self.parent().context