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

logger = sgtk.platform.get_logger(__name__)


class CustomTreeWidgetBase(QtGui.QFrame):
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

    # status of checkbox / progress
    (
        NEUTRAL,
        PROCESSING,
        VALIDATION_COMPLETE,
        VALIDATION_ERROR,
        PUBLISH_ERROR,
        PUBLISH_COMPLETE,
        FINALIZE_COMPLETE,
        FINALIZE_ERROR,
        EMPTY
    ) = range(9)

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super(CustomTreeWidgetBase, self).__init__(parent)
        self._tree_node = tree_node

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return self.ui.icon.pixmap()

    def set_icon(self, pixmap):
        """
        Set the icon to be used

        :param pixmap: Square icon pixmap to use
        """
        self.ui.icon.setPixmap(pixmap)

    def set_header(self, title):
        """
        Set the title of the item

        :param title: Header text. Can be html.
        """
        self.ui.header.setText(title)

    def _update_check_state(self, state):
        """
        Communicate the value of the checkbox back to the associated node
        """
        self._tree_node.set_check_state(state)

    def set_checkbox_value(self, state):
        """
        Set the value of the checkbox
        """
        if state == QtCore.Qt.Checked:
            self.ui.checkbox.setCheckState(QtCore.Qt.Checked)
        elif state == QtCore.Qt.PartiallyChecked:
            self.ui.checkbox.setCheckState(QtCore.Qt.PartiallyChecked)
        else:
            self.ui.checkbox.setCheckState(QtCore.Qt.Unchecked)

    def set_status(self, status):
        """
        Set the status for the plugin
        :param status: An integer representing on of the
            status constants defined by the class
        """
        # reset
        self.ui.status.show_nothing()

        if status == self.NEUTRAL:
            # do nothing
            pass

        elif status == self.PROCESSING:
            # gray ring
            self.ui.status.show()
            self.ui.status.show_dot(ring_color="#808080", fill_color=None, dotted=True)

        elif status == self.VALIDATION_COMPLETE:
            # blue ring
            self.ui.status.show_dot(ring_color="#18A7E3", fill_color=None)

        elif status == self.VALIDATION_ERROR:
            # orange ring
            self.ui.status.show_dot(ring_color="#FF8000", fill_color=None)

        elif status == self.PUBLISH_COMPLETE:
            # blue fill gray ring
            self.ui.status.show_dot(ring_color="#FFF", fill_color="#18A7E3")

        elif status == self.PUBLISH_ERROR:
            # big fat red
            self.ui.status.show_dot(ring_color="#FF0000", fill_color="#FF0000")

        elif status == self.FINALIZE_COMPLETE:
            # blue dot
            self.ui.status.show_dot(ring_color="#18A7E3", fill_color="#18A7E3")

        elif status == self.FINALIZE_ERROR:
            # red ring blue middle
            self.ui.status.show_dot(ring_color="#FF0000", fill_color="#18A7E3")

        else:
            raise sgtk.TankError("Invalid item status!")


