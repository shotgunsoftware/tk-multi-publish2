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
from sgtk.platform.qt import QtCore, QtGui
from .ui.task_widget import Ui_TaskWidget
from .custom_widget_base import CustomTreeWidgetBase

logger = sgtk.platform.get_logger(__name__)


class CustomTreeWidgetTask(CustomTreeWidgetBase):
    """
    Widget representing a single item in the left hand side tree view.
    (Connected to a designer ui setup)

    Each item has got the following associated properties:

    - An area which can either be a checkbox for selection
      or a "dot" which signals progress udpates

    - An icon

    - A header text

    These widgets are plugged in as subcomponents inside a QTreeWidgetItem
    via the PublishTreeWidget class hierarchy.
    """

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super(CustomTreeWidgetTask, self).__init__(tree_node, parent)

        # set up the UI
        self.ui = Ui_TaskWidget()
        self.ui.setupUi(self)
        self.set_status(self.NEUTRAL)

        self.ui.checkbox.stateChanged.connect(self._on_checkbox_click)

        self.ui.status.clicked.connect(self._on_status_click)

    def _on_checkbox_click(self, state):
        """
        Callback that fires when the user clicks the checkbox
        """
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            logger.debug("shift held. propagating check to all plugins.")
            self._tree_node.set_check_state(state, apply_to_all_plugins=True)
        else:
            self._tree_node.set_check_state(state, apply_to_invisible_siblings=True)

    def _on_status_click(self):
        """
        Callback that fires when the user clicks the status icon
        """
        current_task = self._tree_node.task
        self._tree_node.treeWidget().status_clicked.emit(current_task)
