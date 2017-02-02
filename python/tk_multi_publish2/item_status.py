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

class ItemStatus(QtGui.QWidget):
    """
    Publish Status Widget
    """

    (_MODE_OFF, _MODE_ON) = range(2)

    def __init__(self, parent=None):
        """
        Constructor
        """
        QtGui.QWidget.__init__(self, parent)
        self._bundle = sgtk.platform.current_bundle()
        self._mode = self._MODE_OFF
        self._dotted = False
        self._pen_color = None
        self._brush_color = None



    ############################################################################################
    # public interface

    def show_dot(self, ring_color, fill_color, dotted=False):

        self._mode = self._MODE_ON
        self._pen_color = ring_color
        self._brush_color = fill_color
        self._dotted = dotted
        self.repaint()

    def show_nothing(self):
        """
        Hide the overlay.
        """
        self._mode = self._MODE_OFF
        self.repaint()


    ############################################################################################
    # internal methods

    def paintEvent(self, event):
        """
        Render the UI.
        """
        if self._mode == self._MODE_OFF:
            # fast exit
            return

        painter = QtGui.QPainter()
        painter.begin(self)
        try:

            # set up semi transparent backdrop
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            painter.translate((painter.device().width() / 2) - 7,
                              (painter.device().height() / 2) - 7)

            if self._pen_color:

                pen = QtGui.QPen(QtGui.QColor(self._pen_color))

                if self._dotted:
                    pen.setWidth(1)
                    pen.setStyle(QtCore.Qt.DotLine)
                else:
                    pen.setWidth(2)

                painter.setPen(pen)

            if self._brush_color:

                brush = QtGui.QBrush(QtGui.QColor(self._brush_color))
                painter.setBrush(brush)
                pen = QtGui.QPen(QtCore.Qt.NoPen)
                painter.setPen(pen)

            r = QtCore.QRectF(0.0, 0.0, 14.0, 14.0)
            painter.drawEllipse(r)


        finally:
            painter.end()

