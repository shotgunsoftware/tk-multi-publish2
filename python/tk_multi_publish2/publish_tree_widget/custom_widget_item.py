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
from .ui.item_widget import Ui_ItemWidget
from .custom_widget_base import CustomTreeWidgetBase

logger = sgtk.platform.get_logger(__name__)




class CustomTreeWidgetItem(CustomTreeWidgetBase):
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

    # indexes for the widget's stacked drag handle sub widget
    (DRAGGABLE, LOCKED) = range(2)

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super(CustomTreeWidgetItem, self).__init__(tree_node, parent)

        # set up the UI
        self.ui = Ui_ItemWidget()
        self.ui.setupUi(self)

        self.set_status(self.NEUTRAL)

        # hide the handle by default
        self.hide_drag_handle()

        self.ui.checkbox.stateChanged.connect(self._on_checkbox_click)
        self.ui.checkbox.nextCheckState = self.nextCheckState
        self.ui.status.clicked.connect(self._on_status_click)

    def nextCheckState(self):
        """
        Callback that handles QT tri-state logic
        """
        # QT tri-state logic is a little odd, see the docs for more
        # details.
        self.ui.checkbox.setChecked(not self.ui.checkbox.isChecked())
        self._tree_node.set_check_state(self.ui.checkbox.checkState())

    def _on_checkbox_click(self, state):
        """
        Callback that fires when the user clicks the checkbox
        """
        self._tree_node.set_check_state(state)

    def _on_status_click(self):
        """
        Callback that fires when the user clicks the status icon
        """
        current_item = self._tree_node.item
        self._tree_node.treeWidget().status_clicked.emit(current_item)

    def hide_drag_handle(self):
        """Hides the drag handle stack widget"""
        self.ui.handle_stack.hide()

    def show_drag_handle(self, draggable):
        """
        Shows the stack widget with the drag icon if ``draggable`` is True.

        If ``draggable`` is ``False``, show the lock.
        """

        # the locked state is really a placeholder. it currently only displays
        # a label of the same size as the drag icon. this allows the rest of
        # the widget to align with other item widgets that do have a drag
        # handle displayed

        state = self.DRAGGABLE if draggable else self.LOCKED

        self.ui.handle_stack.show()
        self.ui.handle_stack.setCurrentIndex(state)

