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
from .custom_widget_summary import CustomTreeWidgetSummary

logger = sgtk.platform.get_logger(__name__)

from .tree_node_base import TreeNodeBase


class TreeNodeSummary(TreeNodeBase):
    """
    Tree item for a publish item
    """

    def __init__(self, parent):
        """
        :param item:
        :param parent: The parent QWidget for this control
        """
        super().__init__(parent)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable)

    def _create_widget(self, parent):
        """
        Create the widget that is used to visualise the node
        """
        # create an item widget and associate it with this QTreeWidgetItem
        widget = CustomTreeWidgetSummary(self, parent)
        return widget

    def __repr__(self):
        return "<TreeNodeSummary>"

    def __str__(self):
        return "Item Summary"

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
