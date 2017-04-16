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

logger = sgtk.platform.get_logger(__name__)

# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
SimpleShotgunModel = shotgun_model.SimpleShotgunModel



class TaskComboBox(QtGui.QComboBox):
    """
    Context setting combo box with a built in hierarchy tree
    """

    def __init__(self, parent):

        super(TaskComboBox, self).__init__(parent)
        self._bundle = sgtk.platform.current_bundle()

        self.addItem("Recent")
        self.addItem("Foo bar")
        self.addItem("Foo bar")
        self.addItem("Foo bar")
        self.insertSeparator(self.count())
        self.addItem("My Tasks")
        self.addItem("Foo bar")
        self.addItem("Foo bar")
        self.addItem("Foo bar")
        self.insertSeparator(self.count())
        self.addItem("Associated Tasks")
        self.addItem("Foo bar")
        self.addItem("Foo bar")
        self.addItem("Foo bar")


    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """

        self._model = SimpleShotgunModel(
            self,
            bg_task_manager=task_manager
        )

        self._hierarchy_proxy = QtGui.QSortFilterProxyModel(self)
        self._hierarchy_proxy.setSourceModel(self._model)
        # Sort alphabetically
        self._hierarchy_proxy.sort(0)
        self._hierarchy_proxy.setDynamicSortFilter(True)

        self.setModel(self._hierarchy_proxy)

        self._model.load_data(
            entity_type="Asset"
        )


    def set_entity(self, task):

        logger.debug("Set task!")