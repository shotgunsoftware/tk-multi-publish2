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
    An overlay which sits on top of the details and treeview
    in the main UI. Used to present progress and status,
    e.g. "loading items" or "publish failed!"
    """

    # signal emitted when the info label is clicked by the user
    info_clicked = QtCore.Signal()

    # signal emitted when the publish again is clicked by the user
    publish_again_clicked = QtCore.Signal()

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super().__init__(parent)

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

        self.ui.info.clicked.connect(self.info_clicked.emit)
        self.ui.publish_again.clicked.connect(self.publish_again_clicked.emit)

    def show_no_items_error(self):
        """
        Shows a special message when there is no items collected under an alternate
        UI operation determined by the 'enable_manual_load' application option.
        """
        self.ui.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/publish_failed.png"))
        # Hardcoding line break so the message displays on 2 lines.
        # Usage of label's own word wrap displays the message below on 3 lines.
        # NOTE: Can't manually break line when using <p></p>
        self.ui.label.setText("Could not find any\nitems to publish.")
        self.ui.info.setText("For more details, <b><u>click here</u></b>.")
        self.ui.publish_again.hide()
        self.show()

    def show_success(self):
        """
        Shows standard "publish completed successfully!" prompt
        """
        self.ui.icon.setPixmap(
            QtGui.QPixmap(":/tk_multi_publish2/publish_complete.png")
        )
        self.ui.label.setText("Publish\nComplete")
        self.ui.info.setText("For more details, <b><u>click here</u></b>.")

        self.ui.publish_again.setText("To publish again, <b><u>click here</u></b>.")
        self.ui.publish_again.show()

        self.show()

    def show_fail(self):
        """
        Shows standard "publish failed!" prompt
        """
        self.ui.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/publish_failed.png"))
        self.ui.label.setText("Publish\nFailed!")
        self.ui.info.setText("For more details, <b><u>click here</u></b>.")

        self.ui.publish_again.hide()
        self.ui.publish_again.setText("")

        self.show()

    def show_loading(self):
        """
        Shows standard "loading stuff" prompt
        """
        self.ui.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/overlay_loading.png"))
        self.ui.label.setText("Loading and processing")
        self.ui.info.setText("Hold tight while we analyze your data")

        self.ui.publish_again.hide()
        self.ui.publish_again.setText("")

        self.show()

    def show(self):
        """
        Subclassed show method
        """
        super().show()
        self._on_parent_resized()

    def _on_parent_resized(self):
        """
        Special slot hooked up to the event filter.
        When associated widget is resized this slot is being called.
        """
        self.resize(self.parentWidget().size())


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
