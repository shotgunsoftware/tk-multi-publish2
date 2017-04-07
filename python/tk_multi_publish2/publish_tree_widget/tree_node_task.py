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
from .tree_node_base import TreeNodeBase
from .custom_widget_task import CustomTreeWidgetTask

logger = sgtk.platform.get_logger(__name__)




class TreeNodeTask(TreeNodeBase):
    """
    Tree item for a publish task
    """

    def __init__(self, task, parent):
        """
        :param task: Task instance
        :param parent: The parent QWidget for this control
        """
        self._task = task

        super(TreeNodeTask, self).__init__(parent)

        # tasks cannot be dragged or dropped on
        self.setFlags(QtCore.Qt.ItemIsEnabled)

        # set up defaults based on task settings
        self._embedded_widget.set_checkbox_value(
            QtCore.Qt.Checked if self._task.enabled else QtCore.Qt.Unchecked
        )

        if self._task.required:
            self._embedded_widget.ui.checkbox.setEnabled(False)
        else:
            self._embedded_widget.ui.checkbox.setEnabled(True)

    def __repr__(self):
        return "<TreeNodeTask %s>" % str(self)

    def __str__(self):
        return self._task.plugin.name

    def _create_widget(self):
        """
        Create the widget that is used to visualise the node
        """
        # create an item widget and associate it with this QTreeWidgetItem
        tree_widget = self.treeWidget()
        widget = CustomTreeWidgetTask(self, tree_widget)
        tree_widget.setItemWidget(self, 0, widget)

        widget.set_header(self._task.plugin.name)
        widget.set_icon(self._task.plugin.icon)
        widget.set_checkbox_value(self.data(0, self.CHECKBOX_ROLE))

        return widget

    @property
    def task(self):
        """
        Associated task instance
        """
        return self._task

    def validate(self):
        """
        Perform validation
        """
        try:
            status = self._task.validate()
        except Exception, e:
            self._set_status_upwards(self._embedded_widget.VALIDATION_ERROR)
            status = False
        else:
            if status:
                self._embedded_widget.set_status(self._embedded_widget.VALIDATION_COMPLETE)
            else:
                self._set_status_upwards(self._embedded_widget.VALIDATION_ERROR)
        return status

    def publish(self):
        """
        Perform publish
        """
        try:
            self._task.publish()
        except Exception, e:
            self._set_status_upwards(self._embedded_widget.PUBLISH_ERROR)
            raise
        else:
            self._embedded_widget.set_status(self._embedded_widget.PUBLISH_COMPLETE)
        return True

    def finalize(self):
        """
        Perform finalize
        """
        try:
            self._task.finalize()
        except Exception, e:
            self._set_status_upwards(self._embedded_widget.FINALIZE_ERROR)
            raise
        else:
            self._embedded_widget.set_status(self._embedded_widget.FINALIZE_COMPLETE)
        return True
