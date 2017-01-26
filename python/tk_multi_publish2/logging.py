# # Copyright (c) 2017 Shotgun Software Inc.
# #
# # CONFIDENTIAL AND PROPRIETARY
# #
# # This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# # Source Code License included in this distribution package. See LICENSE.
# # By accessing, using, copying or modifying this work you indicate your
# # agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# # not expressly granted therein are reserved by Shotgun Software Inc.
#
#
# import sgtk
# import logging
#
# logger = sgtk.platform.get_logger(__name__)
#
# class PublishLogHandler(logging.Handler):
#     """
#     Publish Log handler
#     """
#
#     def __init__(self, list_widget):
#         """
#         :param engine: Engine to which log messages should be forwarded.
#         :type engine: :class:`Engine`
#         """
#         # avoiding super in order to be py25-compatible
#         logging.Handler.__init__(self)
#         self._list_widget = list_widget
#
#     def emit(self, record):
#         """
#         Emit a log message back to the engine logging callback.
#
#         :param record: std log record to handle logging for
#         """
#         # for simplicity, add a 'basename' property to the record to
#         # only contain the leaf part of the logging name
#         # sgtk.env.asset.tk-maya -> tk-maya
#         # sgtk.env.asset.tk-maya.tk-multi-publish -> tk-multi-publish
#         record.basename = record.name.rsplit(".", 1)[-1]
#
#         self._list_widget.addItem(record.msg)
#
#
# def create_logger():
#     # set up a logger
#     full_log_path = "%s.ui" % (logger.name)
#     logger = logging.getLogger(full_log_path)
#
#     self._handler = PublishLogHandler(self.ui.log_list)
#
#     # and handle it in the UI
#     self._logger.addHandler(self._handler)
#
#     if sgtk.LogManager().global_debug:
#         self._handler.setLevel(logging.DEBUG)
#     else:
#         self._handler.setLevel(logging.INFO)
#
#     formatter = logging.Formatter(
#         "[%(levelname)s %(basename)s] %(message)s"
#     )
#     self._handler.setFormatter(formatter)
#
#
#
#
