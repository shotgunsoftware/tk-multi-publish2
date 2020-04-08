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

logger = sgtk.platform.get_logger(__name__)


class PublishDescriptionEdit(QtGui.QPlainTextEdit):
    """
    Widget that holds the summary description
    """

    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        """
        QtGui.QPlainTextEdit.__init__(self, parent)

        self._show_placeholder = False

        # this is the placeholder text to be displayed in the bottom right corner of the widget. The spaces afterwards were added so that the
        # placeholder text won't be hidden behind the scroll bar that is automatically added when the text is too long
        self._placeholder_text = "<multiple values>"

    def paintEvent(self, paint_event):
        """
        Paints the line plain text editor and adds a placeholder on bottom right corner when multiple values are detected.
        """

        # If the box does not have focus, draw <multiple values> placeholder when self._show_placeholder is true, even if the widget has text
        if not self.hasFocus() and self._show_placeholder == True:
            p = QtGui.QPainter(self.viewport())

            # right placeholder note in blue
            col = QtGui.QColor(24, 167, 227)  # blue
            p.setPen(QtGui.QPen(col))
            p.setBrush(QtGui.QBrush(col))

            p.drawText(
                self.rect(),
                QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft,
                self._placeholder_text,
            )

        else:
            QtGui.QPlainTextEdit.paintEvent(self, paint_event)
