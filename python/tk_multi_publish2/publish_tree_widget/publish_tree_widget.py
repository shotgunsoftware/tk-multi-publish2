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
from collections import defaultdict
from sgtk.platform.qt import QtCore, QtGui
from .tree_node_context import TreeNodeContext
from .tree_node_task import TreeNodeTask
from .tree_node_item import TreeNodeItem, TopLevelTreeNodeItem
from .tree_node_summary import TreeNodeSummary

logger = sgtk.platform.get_logger(__name__)


class PublishTreeWidget(QtGui.QTreeWidget):
    """
    Publish tree widget which contains context, summary, tasks and items.
    """

    # emitted when a status icon is clicked
    status_clicked = QtCore.Signal(object)
    # emitted when the tree has been rearranged using drag n drop
    tree_reordered = QtCore.Signal()
    # emitted when a checkbox has been clicked in the tree
    # passed the TreeNodeBase instance
    checked = QtCore.Signal(object)

    # keep a handle on all items created for the tree. the publisher is
    # typically a transient interface, so this shouldn't be an issue in terms of
    # sucking up memory. hopefully this will eliminate some of the
    # "Internal C++ object already deleted" errors we're seeing.
    __created_items = []

    def __init__(self, parent):
        """
        :param parent: The parent QWidget for this control
        """
        super(PublishTreeWidget, self).__init__(parent)
        self._plugin_manager = None
        self._selected_items_state = []
        self._bundle = sgtk.platform.current_bundle()
        # make sure that we cannot drop items on the root item
        self.invisibleRootItem().setFlags(QtCore.Qt.ItemIsEnabled)

        # 20 px indent for items
        self.setIndentation(28)
        # no indentation for the top level items
        self.setRootIsDecorated(False)
        # turn off keyboard focus - this is to disable the
        # dotted lines around the widget which is selected.
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # create the summary node and add to the tree
        self._summary_node = TreeNodeSummary(self)
        self.addTopLevelItem(self._summary_node)
        self._summary_node.setHidden(True)

        # forward double clicks on items to the items themselves
        self.itemDoubleClicked.connect(lambda i, c: i.double_clicked(c))

    def set_plugin_manager(self, plugin_manager):
        """
        Associate a plugin manager.

        This should be done once and immediately after
        construction. The reason it is not part of the constructor
        is to allow the widget to be used in QT Designer.

        :param plugin_manager: Plugin manager instance
        """
        self._plugin_manager = plugin_manager

    def _build_item_tree_r(self, item, enabled, level, tree_parent):
        """
        Build a subtree of items, recursively, for the given item

        :param item: Low level processing item instance
        :param bool enabled: flag to indicate that the item is enabled
        :param int level: recursion depth
        :param QTreeWidgetItem tree_parent: parent node in tree
        """
        if len(item.tasks) == 0 and len(item.children) == 0:
            # orphan. Don't create it
            return None

        if level == 0:
            ui_item = TopLevelTreeNodeItem(item, tree_parent)
        else:
            ui_item = TreeNodeItem(item, tree_parent)

        self.__created_items.append(ui_item)

        # set expand state for item
        ui_item.setExpanded(item.expanded)

        # see if the node is enabled. This setting propagates down
        enabled &= item.enabled

        # create children
        for task in item.tasks:
            task = TreeNodeTask(task, ui_item)
            self.__created_items.append(task)

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
        Rebuilds the tree, ensuring that it is in sync with
        the low level plugin manager state.

        Does this in a lazy way in order to preserve as much
        state is possible.
        """

        logger.debug("Building tree.")

        # pass 1 - check if there is any top level item in the tree which shouldn't be there.
        #          also build a list of all top level items in the tree
        #          also check for items where the context has changed (e.g. so they need to move)
        #
        top_level_items_in_tree = []
        items_to_move = []
        for top_level_index in xrange(self.topLevelItemCount()):
            top_level_item = self.topLevelItem(top_level_index)

            if not isinstance(top_level_item, TreeNodeContext):
                # skip summary
                continue

            # go backwards so that when we take stuff out we don't
            # destroy the indices
            for item_index in reversed(range(top_level_item.childCount())):
                item = top_level_item.child(item_index)

                if item.item not in self._plugin_manager.top_level_items:
                    # no longer in the plugin mgr. remove from tree
                    top_level_item.takeChild(item_index)
                else:
                    # an active item
                    top_level_items_in_tree.append(item.item)
                    # check that items are parented under the right context
                    if str(item.item.context) != str(top_level_item.context):
                        # this object needs moving!
                        (item, state) = self.__take_item(top_level_item, item_index)
                        items_to_move.append((item, state))

        # now put all the moved items in
        for item, state in items_to_move:
            self.__insert_item(item, state)

        # pass 2 - check that there aren't any dangling contexts
        # process backwards so that when we take things out we don't
        # destroy the list
        for top_level_index in reversed(range(self.topLevelItemCount())):
            top_level_item = self.topLevelItem(top_level_index)

            if not isinstance(top_level_item, TreeNodeContext):
                # skip summary
                continue

            if top_level_item.childCount() == 0:
                self.takeTopLevelItem(top_level_index)

        # pass 3 - see if anything needs adding
        for item in self._plugin_manager.top_level_items:
            if item not in top_level_items_in_tree:
                self.__add_item(item)

        # finally, see if we should show the summary widget or not
        if len(self._plugin_manager.top_level_items) < 2:
            self._summary_node.setHidden(True)
        else:
            self._summary_node.setHidden(False)

    def __ensure_context_node_exists(self, context):
        """
        Make sure a node representing the context exists in the tree

        :param context: Toolkit context
        :returns: context item object
        """
        # first find the right context
        context_tree_node = None
        for context_index in xrange(self.topLevelItemCount()):
            context_item = self.topLevelItem(context_index)
            if isinstance(context_item, TreeNodeContext) and str(context_item.context) == str(context):
                context_tree_node = context_item

        if context_tree_node is None:
            # context not found! Create it!
            context_tree_node = TreeNodeContext(context, self)
            self.__created_items.append(context_tree_node)
            context_tree_node.setExpanded(True)
            self.addTopLevelItem(context_tree_node)

        return context_tree_node

    def __get_item_state(self, item):
        """
        Extract the state for the given tree item.
        Use :meth:`__set_item_state` to apply the returned data.

        :param item: Item to operate on
        :returns: dict with state
        """
        state = {
            "selected": item.isSelected(),
            "expanded": item.isExpanded()
        }
        return state

    def __set_item_state(self, item, state):
        """
        Applies state previously extracted with :meth:`__get_item_state` to an item.

        :param item: Item to operate on
        :param state: State dictionary to apply, as returned by :meth:`__get_item_state`
        """
        item.setSelected(state["selected"])
        item.setExpanded(state["expanded"])

    def __take_item(self, parent, index):
        """
        Takes out the given widget out of the tree
        and captures its state. This is meant to be used
        in conjunction with :meth:`__insert_item`.

        :param parent: parent item
        :param index: index of the item to take out
        :returns: (item, state)
        :rtype: (QTreeWidgetItem, dict)
        """
        state = self.__get_item_state(parent.child(index))
        item = parent.takeChild(index)
        return item, state

    def __insert_item(self, widget_item, state):
        """
        Inserts the given item into the tree

        :param widget_item: item to put in
        :param dict state: state dictionary as created by :meth:`__take_item`.
        """
        context_tree_node = self.__ensure_context_node_exists(widget_item.item.context)
        context_tree_node.addChild(widget_item)

        # re-initialize the item recursively
        _init_item_r(widget_item)

        # restore its state
        self.__set_item_state(widget_item, state)

        # if the item is selected, scroll to it after the move
        if widget_item.isSelected():
            widget_item.treeWidget().scrollToItem(widget_item)

    def __add_item(self, processing_item):
        """
        Create a node in the tree to represent the given top level item

        :param processing_item: processing module item instance.
        """
        context_tree_node = self.__ensure_context_node_exists(processing_item.context)

        # now add the new node
        self._build_item_tree_r(
            processing_item,
            enabled=True,
            level=0,
            tree_parent=context_tree_node
        )

    def get_full_summary(self):
        """
        Compute a full summary report.

        :returns: (num_items, string with html)
        """
        summary = []
        num_items = 0
        for context_index in xrange(self.topLevelItemCount()):
            context_item = self.topLevelItem(context_index)
            summary.extend(context_item.create_summary())
            tasks = self._summarize_tasks_r(context_item)

            # values of the tasks dictionary contains
            # how many items there are for each type
            num_items += sum(tasks.values())
            # iterate over dictionary and build histogram
            for task_name, num_tasks in tasks.iteritems():
                if num_tasks == 1:
                    summary.append("&ndash; %s: 1 item<br>" % task_name)
                else:
                    summary.append("&ndash; %s: %s items<br>" % (task_name, num_tasks))

        if len(summary) == 0:
            summary_text = "Nothing will published."

        else:
            summary_text = "".join(["%s" % line for line in summary])

        return (num_items, summary_text)

    def _summarize_tasks_r(self, node):
        """
        Recurses down and counts tasks

        :param node: The root node to begin recursion from
        :returns: Dictionary keyed by task name and where the
            value represents the number of instances of that task.
        """
        tasks = defaultdict(int)
        for child_index in xrange(node.childCount()):
            child = node.child(child_index)
            if isinstance(child, TreeNodeTask) and child.enabled:
                task_obj = child.task
                tasks[task_obj.plugin.name] += 1
            else:
                # process children
                child_tasks = self._summarize_tasks_r(child)
                for task_name, num_task_instances in child_tasks.iteritems():
                    tasks[task_name] += num_task_instances
        return tasks

    def select_first_item(self):
        """
        Selects the summary if it exists,
        otherwise selects he first item in the tree.
        """
        self.clearSelection()

        logger.debug("Selecting first item in the tree..")
        if self.topLevelItemCount() == 0:
            logger.debug("Nothing to select!")
            return

        # summary item is always the first one
        summary_item = self.topLevelItem(0)
        if not summary_item.isHidden():
            logger.debug("Selecting the summary node")
            self.setCurrentItem(summary_item)

        else:
            # summary hidden. select first item instead.
            first_item = None
            for context_index in xrange(1, self.topLevelItemCount()):
                context_item = self.topLevelItem(context_index)
                for child_index in xrange(context_item.childCount()):
                    first_item = context_item.child(child_index)
                    break
            if first_item:
                self.setCurrentItem(first_item)
                logger.debug("No summary node present. Selecting %s" % first_item)
            else:
                logger.debug("Nothing to select!")

    def set_check_state_for_all_plugins(self, plugin, state):
        """
        Set the check state for all items associated with the given plugin

        :param plugin: Plugin for which tasks should be manipulated
        :param state: checkstate to set.
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

        for item, state in self._selected_items_state:

            # make sure that the item picks up the new context
            if isinstance(item, TopLevelTreeNodeItem):
                item.synchronize_context()

            # re-initialize the item recursively
            _init_item_r(item)

            # restore state after drop
            self.__set_item_state(item, state)

        self.tree_reordered.emit()

    def dragEnterEvent(self, event):
        """
        Event triggering when a drag operation starts
        """
        # record selection for use later.
        self._selected_items_state = []

        dragged_items = []
        selected_items_state = []

        # process all selected items
        for item in self.selectedItems():

            # we only want to drag/drop top level items
            if isinstance(item, TopLevelTreeNodeItem):

                # ensure context change is allowed before dragging/dropping
                if not item.item.context_change_allowed:
                    # deselect to prevent drag/drop of items whose context
                    # can't be changed
                    item.setSelected(False)

                dragged_items.append(item)

            else:
                # deselect to prevent drag/drop of non top level items
                item.setSelected(False)

            # keep the state of all selected items to restore post-drop
            state = self.__get_item_state(item)
            selected_items_state.append((item, state))

        # ignore any selection that does not contain at least one TopLevelTreeNodeItems
        if not dragged_items:
            logger.debug("No top-level nodes included in selection.")        
            return

        self._selected_items_state = selected_items_state

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

def _init_item_r(parent_item):

    # qt seems to drop the associated widget
    # (http://doc.qt.io/qt-4.8/qtreewidget.html#setItemWidget)
    # when a tree node is taken out of the tree, either via drag n drop
    # or via explicit manipulation. So make sure that we recreate
    # the internal widget as part of re-inserting the node into the tree.
    parent_item.build_internal_widget()

    # do this for all children of the supplied item recursively
    for child_index in xrange(parent_item.childCount()):
        child = parent_item.child(child_index)
        child.setExpanded(True)
        _init_item_r(child)

