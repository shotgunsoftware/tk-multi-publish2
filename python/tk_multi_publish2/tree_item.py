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


class PublishTreeWidgetConnection(QtGui.QTreeWidgetItem):

    def __init__(self, task, parent):
        """
        """
        QtGui.QTreeWidgetItem.__init__(self, parent)

        tree_widget = self.treeWidget()

        pd = Item(tree_widget)
        pd.set_header(task.plugin.name)
        pd.set_icon(task.plugin.icon_pixmap)
        #pd.set_status(pd.VALIDATION_ERROR)

        tree_widget = self.treeWidget()
        tree_widget.setItemWidget(self, 0, pd)


class PublishTreeWidgetItem(QtGui.QTreeWidgetItem):


    def __init__(self, item, parent):
        """
        Constructor

        :param parent:          The parent QWidget for this control
        """
        QtGui.QTreeWidgetItem.__init__(self, parent)

        tree_widget = self.treeWidget()

        pd = Item(tree_widget)
        pd.set_header(item.name)
        pd.set_icon(item.icon_pixmap)
        #pd.set_status(pd.VALIDATION_ERROR)


        tree_widget.setItemWidget(self, 0, pd)
