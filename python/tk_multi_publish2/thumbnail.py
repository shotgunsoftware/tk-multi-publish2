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


class Thumbnail(QtGui.QLabel):
    """
    A specialized, custom widget that either displays a
    static square thumbnail or a thumbnail that can be captured
    using screen capture and other methods.
    """

    # emitted when screen is captured
    # passes the QPixmap as a parameter
    screen_grabbed = QtCore.Signal(object)

    # internal signal to initiate screengrab
    _do_screengrab = QtCore.Signal()

    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        QtGui.QLabel.__init__(self, parent)
        self._thumbnail = None
        self._enabled = True
        self._bundle = sgtk.platform.current_bundle()
        self.setAutoFillBackground(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._no_thumb_pixmap = QtGui.QPixmap(":/tk_multi_publish2/camera.png")
        self._do_screengrab.connect(self._on_screengrab)
        self.set_thumbnail(self._no_thumb_pixmap)

    def setEnabled(self, enabled):
        """
        Overrides base class setEnabled

        :param bool enabled: flag to indicate enabled state of the widget
        """
        self._enabled = enabled
        if enabled:
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.unsetCursor()

    def set_thumbnail(self, pixmap):
        """
        Set pixmap to be displayed

        :param pixmap: QPixmap to show or None in order to show default one.
        """
        if pixmap is None:
            self._set_screenshot_pixmap(self._no_thumb_pixmap)
        else:
            self._set_screenshot_pixmap(pixmap)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed.
        In order to emulate the aesthetics of a button,
        a white frame is rendered around the label at mouse press.
        """
        QtGui.QLabel.mousePressEvent(self, event)

        if self._enabled:
            self.setStyleSheet("{border: 1px solid #eee;}")

    def mouseReleaseEvent(self, event):
        """
        Fires when the mouse is released
        Stop drawing the border and emit screen grab signal.
        """
        QtGui.QLabel.mouseReleaseEvent(self, event)

        if self._enabled:
            # disable style
            self.setStyleSheet(None)

            # if the mouse is released over the widget,
            # kick off the screengrab
            pos_mouse = event.pos()
            if self.rect().contains(pos_mouse):
                self._do_screengrab.emit()

    def _on_screengrab(self):
        """
        Perform a screengrab and update the label pixmap.
        """
        self._bundle.log_debug("Prompting for screenshot...")

        self.window().hide()
        try:
            pixmap = screen_grab.ScreenGrabber.screen_capture()
        finally:
            self.window().show()

        if pixmap:
            self._bundle.log_debug(
                "Got screenshot %sx%s" % (pixmap.width(), pixmap.height())
            )
            self._set_screenshot_pixmap(pixmap)
            self.screen_grabbed.emit(pixmap)

    def _set_screenshot_pixmap(self, pixmap):
        """
        Takes the given QPixmap and sets it to be the thumbnail
        image of the note input widget.

        :param pixmap:  A QPixmap object containing the screenshot image.
        """
        self._thumbnail = pixmap

        # format it to fit the label size
        thumb = self._thumbnail.scaled(
            self.width(),
            self.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        self.setPixmap(thumb)
