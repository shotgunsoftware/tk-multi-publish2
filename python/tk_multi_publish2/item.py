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

from .ui.item import Ui_Item

logger = sgtk.platform.get_logger(__name__)

class Item(QtGui.QFrame):
    """
    Represents a right hand side details pane in the UI
    """

    (ITEM, PLUGIN) = range(2)
    (NEUTRAL, PROCESSING, VALIDATION_COMPLETE, VALIDATION_ERROR, PUBLISH_ERROR, PUBLISH_COMPLETE) = range(6)

    def __init__(self, parent=None):
        """
        Constructor
        
        :param parent:          The parent QWidget for this control
        """
        QtGui.QFrame.__init__(self, parent)

        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Raised)

        # set up the UI
        self.ui = Ui_Item()
        self.ui.setupUi(self)

        self.ui.left_stack.setCurrentIndex(0)


    def set_mode(self, mode):
        """
        Specifies if this item should be a plugin or a item
        """
        if mode == self.ITEM:
            self.ui.icon.set_thumbnail()

        elif mode == self.PLUGIN:
            self.ui.icon.set_static_thumb(
                QtGui.QPixmap(":/tk_multi_publish2/item.png")
            )

        else:
            raise sgtk.TankError("Unknown item mode!")

    def set_status(self, status):
        """
        Set the status for the plugin
        @param status:
        @return:
        """

    def set_header(self, title):
        """
        Set the title of the item
        """
        self.ui.header.setText(title)


