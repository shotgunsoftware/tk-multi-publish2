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

from .progress_details_widget import ProgressDetailsWidget
from .publish_logging import PublishLogWrapper

logger = sgtk.platform.get_logger(__name__)

class ProgressHandler(object):
    """
    Progress reporting and logging
    """

    (INFO, ERROR, DEBUG, WARNING) = range(4)

    (PHASE_LOAD, PHASE_VALIDATE, PHASE_PUBLISH, PHASE_FINALIZE) = range(4)

    _PUBLISH_INSTANCE_ROLE = QtCore.Qt.UserRole + 1001

    def __init__(self, icon_label, status_label, progress_bar):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ProgressHandler, self).__init__()

        self._icon_label = icon_label
        self._status_label = status_label
        self._progress_bar = progress_bar

        self._icon_lookup = {
            self.PHASE_LOAD: QtGui.QPixmap(":/tk_multi_publish2/status_load.png"),
            self.PHASE_VALIDATE: QtGui.QPixmap(":/tk_multi_publish2/status_validate.png"),
            self.PHASE_PUBLISH: QtGui.QPixmap(":/tk_multi_publish2/status_publish.png"),
            self.PHASE_FINALIZE: QtGui.QPixmap(":/tk_multi_publish2/status_success.png"),
        }

        self._icon_error_lookup = {
            self.PHASE_LOAD: QtGui.QPixmap(":/tk_multi_publish2/status_warning.png"),
            self.PHASE_VALIDATE: QtGui.QPixmap(":/tk_multi_publish2/status_warning.png"),
            self.PHASE_PUBLISH: QtGui.QPixmap(":/tk_multi_publish2/status_error.png"),
            self.PHASE_FINALIZE: QtGui.QPixmap(":/tk_multi_publish2/status_error.png"),
        }


        self._debug_brush = QtGui.QBrush(QtGui.QColor("#05AB6C"))  # green
        self._warning_brush = QtGui.QBrush(QtGui.QColor("#F57209"))  # orange
        self._error_brush = QtGui.QBrush(QtGui.QColor("#FF2D5B"))  # red


        # parent our progress widget overlay
        self._progress_details = ProgressDetailsWidget(self._progress_bar, self._progress_bar.parent())

        # clicking on the log toggles the logging window
        self._status_label.clicked.connect(self._progress_details.toggle)

        # set up our log dispatch
        self._log_wrapper = PublishLogWrapper(self)

        self._logging_parent_item = None  # none means root

        self._current_phase = None

    def select_last_message(self, publish_instance):
        """
        reveals the last log entry associated with the given publish instance.
        """
        # find the last message matching the task or item
        def _check_r(parent):
            for child_index in range(parent.childCount())[::-1]:
                child = parent.child(child_index)

                # depth first, backwards
                match = _check_r(child)
                if match:
                    return match

                if child.data(0, self._PUBLISH_INSTANCE_ROLE) == publish_instance:
                    return child

            return None

        tree_node = _check_r(self._progress_details.log_tree.invisibleRootItem())

        if tree_node:
            # make sure the log ui is visible
            self._progress_details.show()
            # focus on node in tree
            self._progress_details.log_tree.scrollToItem(
                tree_node,
                QtGui.QAbstractItemView.PositionAtCenter
            )
            # make it current
            self._progress_details.log_tree.setCurrentItem(tree_node)


    def process_log_message(self, message, status):
        """
        Called from the internal logger

        @param message:
        @param status:
        @return:
        """

        self._status_label.setText(message)

        # set phase icon in logger
        if self._current_phase is None:
            icon = None
        elif status != self.ERROR:
            icon = self._icon_lookup[self._current_phase]
        else:
            icon = self._icon_error_lookup[self._current_phase]

        self._icon_label.setPixmap(icon)

        item = QtGui.QTreeWidgetItem(self._logging_parent_item)

        if status == self.DEBUG:
            message = "Debug: %s" % message
        elif status == self.WARNING:
            message = "Warning: %s" % message

        item.setText(0, message)
        item.setToolTip(0, message)
        item.setIcon(0, icon)

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

    def set_phase(self, phase):
        """
        set the phase that we are currently in
        """
        self._current_phase = phase

    def reset_progress(self, max_items):
        logger.debug("Resetting progress bar. Number of items: %s" % max_items)
        self._progress_bar.setMaximum(max_items)
        self._progress_bar.reset()
        self._progress_bar.setValue(0)

    def increment_progress(self):
        progress = self._progress_bar.value() + 1
        logger.debug("Setting progress to %s" % progress)
        self._progress_bar.setValue(progress)

    def push(self, text, icon=None, publish_instance=None):
        """
        Push a child node to the tree. New log records will
        be added as children to this child node.

        :param text: Caption for the entry
        :param icon: QIcon for the entry
        :param publish_instance: item or task associated with this level.
        """
        logger.debug("Pushing subsection to log tree: %s" % text)

        self._status_label.setText(text)

        item = QtGui.QTreeWidgetItem()
        item.setText(0, text)
        item.setData(0, self._PUBLISH_INSTANCE_ROLE, publish_instance)

        if self._logging_parent_item is None:
            self._progress_details.log_tree.invisibleRootItem().addChild(item)
        else:
            self._logging_parent_item.addChild(item)

        if icon:
            item.setIcon(0, icon)
            self._icon_label.setPixmap(icon)
        elif self._current_phase:
            std_icon = self._icon_lookup[self._current_phase]
            item.setIcon(0, std_icon)
            self._icon_label.setPixmap(std_icon)

        self._progress_details.log_tree.setCurrentItem(item)
        self._logging_parent_item = item

    def pop(self):
        """
        Pops any active child section.
        If no child sections exist, this operation will not
        have any effect.
        """
        logger.debug("Popping log tree hierarchy.")
        # top level items return None
        if self._logging_parent_item:
            self._logging_parent_item = self._logging_parent_item.parent()
