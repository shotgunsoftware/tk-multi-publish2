# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

#try:
#   import cPickle as pickle
#except:
#   import pickle
import pickle

import sgtk

from .item import PublishItem

logger = sgtk.platform.get_logger(__name__)


class PublishGraph(object):

    @staticmethod
    def load(path):

        with open(path, "rb") as graph_file:
            graph = pickle.load(graph_file)

        return graph

    def __init__(self):

        self._root_item = PublishItem(self, "root", "_root", "_root")

        # different structures define the graph itself
        self._child_lookup = {}
        self._items = []
        self._items_by_id = {}
        self._parent_lookup = {}
        self._plugins = {}
        self._tasks = []
        self._tasks_by_item = {}
        self._tasks_by_id = {}
        self._item_by_task = {}

        # be sure to add the root item
        self.add_item(self._root_item)

    def __iter__(self):
        """Iterates over the graph, depth first."""

        for item in self._traverse_graph(self._root_item):
            yield item

    def add_item(self, item, parent_item=None):

        item_ids = [n.id for n in self._items]

        # if specified, ensure the parent item is in the graph
        if parent_item and parent_item.id not in item_ids:
            raise LookupError(
                "Can not add item %s to the graph because the specified parent "
                "item, %s, does not exist in the graph." % (item, parent_item)
            )

        # use the root if no parent specified (and the item being added isn't
        # the root item itself)
        if not parent_item and item != self._root_item:
            parent_item = self._root_item

        # make sure the item doesn't already exist in the graph
        if item.id in item_ids:
            raise LookupError("The supplied item already exists in the graph.")

        # initialize the child list for the item
        self._child_lookup[item.id] = []

        # add the item to the list of items. Note, we're using a list here to
        # maintain order
        self._items.append(item)

        # for convenience, create a lookup by id
        self._items_by_id[item.id] = item

        # add the item to the parent and child lookups
        if parent_item:
            self._parent_lookup[item.id] = parent_item.id
            self._child_lookup[parent_item.id].append(item.id)

        # prepopulate the list of tasks for the item
        self._tasks_by_item[item.id] = []

    def remove_item(self, item):
        pass

        # remove from items list
        # remove from items_by_id dict
        # remove from parent lookup
        # remove from child lookups
        # do the same for any children recursively

    def add_plugin(self, plugin):

        if plugin.id in self._plugins:
            logger.debug(
                "Skipping adding plugin %s to the graph. "
                "It was previously added ot the graph." %
                (plugin,)
            )

        self._plugins[plugin.id] = plugin

    def add_task(self, task, parent_item):
        # TODO: docstring

        # ensure the task's plugin has been added to the graph
        if task.plugin.id not in self._plugins:
            raise LookupError(
                "Unable to add task '%s' to the graph. It references a plugin "
                "that the graph is unaware of. Please be sure to add the "
                "plugin to the graph first by calling `add_plugin()`."
            )

        item_ids = [n.id for n in self._items]

        if parent_item.id not in item_ids:
            raise LookupError(
                "Unable to add task '%s' to item '%s'. The item does not exist "
                "in the graph."
            )

        self._tasks.append(task)
        self._tasks_by_id[task.id] = task
        self._tasks_by_item[parent_item.id].append(task.id)
        self._item_by_task[task.id] = parent_item.id

    def get_parent(self, child_item):
        """Returns the parent of the supplied item."""

        parent_id = self._parent_lookup.get(child_item.id)

        if not parent_id:
            return None

        return self._items_by_id[parent_id]

    def get_children(self, parent_item):
        """Returns a list of all child items of the supplied parent."""
        child_item_ids = self._child_lookup[parent_item.id]

        child_items = []
        for child_item_id in child_item_ids:
            child_items.append(self._items_by_id[child_item_id])

        return child_items

    def get_items_for_ids(self, item_ids):
        """Return items in the graph for the supplied ids."""

        items = []

        for item_id in item_ids:
            if item_id in self._items_by_id:
                items.append(self._items_by_id[item_id])

        return items

    def get_item_for_task(self, task):
        """Returns the item the supplied task is associated with."""
        item_id = self._item_by_task.get(task.id)
        return self._items_by_id.get(item_id)

    def get_plugin_by_id(self, plugin_id):
        """Returns the plugin for the given plugin id."""
        return self._plugins.get(plugin_id)

    def get_tasks(self, item):
        """Return a list of all the tasks attached to the supplied item."""

        if not item.id in self._items_by_id:
            raise LookupError(
                "Unable to get tasks for item '%s'. The item has not been "
                "added to the graph." % (item,)
            )

        task_ids = self._tasks_by_item.get(item.id)

        tasks = []
        for task_id in task_ids:
            tasks.append(self._tasks_by_id[task_id])

        return tasks

    def save(self, path):
        """Save the graph to disk at the supplied path."""

        with open(path, "wb") as graph_file:
            try:
                pickle.dump(self, graph_file, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:
                import traceback
                logger.debug(traceback.format_exc())
                raise

    @property
    def items(self):
        """Returns a list of all items in the graph. Order is not guaranteed."""
        return self._items

    @property
    def root_item(self):
        """Returns the root item of this graph."""
        return self._root_item

    def _traverse_graph(self, parent_item):
        """Depth first traversal of the supplied item."""

        for item in self.get_children(parent_item):
            yield item
            for child_item in self._traverse_graph(item):
                yield child_item
