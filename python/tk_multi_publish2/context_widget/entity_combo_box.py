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

from .entity_model import EntityModel



class EntityComboBox(QtGui.QComboBox):
    """
    Context setting combo box with a built in hierarchy tree
    """

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(EntityComboBox, self).__init__(parent)
        self._bundle = sgtk.platform.current_bundle()
        # helper to track if the tree is being manipulated
        # or if we are selecting something
        self._skip_next_hide = False
        # helper to track if a shotgun object is being selected
        self._selected_entity = False

    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """
        # associate a data model
        self._context_model = EntityModel(
            self,
            bg_task_manager=task_manager
        )
        # make sure it's sorted
        self._hierarchy_proxy = QtGui.QSortFilterProxyModel(self)
        self._hierarchy_proxy.setSourceModel(self._context_model)
        # Sort alphabetically
        self._hierarchy_proxy.sort(0)
        self._hierarchy_proxy.setDynamicSortFilter(True)

        # create a treeview to embed in combo
        self._context_tree = QtGui.QTreeView(self)
        self._context_tree.setObjectName("context_widget_tree")
        self._context_tree.setHeaderHidden(True)
        # make sure the popup isn't too small when displaying the tree
        self._context_tree.setMinimumSize(QtCore.QSize(20, 300))

        # associate model with treeview
        self._context_tree.setModel(self._hierarchy_proxy)

        # associate model and view with combo
        self.setModel(self._hierarchy_proxy)
        self.setView(self._context_tree)

        # add logic to help track navigation vs selection
        self.view().viewport().installEventFilter(self)

    def get_selected_entity(self):
        """
        Returns the currently selected shotgun entity

        :returns: Selected entity nav dict or None if nothing selected.
        """
        if not self._selected_entity:
            return None

        current_index = self.view().selectionModel().currentIndex()

        # get the item from the source model
        selected_item = self._context_model.itemFromIndex(
            # get the source hierarchy model index
            self._hierarchy_proxy.mapToSource(current_index)
        )
        if selected_item is None:
            return None

        return selected_item.get_sg_data()

    def set_entity(self, entity):
        """
        Initialize the combo in a default state set to the given entity
        :param dict entity: Std Shotgun dictionary with name, type and id
        """
        # tell data model to update
        self._context_model.set_entity(entity)

    def hidePopup(self):
        """
        Overridden logic to determine when the popout should contract
        """
        self._selected_entity = False
        if self._skip_next_hide:
            self._skip_next_hide = False
        else:
            super(EntityComboBox, self).hidePopup()
            self._selected_entity = True

    def eventFilter(self, obj, event):
        """
        Event filter to track the tree navigation
        """
        if event.type() == QtCore.QEvent.MouseButtonPress and obj == self.view().viewport():
            index = self.view().indexAt(event.pos())

            if not self.view().visualRect(index).contains(event.pos()):
                self._skip_next_hide = True
            else:
                # see if index is a non-sg node
                selected_item = self._context_model.itemFromIndex(
                    # get the source hierarchy model index
                    self._hierarchy_proxy.mapToSource(index)
                )

                sg_data = selected_item.get_sg_data()
                if sg_data["ref"]["kind"] not in ["entity", "current_context"]:
                    # this is not a shotgun entity so don't collapse the tree
                    self._skip_next_hide = True

        return False
