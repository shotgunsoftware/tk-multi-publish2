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

screen_grab = sgtk.platform.import_framework("tk-framework-qtwidgets", "screen_grab")

class Thumbnail(QtGui.QLabel):
    """
    A specialized, custom widget that either displays a
    static square thumbnail or a thumbnail that can be captured
    using screen capture and other methods.
    """

    screen_grabbed = QtCore.Signal(object)

    def __init__(self, parent=None):
        """
        Constructor

        :param parent:          The parent QWidget for this control
        """
        QtGui.QLabel.__init__(self, parent)
        self._thumbnail = None
        self._bundle = sgtk.platform.current_bundle()
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._no_thumb_pixmap = QtGui.QPixmap(":/tk_multi_publish2/camera.png")

        self.set_thumbnail(self._no_thumb_pixmap)

    def set_thumbnail(self, pixmap):
        """
        Set up the widget as a thumb
        """
        if pixmap is None:
            self._set_screenshot_pixmap(self._no_thumb_pixmap)
        else:
            self._set_screenshot_pixmap(pixmap)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QLabel.mousePressEvent(self, event)

        # no pixmap exists - screengrab mode
        self._bundle.log_debug("Prompting for screenshot...")

        self.window().hide()
        try:
            pixmap = screen_grab.ScreenGrabber.screen_capture()
        finally:
            self.window().show()

        # It's possible that there's custom screencapture logic
        # happening and we won't get a pixmap back right away.
        # A good example of this is something like RV, which
        # will handle screenshots itself and provide back the
        # image asynchronously.
        if pixmap:
            self._bundle.log_debug(
                "Got screenshot %sx%s" % (pixmap.width(), pixmap.height())
            )
            self.screen_grabbed.emit(pixmap)
            self._set_screenshot_pixmap(pixmap)

    def _set_screenshot_pixmap(self, pixmap):
        """
        Takes the given QPixmap and sets it to be the thumbnail
        image of the note input widget.

        :param pixmap:  A QPixmap object containing the screenshot image.
        """
        self._thumbnail = pixmap
        # format it to 16:9
        thumb = self.__format_thumbnail(pixmap)
        self.setPixmap(thumb)

    def __format_thumbnail(self, pixmap_obj):
        """
        Format a given pixmap to 16:9 ratio

        :param pixmap_obj: input screenshot
        :returns: 160x90 pixmap
        """
        CANVAS_WIDTH = 320
        CANVAS_HEIGHT = 180

        # get the 512 base image
        base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        base_image.fill(QtCore.Qt.transparent)

        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = pixmap_obj.scaled(CANVAS_WIDTH,
                                         CANVAS_HEIGHT,
                                         QtCore.Qt.KeepAspectRatioByExpanding,
                                         QtCore.Qt.SmoothTransformation)

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)

        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)

        pen = QtGui.QPen()
        pen.setWidth(0)
        painter.setPen(pen)

        # note how we have to compensate for the corner radius
        painter.drawRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

        painter.end()

        return base_image
