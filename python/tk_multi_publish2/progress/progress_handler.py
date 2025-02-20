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
from .publish_actions import (
    show_folder,
    show_in_shotgun,
    show_more_info,
    open_url,
)

logger = sgtk.platform.get_logger(__name__)


class ProgressHandler(object):
    """
    Progress reporting and logging
    """

    (INFO, ERROR, DEBUG, WARNING) = range(4)

    (PHASE_LOAD, PHASE_VALIDATE, PHASE_PUBLISH, PHASE_FINALIZE) = range(4)

    _PUBLISH_INSTANCE_ROLE = QtCore.Qt.UserRole + 1001
    _NUM_ERRORS_ROLE = QtCore.Qt.UserRole + 1002

    def __init__(self, icon_label, status_label, progress_bar):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super().__init__()

        self._icon_label = icon_label
        self._status_label = status_label
        self._progress_bar = progress_bar

        self._icon_lookup = {
            self.PHASE_LOAD: QtGui.QPixmap(":/tk_multi_publish2/status_load.png"),
            self.PHASE_VALIDATE: QtGui.QPixmap(
                ":/tk_multi_publish2/status_validate.png"
            ),
            self.PHASE_PUBLISH: QtGui.QPixmap(":/tk_multi_publish2/status_publish.png"),
            self.PHASE_FINALIZE: QtGui.QPixmap(
                ":/tk_multi_publish2/status_success.png"
            ),
        }

        self._icon_warning = QtGui.QPixmap(":/tk_multi_publish2/status_warning.png")
        self._icon_error = QtGui.QPixmap(":/tk_multi_publish2/status_error.png")

        # These colors come from the HIG.
        self._debug_brush = QtGui.QBrush(QtGui.QColor("#88BC47"))  # green
        self._warning_brush = QtGui.QBrush(QtGui.QColor("#F9A332"))  # orange
        self._error_brush = QtGui.QBrush(QtGui.QColor("#EC494A"))  # red

        # parent our progress widget overlay
        self._progress_details = ProgressDetailsWidget(self._progress_bar.parent())
        self._progress_details.copy_to_clipboard_clicked.connect(
            self._copy_log_to_clipboard
        )

        # clicking on the log toggles the logging window
        self._status_label.clicked.connect(self._progress_details.toggle)

        # store all log messages in a list
        self._log_messages = []
        self._current_indent = 0

        # set up our log dispatch
        self._log_wrapper = PublishLogWrapper(self)

        self._logging_parent_item = None  # none means root

        self._current_phase = None

    def shut_down(self):
        """
        Deallocate all loggers
        """
        logger.debug("Shutting down publish logging...")
        self._log_wrapper.shut_down()

    def is_showing_details(self):
        """
        Returns true if the log details are shown, false if not
        """
        return self._progress_details.isVisible()

    def hide_details(self):
        """
        Hides details window if it's shown
        """
        self._progress_details.hide()

    def show_details(self):
        """
        Shows details window if it's hidden
        """
        self._progress_details.show()

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
                tree_node, QtGui.QAbstractItemView.PositionAtCenter
            )
            # make it current
            self._progress_details.log_tree.setCurrentItem(tree_node)

    def _copy_log_to_clipboard(self):
        """
        Copy the log to the clipboard
        """
        logger.debug(
            "Copying %d log messages to clipboard..." % len(self._log_messages)
        )
        QtGui.QApplication.clipboard().setText("\n".join(self._log_messages))

    def process_log_message(self, message, status, action):
        """
        Handles log messages
        """
        if status != self.DEBUG:
            self._status_label.setText(message)

        # set phase icon in logger
        if self._current_phase is None:
            icon = None
        elif status == self.ERROR:
            icon = self._icon_error
        elif status == self.WARNING:
            icon = self._icon_warning
        else:
            icon = self._icon_lookup[self._current_phase]

        self._icon_label.setPixmap(icon)

        item = QtGui.QTreeWidgetItem(self._logging_parent_item)

        # count the errors on the parent item
        if self._logging_parent_item and status == self.ERROR:

            self._logging_parent_item.setData(
                0,
                self._NUM_ERRORS_ROLE,
                self._logging_parent_item.data(0, self._NUM_ERRORS_ROLE) + 1,
            )

        # better formatting in case of errors and warnings
        if status == self.DEBUG:
            message = "DEBUG: %s" % message
        elif status == self.WARNING:
            message = "WARNING: %s" % message
        elif status == self.ERROR:
            message = "ERROR: %s" % message

        item.setText(0, message)

        if icon:
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

        # if status == self.DEBUG:
        #     item.setForeground(0, self._debug_brush)

        if action:
            # add any action button to the log item
            self._process_action(item, action)

        self._progress_details.log_tree.setCurrentItem(item)
        self._log_messages.append("%s%s" % (" " * (self._current_indent * 2), message))

        QtCore.QCoreApplication.processEvents()

    @property
    def logger(self):
        """
        The logger root for all publish related info
        """
        return self._log_wrapper.logger

    @property
    def progress_details(self):
        """
        The progress details widget.
        """
        return self._progress_details

    def set_phase(self, phase):
        """
        Sets the phase that we are currently in
        """
        self._current_phase = phase

    def reset_progress(self, max_items=1):
        """
        Resets the progress bar
        """
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
        item.setData(0, self._NUM_ERRORS_ROLE, 0)

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
        self._log_messages.append("%s%s" % (" " * (self._current_indent * 2), text))
        self._current_indent += 1

    def pop(self):
        """
        Pops any active child section.
        If no child sections exist, this operation will not
        have any effect.

        :returns: number of errors emitted in the subtree
        """
        logger.debug("Popping log tree hierarchy.")
        self._current_indent -= 1

        # top level items return None
        if self._logging_parent_item:
            num_errors = self._logging_parent_item.data(0, self._NUM_ERRORS_ROLE)
            self._logging_parent_item = self._logging_parent_item.parent()

            if self._logging_parent_item:
                # now calculate the number of errors for this node by aggregating the
                # error counts for all children
                parent_errors = 0
                for child_index in range(self._logging_parent_item.childCount()):
                    child_item = self._logging_parent_item.child(child_index)
                    parent_errors += child_item.data(0, self._NUM_ERRORS_ROLE)

                self._logging_parent_item.setData(
                    0, self._NUM_ERRORS_ROLE, parent_errors
                )

        else:
            num_errors = 0

        return num_errors

    def _process_action(self, item, action):
        """
        Process an action attached to a record, represented by the supplied item

        :param item: The item created for the record
        :param action: The action dictionary attached to the record
        """

        logger.debug("Rendering log action %s" % action)
        if action["type"] == "button":
            # A generic button with a supplied callback:
            # {
            #     "label": "Hello, world!",
            #     "tooltip": "This button says hello to the world."
            #     "callback": self._hello_world,
            #     "args": {"foo": 123, "bar": 456}
            # }

            if "args" not in action:
                # allows plugins to not have to define args if the callback
                # does not require them.
                action["args"] = dict()

        elif action["type"] == "show_folder":
            # A common action for showing the folder for a supplied path in
            # the system's file browser. The label and tooltip are optional.
            # {
            #     "label": "Show Publish Folder",
            #     "tooltip": "Show the publish path in a file browser.",
            #     "path": path
            # }

            action["callback"] = show_folder
            action["args"] = dict(path=action.get("path"))

            # add a label if not supplied
            if "label" not in action:
                action["label"] = "Show Folder"

            # add a tooltip if not supplied
            if "tooltip" not in action:
                action["tooltip"] = "Reveal in the system's file browser"

        elif action["type"] == "show_in_shotgun":
            # A common action for showing an entity's detail page in Shotgun
            # The label and tooltip are optional.
            # {
            #     "label": "Show Version in Shotgun",
            #     "tooltip": "Show the uploaded version in Shotgun.",
            #     "entity": entity
            # }

            action["callback"] = show_in_shotgun
            action["args"] = dict(entity=action.get("entity"))

            # add a label if not supplied
            if "label" not in action:
                action["label"] = "Show Folder"

            # add a tooltip if not supplied
            if "tooltip" not in action:
                action["tooltip"] = "Reveal the entity in Flow Production Tracking"

        elif action["type"] == "show_more_info":
            # A common action for showing more information than what
            # typically fits on a single line of logging output
            # {
            #     "label": "Show Error",
            #     "tooltip": "Show the full error stack trace.",
            #     "text": formatted_stack_trace,
            # }

            action["callback"] = show_more_info
            action["args"] = dict(
                pixmap=item.icon(0).pixmap(16, 16),
                message=item.text(0),  # the one line log message
                text=action.get("text", ""),
                parent=self._progress_details.log_tree,
            )

            # add a label if not supplied
            if "label" not in action:
                action["label"] = "More Info..."

            # add a tooltip if not supplied
            if "tooltip" not in action:
                action["tooltip"] = "Show additional logging info"

        elif action["type"] == "open_url":
            # A common action for opening a supplied url.
            # example: opening documentation in a browser
            # {
            #     "label": "Show Docs",
            #     "tooltip": "Show the associated documentation.",
            #     "url": url,
            # }

            action["callback"] = open_url
            action["args"] = dict(url=action.get("url"))

            # add a label if not supplied
            if "label" not in action:
                action["label"] = "Open URL"

            # add a tooltip if not supplied
            if "tooltip" not in action:
                action["tooltip"] = "Opens a url in the appropriate browser"

        else:
            logger.warning("Detected unrecognized action type: %s" % (action["type"],))
            return

        # make sure the required keys are defined
        for key in ["label", "callback", "args"]:
            if key not in action:
                logger.warning("Key '%s' is required for progress action." % (key,))
                return

        # create the button!
        embedded_widget = QtGui.QToolButton(self._progress_details.log_tree)
        embedded_widget.setObjectName("log_action_button")
        embedded_widget.setText(action["label"])
        embedded_widget.setToolTip(action.get("tooltip", ""))
        embedded_widget.clicked.connect(lambda: action["callback"](**action["args"]))

        self._progress_details.log_tree.setItemWidget(item, 1, embedded_widget)
