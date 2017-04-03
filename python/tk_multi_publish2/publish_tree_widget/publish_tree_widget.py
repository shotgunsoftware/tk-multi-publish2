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
import collections
from sgtk.platform.qt import QtCore, QtGui
from .tree_node import TreeNodeContext, TreeNodeTask, TreeNodeItem, TopLevelTreeNodeItem

logger = sgtk.platform.get_logger(__name__)


class PublishTreeWidget(QtGui.QTreeWidget):
    """
    Main widget
    """

    def __init__(self, parent):
        """
        :param parent: The parent QWidget for this control
        """
        super(PublishTreeWidget, self).__init__(parent)
        self._plugin_manager = None
        self._dragged_items = []
        self._bundle = sgtk.platform.current_bundle()
        # make sure that we cannot drop items on the root item
        self.invisibleRootItem().setFlags(QtCore.Qt.ItemIsEnabled)

        # 20 px indent for items
        self.setIndentation(20)
        # no indentation for the top level items
        self.setRootIsDecorated(False)
        # turn off keyboard focus - this is to disable the
        # dotted lines around the widget which is selected.
        self.setFocusPolicy(QtCore.Qt.NoFocus)



    def set_plugin_manager(self, plugin_manager):
        self._plugin_manager = plugin_manager

    def _build_item_tree_r(self, item, level, tree_parent):
        """
        Build the tree of items
        """
        if len(item.tasks) == 0 and len(item.children) == 0:
            # orphan. Don't create it
            return None

        if level == 0:
            ui_item = TopLevelTreeNodeItem(item, tree_parent)
        else:
            ui_item = TreeNodeItem(item, tree_parent)
        ui_item.setExpanded(True)

        for task in item.tasks:
            task = TreeNodeTask(task, ui_item)

        for child in item.children:
            self._build_item_tree_r(child, level+1, ui_item)

        return ui_item

    def build_tree(self):
        """
        Rebuilds the tree
        """

        # group items by context
        items_by_context = collections.defaultdict(list)
        for item in self._plugin_manager.top_level_items:
            items_by_context[item.context].append(item)

        logger.debug("Building tree.")
        self.clear()

        for (context, items) in items_by_context.iteritems():
            context_item = TreeNodeContext(context, self)
            context_item.setExpanded(True)
            self.addTopLevelItem(context_item)
            for item in items:
                self._build_item_tree_r(item, level=0, tree_parent=context_item)

        empty_ctx = self._bundle.sgtk.context_empty()
        context_item = TreeNodeContext(empty_ctx, self)
        context_item.setExpanded(True)
        self.addTopLevelItem(context_item)


    def dropEvent(self, event):
        super(PublishTreeWidget, self).dropEvent(event)

        for item in self._dragged_items:
            print "item %s" % item
            item.create_widget()
            # and do it for all children

            def _check_r(parent):
                for child_index in xrange(parent.childCount()):
                    child = parent.child(child_index)
                    child.create_widget()
                    _check_r(child)

            _check_r(item)

        #self._dagged_items = []




    def dragEnterEvent(self, event):

        self._dragged_items = self.selectedItems()
        super(PublishTreeWidget, self).dragEnterEvent(event)


    def mouseMoveEvent(self, event):

        if self.state() != QtGui.QAbstractItemView.DragSelectingState:
            # bubble
            print "bubble"
            super(PublishTreeWidget, self).mouseMoveEvent(event)

