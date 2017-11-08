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

logger = sgtk.platform.get_logger(__name__)



class TreeNodeBase(QtGui.QTreeWidgetItem):
    """
    Base class for all tree widgets.

    Each of these QTreeWidgetItem objects encapsulate an
    Item widget which is used to display the actual UI
    for the tree node.
    """

    CHECKBOX_ROLE = QtCore.Qt.UserRole + 1001

    def __init__(self, parent):
        """
        :param parent: The parent QWidget for this control
        """
        super(TreeNodeBase, self).__init__(parent)
        self.build_internal_widget()

        self.setFlags(QtCore.Qt.ItemIsEnabled)

    def build_internal_widget(self):
        """
        Create the widget and reassign it

        @return:
        """
        tree_widget = self.treeWidget()
        self._embedded_widget = self._create_widget(tree_widget)
        tree_widget.setItemWidget(self, 0, self._embedded_widget)

    def _create_widget(self):
        """
        Create the widget that is used to visualise the node

        :returns: widget instance
        """
        raise NotImplementedError()

    def get_publish_instance(self):
        """
        Returns the low level item or task instance
        that this object represents

        :returns: task or item instance
        """
        return None

    @property
    def check_state(self):
        return self.data(0, self.CHECKBOX_ROLE)

    @property
    def enabled(self):
        return self.check_state != QtCore.Qt.Unchecked

    def set_check_state(self, state):
        """
        Called by child item when checkbox was ticked
        """
        self._set_check_state_r(state)
        # emit tree level signal
        self.treeWidget().checked.emit(self)

    def _set_check_state_r(self, state):
        """
        Called by child item when checkbox was ticked
        """
        # do if for just this item
        # first store it in our data model
        self.setData(0, self.CHECKBOX_ROLE, state)
        self._embedded_widget.set_checkbox_value(self.data(0, self.CHECKBOX_ROLE))
        if state == QtCore.Qt.Checked:
            # ensure all children are checked
            for child_index in range(self.childCount()):
                self.child(child_index)._set_check_state_r(QtCore.Qt.Checked)
        elif state == QtCore.Qt.Unchecked:
            # uncheck all children
            for child_index in range(self.childCount()):
                self.child(child_index)._set_check_state_r(QtCore.Qt.Unchecked)
        # tell parent to recompute
        if self.parent():
            self.parent().recompute_check_state()

    def recompute_check_state(self):

        # look at immediate children, determine status, set status, recurse up
        checked = 0
        unchecked = 0
        for child_index in range(self.childCount()):
            if self.child(child_index).check_state == QtCore.Qt.Checked:
                checked += 1
            elif self.child(child_index).check_state == QtCore.Qt.Unchecked:
                unchecked += 1

        if checked == self.childCount():
            # all checked
            state = QtCore.Qt.Checked
        elif unchecked == self.childCount():
            state = QtCore.Qt.Unchecked
        else:
            state = QtCore.Qt.PartiallyChecked

        # set value
        self.setData(0, self.CHECKBOX_ROLE, state)
        self._embedded_widget.set_checkbox_value(self.data(0, self.CHECKBOX_ROLE))

        # proceed up
        if self.parent():
            self.parent().recompute_check_state()

    def create_summary(self):
        """
        Creates summary of actions

        :returns: List of strings
        """
        return []

    def reset_progress(self):
        """
        Reset progress state
        """
        self._embedded_widget.set_status(self._embedded_widget.NEUTRAL)

    # message is for the status icon tooltip. The status is propagated to
    # parents, but the message is not.
    def _set_status_upwards(self, status, message, info_below = False):
        """
        Traverse all parents and set them to be a certain status
        """
        self._embedded_widget.set_status(status, message, info_below)
        if self.parent():
            self.parent()._set_status_upwards(
                status,
                "There are issues with some of the items in this group.",
                True
            )

    def validate(self, standalone):
        """
        Perform validation
        """
        if standalone:
            self._embedded_widget.set_status(
                self._embedded_widget.VALIDATION_STANDALONE)
        else:
            self._embedded_widget.set_status(self._embedded_widget.VALIDATION)
        return True

    def publish(self):
        """
        Perform publish
        """
        self._embedded_widget.set_status(self._embedded_widget.PUBLISH)
        return True

    def finalize(self):
        """
        Perform finalize
        """
        self._embedded_widget.set_status(self._embedded_widget.FINALIZE)
        return True

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return self._embedded_widget.icon



