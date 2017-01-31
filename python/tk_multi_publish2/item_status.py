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

    (_MODE_OFF, _MODE_SPIN, _MODE_DOT) = range(3)

    def __init__(self, parent=None):
        """
        Constructor
        """

        QtGui.QWidget.__init__(self, parent)

        self._bundle = sgtk.platform.current_bundle()

        # setup spinner timer
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._on_animation)
        self._spin_angle = 0

        self._mode = self._MODE_OFF


    ############################################################################################
    # public interface

    def show_spin(self):
        """
        Turn on spinning
        """
        self._mode = self._MODE_SPIN
        self._timer.start(40)

    def show_dot(self, color):

        self._timer.stop()
        self._mode = self._MODE_DOT
        self._color = color

    def show_nothing(self):
        """
        Hide the overlay.
        """
        self._timer.stop()
        self._mode = self._MODE_OFF


    ############################################################################################
    # internal methods

    def _on_animation(self):
        """
        Spinner async callback to help animate the progress spinner.
        """
        self._spin_angle += 2
        if self._spin_angle == 90:
            self._spin_angle = 0
        self.repaint()

    def paintEvent(self, event):
        """
        Render the UI.
        """
        if self._mode == self._MODE_OFF:
            return

        painter = QtGui.QPainter()
        painter.begin(self)
        try:

            # set up semi transparent backdrop
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            if self._mode == self._MODE_SPIN:

                # show the spinner
                painter.translate((painter.device().width() / 2) - 8,
                                  (painter.device().height() / 2) - 8)

                pen = QtGui.QPen(QtGui.QColor(self._bundle.style_constants["SG_HIGHLIGHT_COLOR"]))
                pen.setCapStyle(QtCore.Qt.RoundCap)
                pen.setWidth(2)
                painter.setPen(pen)

                r = QtCore.QRectF(0.0, 0.0, 16.0, 16.0)
                start_angle = (0 + self._spin_angle) * 4 * 16
                span_angle = 300 * 16

                painter.drawArc(r, start_angle, span_angle)

            elif self._mode == self._MODE_DOT:


                painter.translate((painter.device().width() / 2) - 7,
                                  (painter.device().height() / 2) - 7)

                brush = QtGui.QBrush(QtGui.QColor(self._color))
                painter.setBrush(brush)
                pen = QtGui.QPen(QtCore.Qt.NoPen)
                painter.setPen(pen)


                r = QtCore.QRectF(0.0, 0.0, 14.0, 14.0)

                painter.drawEllipse(r)

        finally:
            painter.end()

