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
from sgtk.platform.qt import QtCore
from .ui.item_widget import Ui_ItemWidget
from .custom_widget_base import CustomTreeWidgetBase

logger = sgtk.platform.get_logger(__name__)


class CustomTreeWidgetItem(CustomTreeWidgetBase):
    """
    Widget representing a single item in the left hand side tree view.
    (Connected to a designer ui setup)

    Each item has got the following associated properties:

    - An area which can either be a checkbox for selection
      or a "dot" which signals progress updates

    - An icon

    - A header text

    These widgets are plugged in as subcomponents inside a QTreeWidgetItem
    via the PublishTreeWidget class hierarchy.
    """

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super().__init__(tree_node, parent)

        # set up the UI
        self.ui = Ui_ItemWidget()
        self.ui.setupUi(self)

        self.set_status(self.NEUTRAL)

        # hide the drag handle by default
        self.ui.handle_stack.hide()

        # hide the expand placeholder by default
        self.ui.expand_placeholder.hide()

        self.ui.checkbox.stateChanged.connect(self._on_checkbox_click)
        self.ui.checkbox.nextCheckState = self.nextCheckState
        self.ui.status.clicked.connect(self._on_status_click)

    def nextCheckState(self):
        """
        Callback that handles QT tri-state logic
        """
        # Qt tri-state logic is a little odd. The default behaviour is to go from unchecked
        # to partially checked. We want it to go from unchecked to checked
        if self.ui.checkbox.checkState() == QtCore.Qt.CheckState.Checked:
            next_state = QtCore.Qt.CheckState.Unchecked
        else:
            next_state = QtCore.Qt.CheckState.Checked
        self.ui.checkbox.setCheckState(next_state)
        self._tree_node.set_check_state(next_state)

    def _on_checkbox_click(self, state):
        """
        Callback that fires when the user clicks the checkbox
        """
        # For PySide6 compatibility, convert state to CheckState enum if not already
        # an instance. Issue described at: https://forum.qt.io/post/743017
        if not isinstance(state, QtCore.Qt.CheckState):
            state = QtCore.Qt.CheckState(state)
        self._tree_node.set_check_state(state)

    def _on_status_click(self):
        """
        Callback that fires when the user clicks the status icon
        """
        current_item = self._tree_node.item
        self._tree_node.treeWidget().status_clicked.emit(current_item)

    def show_drag_handle(self, draggable):
        """
        Shows the stack widget with the drag icon if ``draggable`` is True.

        If ``draggable`` is ``False``, show the lock.
        """

        # the locked state is really a placeholder. it currently only displays
        # a label of the same size as the drag icon. this allows the rest of
        # the widget to align with other item widgets that do have a drag
        # handle displayed

        if draggable:
            self.ui.handle_stack.show()
            self.ui.handle_stack.setCurrentIndex(0)  # draggable
        else:
            self.ui.handle_stack.hide()

    @property
    def expand_indicator(self):
        """Exposes the expand_indicator widget."""
        return self.ui.expand_indicator

    @property
    def expand_placeholder(self):
        """Exposes the expand_placeholder widget."""
        return self.ui.expand_placeholder
