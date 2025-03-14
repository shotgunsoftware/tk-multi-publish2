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
    Elided Label which fires onclick events. Specifically designed
    to be used as part of the logging toolbar.
    """

    # emitted when screen is captured
    # passes the QPixmap as a parameter
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super().__init__(parent)

        # for the hover behavior
        self.setMouseTracking(True)

        self._full_text = ""

        self._bundle = sgtk.platform.current_bundle()
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        super().mousePressEvent(event)
        self.clicked.emit()

    def resizeEvent(self, event):
        """
        When item is resized
        """
        self.__update_text_elide()
        super().resizeEvent(event)

    def __update_text_elide(self):
        """
        Update the text in the widget based on its width
        """
        # set main status message but limit it by the current width of the
        # label and only the first line
        chopped_message = self._full_text.split("\n")[0]

        metrics = QtGui.QFontMetrics(self.font())

        # Max text length is widget length minus an
        # offset, so we make sure we can fit the
        # elided text (with the added "...") in
        # the widget without it expanding.
        text_width = self.width() - 10

        elided_message = metrics.elidedText(
            chopped_message, QtCore.Qt.ElideRight, text_width
        )
        self.setText(elided_message, compute_elide=False)

    def setText(self, message, compute_elide=True):
        """
        Sets the text to display in the label.
        """
        if compute_elide:
            # kick the UI recomputation
            self._full_text = message
            self.__update_text_elide()
        else:
            # called from __update_text_elide()
            super().setText(message)
