# Copyright (c) 2017 Shotgun Software Inc
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

from .task_model import TaskModel
logger = sgtk.platform.get_logger(__name__)


class TaskComboBox(QtGui.QComboBox):
    """
    Context setting combo box with a built in hierarchy tree
    """

    def __init__(self, parent):
        super(TaskComboBox, self).__init__(parent)
        self._bundle = sgtk.platform.current_bundle()

    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """
        # create a model to drive the combo
        self._model = TaskModel(
            self,
            bg_task_manager=task_manager
        )
        # make sure it's alphabetically sorted
        self._proxy = QtGui.QSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
        self._proxy.sort(0)
        self._proxy.setDynamicSortFilter(True)
        self.setModel(self._proxy)

    def set_task(self, entity, task):
        """
        Sets the task associated with this combo
        :param dict entity: Sg dictionary with name, type and id
        :param dict task: Sg dictionary with name, type and id
        """
        self._model.set_task(entity, task)

    def get_selected_task_id(self):
        """
        Returns the currently selected task or None
        """
        current_index = self.view().selectionModel().currentIndex()

        # get the item from the source model
        selected_item = self._model.itemFromIndex(
            # get the source hierarchy model index
            self._proxy.mapToSource(current_index)
        )
        if selected_item is None:
            # nothing selected in combo
            return None

        sg_data = selected_item.get_sg_data()
        if sg_data is None:
            # the 'please select a task' item
            return None

        return selected_item.get_sg_data().get("id")
