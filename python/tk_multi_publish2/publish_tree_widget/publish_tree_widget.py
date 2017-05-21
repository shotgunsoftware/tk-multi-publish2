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
    Main widget
    """

    # emitted when a status icon is clicked
    status_clicked = QtCore.Signal(object)
    # emitted when the tree has been rearranged using drag n drop
    tree_reordered = QtCore.Signal()
    # emitted when a checkbox has been clicked in the tree
    # passed the TreeNodeBase instance
    checked = QtCore.Signal(object)


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
        self.setIndentation(28)
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

        # get selected publish instances so that we can restore selection
        selected_publish_instances = []
        for item in self.selectedItems():
            selected_publish_instances.append(item.get_publish_instance())

        logger.debug("Building tree.")
        self.clear()

        # add summary if > 1 item
        if len(self._plugin_manager.top_level_items) > 1:
            summary = TreeNodeSummary(self)
            self.addTopLevelItem(summary)

        # group items by context
        # create a dictionary keyed by context
        # string representation
        items_by_context = {}
        for item in self._plugin_manager.top_level_items:

            ctx_key = str(item.context)
            if ctx_key not in items_by_context:
                items_by_context[ctx_key] = {
                    "context": item.context,
                    "items": []
                }

            items_by_context[ctx_key]["items"].append(item)

        # now build the tree
        for context_str in sorted(items_by_context.keys()):

            # extract the objects for this context
            context = items_by_context[context_str]["context"]
            items = items_by_context[context_str]["items"]

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

        # iterate over all the new tree items to restore selection
        for it in QtGui.QTreeWidgetItemIterator(self):
            item = it.value()
            if item.get_publish_instance() in selected_publish_instances:
                item.setSelected(True)
                self.scrollToItem(item, QtGui.QAbstractItemView.EnsureVisible)

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
        logger.debug("Selecting first item in the tree..")
        if self.topLevelItemCount() == 0:
            logger.debug("Nothing to select!")
            return

        first_top_level_item = self.topLevelItem(0)
        if isinstance(first_top_level_item, TreeNodeSummary):
            logger.debug("Selecting the summary node")
            self.setCurrentItem(first_top_level_item)

        else:
            # no summary. find first item node
            first_item = None
            for context_index in xrange(self.topLevelItemCount()):
                context_item = self.topLevelItem(context_index)
                for child_index in xrange(context_item.childCount()):
                    first_item = context_item.child(child_index)
                    break
            if first_item:
                self.setCurrentItem(first_item)
                logger.debug("No summary node present. Selecting %s" % first_item)
            else:
                logger.debug("Nothing to select!")

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

