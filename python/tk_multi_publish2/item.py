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

    (NEUTRAL, PROCESSING, VALIDATION_COMPLETE, VALIDATION_ERROR, PUBLISH_ERROR, PUBLISH_COMPLETE) = range(6)

    def __init__(self, parent=None):
        """
        Constructor
        
        :param parent:          The parent QWidget for this control
        """
        QtGui.QFrame.__init__(self, parent)

        #self.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.setFrameShadow(QtGui.QFrame.Raised)

        # set up the UI
        self.ui = Ui_Item()
        self.ui.setupUi(self)

        self.set_status(self.NEUTRAL)

    def set_icon(self, pixmap):
        """
        Specifies if this item should be a plugin or a item
        """
        self.ui.icon.setPixmap(pixmap)

    def set_status(self, status):
        """
        Set the status for the plugin
        @param status:
        @return:
        """
        # reset
        self.ui.status.show_nothing()
        self.ui.stack.setCurrentIndex(0)

        if status == self.NEUTRAL:
            self.ui.stack.setCurrentIndex(1)

        elif status == self.PROCESSING:
            self.ui.status.show_spin()

        elif status == self.PUBLISH_COMPLETE:
            self.ui.status.show_dot("#18A7E3")

        elif status == self.PUBLISH_ERROR:
            self.ui.status.show_dot("red")

        elif status == self.VALIDATION_COMPLETE:
            self.ui.status.show_dot("green")

        elif status == self.VALIDATION_ERROR:
            self.ui.status.show_dot("orange")

        else:
            raise sgtk.TankError("Invalid item status!")


    def set_header(self, title):
        """
        Set the title of the item
        """
        self.ui.header.setText(title)


