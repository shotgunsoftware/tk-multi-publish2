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
from .tree_node_context import TreeNodeContext
from .tree_node_task import TreeNodeTask
from .tree_node_item import TreeNodeItem, TopLevelTreeNodeItem
from .tree_node_summary import TreeNodeSummary

logger = sgtk.platform.get_logger(__name__)


class PublishTreeWidget(QtGui.QTreeWidget):
    """
    Main widget
    """

    # emitted when a status icon is clicked
    status_clicked = QtCore.Signal(object)
    # emitted when the tree has been rearranged using drag n drop
    tree_reordered = QtCore.Signal()


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

    def _build_item_tree_r(self, item, enabled, level, tree_parent):
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

        # set expand state for item
        ui_item.setExpanded(item.expanded)

        # see if the node is enabled. This setting propagates down
        enabled &= item.enabled

        # create children
        for task in item.tasks:
            task = TreeNodeTask(task, ui_item)

        for child in item.children:
            self._build_item_tree_r(child, enabled, level+1, ui_item)

        # lastly, handle the item level check state.
        # if the item has been marked as checked=False
        # uncheck it now (which will affect all children)
        if not item.checked:
            ui_item.set_check_state(QtCore.Qt.Unchecked)

        return ui_item

    def build_tree(self):
        """
        Rebuilds the tree
        """
        logger.debug("Building tree.")
        self.clear()

        # add summary
        summary = TreeNodeSummary(self)
        self.addTopLevelItem(summary)

        # group items by context
        items_by_context = collections.defaultdict(list)
        for item in self._plugin_manager.top_level_items:
            items_by_context[item.context].append(item)


        for (context, items) in items_by_context.iteritems():
            context_item = TreeNodeContext(context, self)
            context_item.setExpanded(True)
            self.addTopLevelItem(context_item)
            for item in items:
                self._build_item_tree_r(
                    item,
                    enabled=True,
                    level=0,
                    tree_parent=context_item
                )


    def select_first_item(self):
        """
        Selects the first item in the tree
        """
        # select the top item
        if self.topLevelItemCount() > 0:
            # first context item
            first_context_item = self.topLevelItem(0)
            if first_context_item.childCount() > 0:
                # we got an item
                first_item = first_context_item.child(0)
                self.setCurrentItem(first_item)

    def set_state_for_all_plugins(self, plugin, state):
        """
        set the state for all plugins
        """

        logger.debug(
            "Setting state %d for all plugin %s" % (state, plugin)
        )

        def _check_r(parent):
            for child_index in xrange(parent.childCount()):
                child = parent.child(child_index)

                if isinstance(child, TreeNodeTask) and child.task.plugin == plugin:
                    child.set_check_state(state)

                _check_r(child)

        root = self.invisibleRootItem()
        _check_r(root)

    def dropEvent(self, event):
        """
        Something was dropped on this widget
        """
        # run default implementation
        super(PublishTreeWidget, self).dropEvent(event)

        #
        for item in self._dragged_items:
            item.build_internal_widget()
            item.setExpanded(True)
            item.setSelected(True)
            item.synchronize_context()

            # and do it for all children
            def _check_r(parent):
                for child_index in xrange(parent.childCount()):
                    child = parent.child(child_index)
                    child.build_internal_widget()
                    child.setExpanded(True)
                    _check_r(child)

            _check_r(item)

        self.tree_reordered.emit()

    def dragEnterEvent(self, event):
        """
        Event triggering when a drag operation starts
        """
        # record selection for use later.
        self._dragged_items = self.selectedItems()

        # ignore any selections which aren't purely made from TopLevelTreeNodeItems
        for item in self._dragged_items:
            if not isinstance(item, TopLevelTreeNodeItem):
                logger.debug("Selection contains non-top level nodes. Ignoring")
                return

        super(PublishTreeWidget, self).dragEnterEvent(event)

    def mouseMoveEvent(self, event):
        """
        Overridden mouse move event to suppress
        selecting multiple selection via the mouse since
        this makes drag and drop pretty weird.
        """
        if self.state() != QtGui.QAbstractItemView.DragSelectingState:
            # bubble up all events that aren't drag select related
            super(PublishTreeWidget, self).mouseMoveEvent(event)

