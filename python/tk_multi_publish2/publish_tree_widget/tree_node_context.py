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
from sgtk.platform.qt import QtCore
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
        super().__init__(parent)

        # this object can have other items dropped on it
        # but cannot be dragged
        self.setFlags(self.flags() | QtCore.Qt.ItemIsDropEnabled)

    def __repr__(self):
        return "<TreeNodeContext %s>" % str(self)

    def __str__(self):
        return str(self._context)

    def _create_widget(self, parent):
        """
        Create the widget that is used to visualise the node
        """
        # create an item widget and associate it with this QTreeWidgetItem
        widget = CustomTreeWidgetContext(self, parent)
        # update with any saved state
        widget.set_header(str(self._context))
        return widget

    def create_summary(self):
        """
        Creates summary of actions

        :returns: List of strings
        """
        if self.checked:
            return ["<div style='color:#0AA3F8'><b>%s</b></div>" % self._context]
        else:
            return []

    @property
    def context(self):
        """
        The associated context
        """
        return self._context

    def validate(self, standalone):
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
