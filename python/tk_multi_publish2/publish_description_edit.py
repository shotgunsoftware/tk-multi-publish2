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


class PublishDescriptionEditBase(QtGui.QTextEdit):
    """
    Widget that holds the summary description
    """

    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        """
        super(PublishDescriptionEditBase, self).__init__(parent)

        self._show_multiple_values = False

        # this is the placeholder text to be displayed in the bottom right corner of the widget. The spaces afterwards were added so that the
        # placeholder text won't be hidden behind the scroll bar that is automatically added when the text is too long
        self._multiple_values_text = "<multiple values>"

        # Get the color we will use to draw the placeholder with.
        self._highlight = sgtk.platform.current_bundle().style_constants[
            "SG_HIGHLIGHT_COLOR"
        ]

    def paintEvent(self, paint_event):
        """
        Paints the line plain text editor and adds a placeholder on bottom right corner when multiple values are detected.
        """

        # If the box does not have focus, draw <multiple values> placeholder when self._show_placeholder is true, even if the widget has text
        if not self.hasFocus() and self._show_multiple_values is True:
            p = QtGui.QPainter(self.viewport())

            # right placeholder note in blue
            col = QtGui.QColor(self._highlight)  # blue
            p.setPen(QtGui.QPen(col))
            p.setBrush(QtGui.QBrush(col))

            p.drawText(
                self.rect(),
                QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft,
                self._multiple_values_text,
            )

        else:
            super(PublishDescriptionEditBase, self).paintEvent(paint_event)


class PublishDescriptionEditQt4(PublishDescriptionEditBase):
    """
    Widget that holds the summary description.
    Since Qt 4's QTextEdit doesn't have a built in placeholder, this class implements one.
    Taken from here: https://stackoverflow.com/a/54553625/4223964
    """

    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        """
        super(PublishDescriptionEditQt4, self).__init__(parent)
        self._placeholderText = ""
        self._placeholderVisible = False
        self.textChanged.connect(self.placeholderVisible)

    def placeholderVisible(self):
        """
        Return if the placeholder text is visible, and force update if required.
        """
        placeholderCurrentlyVisible = self._placeholderVisible
        self._placeholderVisible = self._placeholderText and self.document().isEmpty()
        if self._placeholderVisible != placeholderCurrentlyVisible:
            self.viewport().update()
        return self._placeholderVisible

    def placeholderText(self):
        """
        Return text used as a placeholder.
        """
        return self._placeholderText

    def setPlaceholderText(self, text):
        """
        Set text to use as a placeholder.
        """
        self._placeholderText = text
        if self.document().isEmpty():
            self.viewport().update()

    def paintEvent(self, paint_event):
        """
        Paints the line plain text editor and adds a placeholder on bottom right corner when multiple values are detected.
        """
        super(PublishDescriptionEditQt4, self).paintEvent(paint_event)

        if self.placeholderVisible():
            painter = QtGui.QPainter(self.viewport())
            colour = self.palette().text().color()
            colour.setAlpha(128)
            painter.setPen(colour)
            painter.setClipRect(self.rect())
            margin = self.document().documentMargin()
            textRect = self.viewport().rect().adjusted(margin, margin, 0, 0)
            painter.drawText(
                textRect,
                QtCore.Qt.AlignTop | QtCore.Qt.TextWordWrap,
                self.placeholderText(),
            )


# Qt 5 implements a QTextEdit with a placeholder feature built in.
# However for Qt 4 we've had to implement one.
if QtCore.qVersion()[0] == "4":
    base = PublishDescriptionEditQt4
else:
    base = PublishDescriptionEditBase


class PublishDescriptionEdit(base):
    pass
