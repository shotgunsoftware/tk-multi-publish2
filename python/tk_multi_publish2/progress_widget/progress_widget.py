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
from .progress_details_widget import ProgressDetailsWidget
from .publish_logging import PublishLogWrapper

class ProgressWidget(QtGui.QWidget):
    """
    Progress reporting and logging
    """

    (INFO, ERROR, DEBUG, WARNING) = range(4)

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ProgressWidget, self).__init__(parent)

        self._debug_brush = QtGui.QBrush(QtGui.QColor("#F57209"))  # green
        self._warning_brush = QtGui.QBrush(QtGui.QColor("#F57209"))  # orange
        self._error_brush = QtGui.QBrush(QtGui.QColor("#FF2D5B  "))  # red

        # set up the UI
        self.ui = Ui_ProgressWidget()
        self.ui.setupUi(self)

        # parent our progress widget overlay
        self._progress_details = ProgressDetailsWidget(self, self.parent())

        # set up our log dispatch
        self._log_wrapper = PublishLogWrapper(self)

        self.ui.details_toggle.clicked.connect(self._progress_details.toggle)

        self._logging_parent_item = None  # none means root


    def process_log_message(self, message, status):
        """
        Called from the internal logger

        @param message:
        @param status:
        @return:
        """

        item = QtGui.QTreeWidgetItem(self._logging_parent_item)
        item.setText(0, message)
        if self._logging_parent_item:
            self._logging_parent_item.addChild(item)
        else:
            # root level
            self._progress_details.log_tree.addTopLevelItem(item)

        # assign color
        if status == self.WARNING:
            item.setForeground(0, self._warning_brush)
        elif status == self.ERROR:
            item.setForeground(0, self._error_brush)
        elif status == self.DEBUG:
            item.setForeground(0, self._debug_brush)

        self._progress_details.log_tree.setCurrentItem(item)

        QtCore.QCoreApplication.processEvents()



    @property
    def logger(self):
        return self._log_wrapper.logger

    def push(self, text, icon=None):
        """
        Push a child node to the tree. New log records will
        be added as children to this child node.

        :param text: Caption for the entry
        :param icon: QIcon for the entry
        """
        item = QtGui.QTreeWidgetItem()
        item.setText(0, text)
        if self._logging_parent_item is None:
            self._progress_details.log_tree.invisibleRootItem().addChild(item)
        else:
            self._logging_parent_item.addChild(item)

        if icon:
            item.setIcon(0, icon)

        self._progress_details.log_tree.setCurrentItem(item)
        self._logging_parent_item = item

    def pop(self):
        """
        Pops any active child section.
        If no child sections exist, this operation will not
        have any effect.
        """
        # top level items return None
        if self._logging_parent_item:
            self._logging_parent_item = self._logging_parent_item.parent()
