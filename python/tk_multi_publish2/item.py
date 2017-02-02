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

    (
        NEUTRAL,
        PROCESSING,
        VALIDATION_COMPLETE,
        VALIDATION_ERROR,
        PUBLISH_ERROR,
        PUBLISH_COMPLETE,
        FINALIZE_COMPLETE,
        FINALIZE_ERROR,
        EMPTY
    ) = range(9)

    def __init__(self, parent=None):
        """
        Constructor
        
        :param parent:          The parent QWidget for this control
        """
        QtGui.QFrame.__init__(self, parent)

        # set up the UI
        self.ui = Ui_Item()
        self.ui.setupUi(self)

        self.set_status(self.NEUTRAL)

    def set_icon(self, pixmap):
        """
        Specifies if this item should be a plugin or a item
        """
        self.ui.icon.setPixmap(pixmap)

    @property
    def checkbox(self):
        return self.ui.checkbox

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

        elif status == self.EMPTY:
            pass

        elif status == self.PROCESSING:
            # gray ring
            self.ui.status.show_dot(ring_color="#808080", fill_color=None, dotted=True)

        elif status == self.VALIDATION_COMPLETE:
            # blue ring
            self.ui.status.show_dot(ring_color="#18A7E3", fill_color=None)

        elif status == self.VALIDATION_ERROR:
            # orange ring
            self.ui.status.show_dot(ring_color="#FF8000", fill_color=None)

        elif status == self.PUBLISH_COMPLETE:
            # blue fill gray ring
            self.ui.status.show_dot(ring_color="#FFF", fill_color="#18A7E3")

        elif status == self.PUBLISH_ERROR:
            # big fat red
            self.ui.status.show_dot(ring_color="#FF0000", fill_color="#FF0000")

        elif status == self.FINALIZE_COMPLETE:
            # blue dot
            self.ui.status.show_dot(ring_color="#18A7E3", fill_color="#18A7E3")

        elif status == self.FINALIZE_ERROR:
            # red ring blue middle
            self.ui.status.show_dot(ring_color="#FF0000", fill_color="#18A7E3")

        else:
            raise sgtk.TankError("Invalid item status!")


    def set_header(self, title):
        """
        Set the title of the item
        """
        self.ui.header.setText(title)


