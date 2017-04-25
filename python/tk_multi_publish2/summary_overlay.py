# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform.qt import QtCore, QtGui
import sgtk

from .ui.summary_overlay import Ui_SummaryOverlay

logger = sgtk.platform.get_logger(__name__)

class SummaryOverlay(QtGui.QWidget):
    """
    Status summary
    """

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(SummaryOverlay, self).__init__(parent)

        self._bundle = sgtk.platform.current_bundle()

        # set up the UI
        self.ui = Ui_SummaryOverlay()
        self.ui.setupUi(self)

        # hook up a listener to the parent window so this widget
        # follows along when the parent window changes size
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

        self.hide()

    def show_success(self):
        """
        Toggles visibility on and off
        """
        self.ui.icon.setPixmap(
            QtGui.QPixmap(":/tk_multi_publish2/publish_complete.png")
        )
        self.ui.label.setText("Publish\nComplete")
        self.ui.details.setText("For more details, see the log")
        self.show()

    def show_fail(self):
        """
        Toggles visibility on and off
        """
        self.ui.icon.setPixmap(
            QtGui.QPixmap(":/tk_multi_publish2/publish_failed.png")
        )
        self.ui.label.setText("Publish\nFailed!")
        self.ui.details.setText("Please see error log for more details")
        self.show()

    def show_loading(self):
        """

        """
        self.ui.icon.setPixmap(
            QtGui.QPixmap(":/tk_multi_publish2/overlay_loading.png")
        )
        self.ui.label.setText("Loading and processing")
        self.ui.details.setText("Hold tight while we analyze your data")
        self.show()

    def show(self):
        super(SummaryOverlay, self).show()
        self.__recompute_position()

    def __recompute_position(self):
        self.resize(self.parentWidget().size())

    def _on_parent_resized(self):
        """
        Special slot hooked up to the event filter.
        When associated widget is resized this slot is being called.
        """
        self.__recompute_position()


class ResizeEventFilter(QtCore.QObject):
    """
    Utility and helper.

    Event filter which emits a resized signal whenever
    the monitored widget resizes.

    You use it like this:

    # create the filter object. Typically, it's
    # it's easiest to parent it to the object that is
    # being monitored (in this case self.ui.thumbnail)
    filter = ResizeEventFilter(self.ui.thumbnail)

    # now set up a signal/slot connection so that the
    # __on_thumb_resized slot gets called every time
    # the widget is resized
    filter.resized.connect(self.__on_thumb_resized)

    # finally, install the event filter into the QT
    # event system
    self.ui.thumbnail.installEventFilter(filter)
    """
    resized = QtCore.Signal()

    def eventFilter(self, obj, event):
        """
        Event filter implementation.
        For information, see the QT docs:
        http://doc.qt.io/qt-4.8/qobject.html#eventFilter

        This will emit the resized signal (in this class)
        whenever the linked up object is being resized.

        :param obj: The object that is being watched for events
        :param event: Event object that the object has emitted
        :returns: Always returns False to indicate that no events
                  should ever be discarded by the filter.
        """
        # peek at the message
        if event.type() == QtCore.QEvent.Resize:
            # re-broadcast any resize events
            self.resized.emit()
        # pass it on!
        return False

