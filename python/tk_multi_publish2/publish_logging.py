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
import logging

from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)


class PublishLogHandler(logging.Handler):
    """
    Publish Log handler
    """

    def __init__(self, tree_widget):
        """
        :param engine: Engine to which log messages should be forwarded.
        :type engine: :class:`Engine`
        """
        # avoiding super in order to be py25-compatible
        logging.Handler.__init__(self)
        self._tree_widget = tree_widget

        self._logging_parent_item = None # none means root

        self._debug_brush = QtGui.QBrush(QtGui.QColor("#508937"))  # green
        self._warning_brush = QtGui.QBrush(QtGui.QColor("#FFD786"))  # orange
        self._error_brush = QtGui.QBrush(QtGui.QColor("#FF383F"))  # red



    def push(self, text, icon):

        item = QtGui.QTreeWidgetItem()
        item.setText(0, text)
        if self._logging_parent_item is None:
            self._tree_widget.invisibleRootItem().addChild(item)
        else:
            self._logging_parent_item.addChild(item)

        if icon:
            item.setIcon(0, icon)

        self._tree_widget.setCurrentItem(item)
        self._logging_parent_item = item

    def pop(self):

        # top level items return None
        if self._logging_parent_item:
            self._logging_parent_item = self._logging_parent_item.parent()


    def emit(self, record):
        """
        Emit a log message back to the engine logging callback.

        :param record: std log record to handle logging for
        """
        # for simplicity, add a 'basename' property to the record to
        # only contain the leaf part of the logging name
        # sgtk.env.asset.tk-maya -> tk-maya
        # sgtk.env.asset.tk-maya.tk-multi-publish -> tk-multi-publish
        record.basename = record.name.rsplit(".", 1)[-1]

        item = QtGui.QTreeWidgetItem(self._logging_parent_item)
        item.setText(0, record.msg)
        if self._logging_parent_item:
            self._logging_parent_item.addChild(item)
        else:
            # root level
            self._tree_widget.addTopLevelItem(item)

        # assign color
        if record.levelno < logging.ERROR and record.levelno > logging.INFO:
            item.setForeground(0, self._warning_brush)
        elif record.levelno > logging.WARNING:
            item.setForeground(0, self._error_brush)
        elif record.levelno < logging.INFO:
            item.setForeground(0, self._debug_brush)

        self._tree_widget.setCurrentItem(item)

        QtCore.QCoreApplication.processEvents()


class PublishLogWrapper(object):

    def __init__(self, tree_widget):

        # set up a logger
        full_log_path = "%s.publish" % logger.name

        self._logger = logging.getLogger(full_log_path)

        self._handler = PublishLogHandler(tree_widget)

        # and handle it in the UI
        self._logger.addHandler(self._handler)

        # don't spam with debug messages
        # user can see those in console or log files.
        self._handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(levelname)s %(basename)s] %(message)s"
        )
        self._handler.setFormatter(formatter)

    @property
    def logger(self):
        return self._logger

    def push(self, text, icon=None):
        self._handler.push(text, icon)

    def pop(self):
        self._handler.pop()




