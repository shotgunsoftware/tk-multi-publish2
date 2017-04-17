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
SimpleShotgunHierarchyModel = shotgun_model.SimpleShotgunHierarchyModel



class EntityComboBox(QtGui.QComboBox):
    """
    Context setting combo box with a built in hierarchy tree
    """

    def __init__(self, parent):

        super(EntityComboBox, self).__init__(parent)
        self._bundle = sgtk.platform.current_bundle()
        self._skip_next_hide = False

        self.addItem("Recent")
        self.addItem("Shot foo")
        self.insertSeparator(self.count())


    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """
        self._context_tree = QtGui.QTreeView(self)
        self._context_tree.setObjectName("context_widget_tree")
        self._context_tree.setHeaderHidden(True)

        self._context_model = SimpleShotgunHierarchyModel(
            self,
            bg_task_manager=task_manager
        )

        if self._bundle.context.project:
            # for a project context, show items for current project

            # TODO: remove hard coded paths - instead resolve the entity via the
            # self._bundle.shotgun.nav_search_entity() method - which currently
            # seems broken :(

            root_path = "/Project/%d" % self._bundle.context.project["id"]
        else:
            # show everything
            root_path = "/"

        # Show a hierarchy of published files. The rationale here is that
        # when you are in a DCC, your primary objective is to publish files, so
        # the hierarchy should outline items *for which files can be published.*
        published_file_entity_type = sgtk.util.get_published_file_entity_type(self._bundle.sgtk)
        seed = "%s.entity" % (published_file_entity_type,)

        self._context_model.load_data(
            seed,
            path=root_path,
            entity_fields={"__all__": ["code"]}
        )

        self._hierarchy_proxy = QtGui.QSortFilterProxyModel(self)
        self._hierarchy_proxy.setSourceModel(self._context_model)
        # Sort alphabetically
        self._hierarchy_proxy.sort(0)
        self._hierarchy_proxy.setDynamicSortFilter(True)

        self._context_tree.setModel(self._hierarchy_proxy)
        self.setModel(self._hierarchy_proxy)
        self.setView(self._context_tree)

        self.view().viewport().installEventFilter(self)



    def set_entity(self, entity):

        pass


    def hidePopup(self):
        if self._skip_next_hide:
            self._skip_next_hide = False
        else:
            super(EntityComboBox, self).hidePopup()


    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.MouseButtonPress and obj == self.view().viewport():
            index = self.view().indexAt(event.pos())
            if not self.view().visualRect(index).contains(event.pos()):
                self._skip_next_hide = True
        return False
