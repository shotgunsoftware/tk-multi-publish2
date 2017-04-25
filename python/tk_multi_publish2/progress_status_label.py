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

screen_grab = sgtk.platform.import_framework("tk-framework-qtwidgets", "screen_grab")

logger = sgtk.platform.get_logger(__name__)


class ProgressStatusLabel(QtGui.QLabel):
    """
    Elided Label which underlines on mouseover
    and fires onclick events. Specifically designed
    to be used as part of the logging toolbar.
    """

    # emitted when screen is captured
    # passes the QPixmap as a parameter
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super(ProgressStatusLabel, self).__init__(parent)

        # for the hover behavior
        self.setMouseTracking(True)

        self._bundle = sgtk.platform.current_bundle()
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        super(ProgressStatusLabel, self).mousePressEvent(event)
        self.clicked.emit()

    def enterEvent(self, event):
        """
        When the mouse enters
        """
        font = QtGui.QFont()
        font.setUnderline(True)
        self.setFont(font)

    def leaveEvent(self, event):
        """
        When the mouse leaves
        """
        font = QtGui.QFont()
        font.setUnderline(False)
        self.setFont(font)

    def setText(self, message):
        """
        Sets the text to display in the label. Elides it.
        """
        # set main status message but limit it by the current width of the
        # label and only the first line
        chopped_message = message.split("\n")[0]

        if len(chopped_message) < 100:
            super(ProgressStatusLabel, self).setText(chopped_message)
        else:
            metrics = QtGui.QFontMetrics(self.font())

            elided_message = metrics.elidedText(
                chopped_message,
                QtCore.Qt.ElideRight,
                self.width()
            )
            super(ProgressStatusLabel, self).setText(elided_message)
