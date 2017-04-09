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

from .ui.progress_widget import Ui_ProgressWidget

class ProgressWidget(QtGui.QWidget):
    """
    Progress reporting and logging
    """

    RIGHT_OFFSET = 6
    BOTTOM_OFFSET = 6

    def __init__(self, progress_bar, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ProgressWidget, self).__init__(parent)

        self._progress_bar = progress_bar

        # set up the UI
        self.ui = Ui_ProgressWidget()
        self.ui.setupUi(self)

        # hook up a listener to the parent window so this widget
        # follows along when the parent window changes size
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

        self.hide()


    def toggle(self):
        """
        Toggles visibility on and off
        """

        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.__recompute_position()


    @property
    def log_tree(self):
        return self.ui.log_tree


    def __recompute_position(self):

        pos = self._progress_bar.pos()


        self.setGeometry(QtCore.QRect(
            10,
            10,
            self.parentWidget().width() - 20,
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