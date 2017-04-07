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
from .ui.context_widget import Ui_ContextWidget
from .custom_widget_base import CustomTreeWidgetBase


logger = sgtk.platform.get_logger(__name__)


class CustomTreeWidgetContext(CustomTreeWidgetBase):
    """
    Context display widget
    """

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super(CustomTreeWidgetContext, self).__init__(tree_node, parent)

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return None

    def set_icon(self, pixmap):
        """
        Set the icon to be used

        :param pixmap: Square icon pixmap to use
        """
        logger.warning("The context widget does not support thumbnails!")

    def set_status(self, status):
        """
        Set the status for the plugin
        :param status: An integer representing on of the
            status constants defined by the class
        """
        logger.warning("The context widget does not support status!")

    def set_checkbox_value(self, state):
        pass