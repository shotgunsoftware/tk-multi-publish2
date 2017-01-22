# Copyright (c) 2015 Shotgun Software Inc.
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

from .ui.item import Ui_Item

logger = sgtk.platform.get_logger(__name__)

class Item(QtGui.QFrame):
    """
    Represents a right hand side details pane in the UI
    """

    (NEUTRAL, VALIDATION_COMPLETE, VALIDATION_ERROR, PUBLISH_ERROR, PUBLISH_COMPLETE) = range(5)

    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        """
        Constructor
        
        :param parent:          The parent QWidget for this control
        """
        QtGui.QFrame.__init__(self, parent)

        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Raised)

        # set up the UI
        self.ui = Ui_Item()
        self.ui.setupUi(self)
        self.set_mode(self.NEUTRAL)
        self.ui.header_chk.setChecked(True)

        self._tasks = []
        self._current_row = 1
        self.ui.hidden_header.setVisible(False)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QFrame.mousePressEvent(self, event)
        self.clicked.emit()

    def select(self):
        """
        Mark as selected
        """
        self.setProperty("selected", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def deselect(self):
        """
        Mark as deselected
        """
        self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_mode(self, mode):
        """
        Specify which main mode the item should be in
        """
        self._set_mode(mode, self.ui.item_icon)

    def set_icon(self, icon):
        """
        Sets the icon to use. Should be a square pixmap, at least 64px
        """
        self.ui.item_icon.setPixmap(icon)

    def set_header(self, title, description):
        """
        Set the title of the item
        """
        self.ui.header.setText("<big>%s</big><br>%s" % (title, description))

    def add_task(self, name):
        """
        Add a task object
        """
        label = QtGui.QLabel(self)
        label.setObjectName("item_icon")
        label.setText(name)
        self.ui.gridLayout.addWidget(label, self._current_row, 0, 1, 1)

        checkbox = QtGui.QCheckBox(self)
        checkbox.setText("")
        checkbox.setChecked(True)
        checkbox.setObjectName("list_chk")
        self.ui.gridLayout.addWidget(checkbox, self._current_row, 1, 1, 1)

        self._current_row += 1

        self._tasks.append({"name": name, "label": label, "checkbox": checkbox})

        self.set_task_mode(name, self.NEUTRAL)

    def get_tasks(self):
        # todo - handle checkbox state
        return [x["name"] for x in self._tasks]

    def set_task_mode(self, task_name, mode):
        """
        Control the mode indication for a task
        @param task_name:
        @param mode:
        @return:
        """
        for task in self._tasks:
            if task["name"] == task_name:
                widget = task["label"]
                self._set_mode(mode, widget)

    def _set_mode(self, mode, widget):
        """
        Specify which main mode the item should be in
        """
        qss_lookup = {
            self.NEUTRAL: "neutral",
            self.VALIDATION_COMPLETE: "validation_complete",
            self.VALIDATION_ERROR: "validation_error",
            self.PUBLISH_COMPLETE: "publish_complete",
            self.PUBLISH_ERROR: "publish_error"
        }
        widget.setProperty("mode", qss_lookup[mode])
        widget.style().unpolish(widget)
        widget.style().polish(widget)
