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

logger = sgtk.platform.get_logger(__name__)


class PublishLogHandler(logging.Handler):
    """
    Publish Log handler that links up a handler to a
    qt tree for display.
    """

    def __init__(self, progress_widget):
        """
        :param tree_widget: QTreeWidget to use for logging
        """
        # avoiding super in order to be py25-compatible
        logging.Handler.__init__(self)
        self._progress_widget = progress_widget

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

        if record.levelno < logging.ERROR and record.levelno > logging.INFO:
            status = self._progress_widget.WARNING
        elif record.levelno > logging.WARNING:
            status = self._progress_widget.ERROR
        elif record.levelno < logging.INFO:
            status = self._progress_widget.DEBUG
        else:
            status = self._progress_widget.INFO

        # request that the log manager processes the message
        self._progress_widget.process_log_message(record.msg, status)


class PublishLogWrapper(object):
    """
    Convenience object that wraps around a logger and a handler
    that can be used for publishing.
    """

    def __init__(self, progress_widget):
        """
        :param tree_widget: QTreeWidget to use for logging
        """

        self._bundle = sgtk.platform.current_bundle()

        # set up a logger
        full_log_path = "%s.plugins" % self._bundle.logger.name

        self._logger = logging.getLogger(full_log_path)

        self._handler = PublishLogHandler(progress_widget)

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
        """
        The associated logger
        """
        return self._logger





