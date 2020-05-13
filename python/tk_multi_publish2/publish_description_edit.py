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


class PublishDescriptionEdit(QtGui.QTextEdit):
    """
    Widget that holds the summary description
    """

    # Signal emitted when the user starts editing the text box
    started_editing = QtCore.Signal()

    # Signal emitted when the user finishes editing the text box
    finished_editing = QtCore.Signal()

    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        """
        super(PublishDescriptionEdit, self).__init__(parent)

        self._show_placeholder = False

        # this is the placeholder text to be displayed in the bottom right corner of the widget. The spaces afterwards were added so that the
        # placeholder text won't be hidden behind the scroll bar that is automatically added when the text is too long
        self._placeholder_text = "<multiple values>"

    def focusInEvent(self, event):
        """
        Used to detect whether we've started editing the description.
        """
        if event.reason() != QtCore.Qt.FocusReason.ActiveWindowFocusReason:
            self.started_editing.emit()
        return super(PublishDescriptionEdit, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """
        Used to detect whether we've stopped editing the description.
        """
        if event.reason() != QtCore.Qt.FocusReason.ActiveWindowFocusReason:
            self.finished_editing.emit()
        return super(PublishDescriptionEdit, self).focusOutEvent(event)

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
            super(PublishDescriptionEdit, self).paintEvent(paint_event)
