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
        self._embedded_widget = self._create_widget()

    def _create_widget(self):
        """
        Create the widget that is used to visualise the node

        :returns: widget instance
        """
        raise NotImplementedError()

    @property
    def check_state(self):
        return self.data(0, self.CHECKBOX_ROLE)

    def set_check_state(self, state):
        """
        Called by child item when checkbox was ticked
        """
        print "check!"
        # first store it in our data model
        self.setData(0, self.CHECKBOX_ROLE, state)
        self._embedded_widget.set_checkbox_value(self.data(0, self.CHECKBOX_ROLE))
        if state == QtCore.Qt.Checked:
            # ensure all children are checked
            for child_index in range(self.childCount()):
                self.child(child_index).set_check_state(QtCore.Qt.Checked)
        elif state == QtCore.Qt.Unchecked:
            # uncheck all children
            for child_index in range(self.childCount()):
                self.child(child_index).set_check_state(QtCore.Qt.Unchecked)
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


    def begin_process(self):
        """
        Reset progress state
        """
        if self.enabled:
            # enabled nodes get a dotted ring
            self._embedded_widget.set_status(self._embedded_widget.PROCESSING)
        else:
            # unchecked items just get empty
            self._embedded_widget.set_status(self._embedded_widget.EMPTY)

    def _set_status_upwards(self, status):
        """
        Traverse all parents and set them to be a certain status
        """
        self._embedded_widget.set_status(status)
        if self.parent():
            self.parent()._set_status_upwards(status)

    def validate(self):
        """
        Perform validation
        """
        self._embedded_widget.set_status(self._embedded_widget.VALIDATION_COMPLETE)
        return True

    def publish(self):
        """
        Perform publish
        """
        self._embedded_widget.set_status(self._embedded_widget.PUBLISH_COMPLETE)
        return True

    def finalize(self):
        """
        Perform finalize
        """
        self._embedded_widget.set_status(self._embedded_widget.FINALIZE_COMPLETE)
        return True

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return self._embedded_widget.icon


