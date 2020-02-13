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

        # look for actions attached to the record
        if hasattr(record, "action_button"):
            # generic button
            action = record.action_button
            action["type"] = "button"
        elif hasattr(record, "action_show_folder"):
            # show folder in file browser
            action = record.action_show_folder
            action["type"] = "show_folder"
        elif hasattr(record, "action_show_in_shotgun"):
            # show entity in shotgun
            action = record.action_show_in_shotgun
            action["type"] = "show_in_shotgun"
        elif hasattr(record, "action_show_more_info"):
            # show additional supplied data in a popup
            action = record.action_show_more_info
            action["type"] = "show_more_info"
        elif hasattr(record, "action_open_url"):
            # open a url in a browser
            action = record.action_open_url
            action["type"] = "open_url"
        else:
            action = None

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
        self._progress_widget.process_log_message(record.getMessage(), status, action)


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
        full_log_path = "%s.hook" % self._bundle.logger.name

        self._logger = logging.getLogger(full_log_path)

        # seal the logger - this will prevent any log messages
        # emitted by the publish hooks to propagate up
        # in the hierarchy and be picked up by engine loggers.
        # The reason we are doing this is because it may seem odd
        # to get plugin info in for example the maya console.
        # more importantly, it will appear in the shotgun engine
        # in a dialog window after app exit which is non-ideal.
        self._logger.propagate = False

        self._handler = PublishLogHandler(progress_widget)

        # and handle it in the UI
        self._logger.addHandler(self._handler)
        logger.debug("Installed log handler for publishing @ %s" % full_log_path)

        # log level follows the global settings
        if sgtk.LogManager().global_debug:
            self._handler.setLevel(logging.DEBUG)
        else:
            self._handler.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(levelname)s %(basename)s] %(message)s")
        self._handler.setFormatter(formatter)

    def shut_down(self):
        """
        Deallocate logging
        """
        self._logger.removeHandler(self._handler)

    @property
    def logger(self):
        """
        The associated logger
        """
        return self._logger
