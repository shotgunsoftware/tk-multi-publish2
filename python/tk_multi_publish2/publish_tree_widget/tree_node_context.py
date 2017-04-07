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
from .custom_widget_context import CustomTreeWidgetContext

logger = sgtk.platform.get_logger(__name__)

from .tree_node_base import TreeNodeBase

class TreeNodeContext(TreeNodeBase):
    """
    Highest level object in the tree, representing a context
    """

    def __init__(self, context, parent):
        """
        :param item:
        :param parent: The parent QWidget for this control
        """
        self._context = context
        super(TreeNodeContext, self).__init__(parent)

        # this object can have other items dropped on it
        # but cannot be dragged
        self.setFlags(
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsDropEnabled
        )

    def __repr__(self):
        return "<TreeNodeContext %s>" % str(self)

    def __str__(self):
        return str(self._context)

    def _create_widget(self):
        """
        Create the widget that is used to visualise the node
        """
        # create an item widget and associate it with this QTreeWidgetItem
        tree_widget = self.treeWidget()
        widget = CustomTreeWidgetContext(self, tree_widget)
        tree_widget.setItemWidget(self, 0, widget)
        # update with any saved state
        widget.set_header(str(self._context))
        return widget

    def validate(self):
        """
        Perform validation
        """
        return True

    def publish(self):
        """
        Perform publish
        """
        return True

    def finalize(self):
        """
        Perform finalize
        """
        return True


