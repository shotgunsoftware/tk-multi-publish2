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

from .ui.progress_details_widget import Ui_ProgressDetailsWidget

logger = sgtk.platform.get_logger(__name__)

class ProgressDetailsWidget(QtGui.QWidget):
    """
    Progress reporting and logging
    """

    def __init__(self, progress_widget, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ProgressDetailsWidget, self).__init__(parent)

        # set up the UI
        self.ui = Ui_ProgressDetailsWidget()
        self.ui.setupUi(self)

        self._progress_widget = progress_widget

        # hook up a listener to the parent window so this widget
        # follows along when the parent window changes size
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

        self.ui.close.clicked.connect(self.toggle)

        # make sure the first column takes up as much space as poss.
        self.ui.log_tree.header().setResizeMode(0, QtGui.QHeaderView.Stretch)

        self.hide()


    def toggle(self):
        """
        Toggles visibility on and off
        """

        if self.isVisible():
            self.hide()
        else:
            self.show()

    def show(self):
        super(ProgressDetailsWidget, self).show()
        self.__recompute_position()
        self.ui.log_tree.expandAll()

    @property
    def log_tree(self):
        return self.ui.log_tree


    def __recompute_position(self):

        pos = self._progress_widget.pos()

        self.setGeometry(QtCore.QRect(
            pos.x(),
            0,
            self._progress_widget.width(),
            pos.y()
        ))


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
