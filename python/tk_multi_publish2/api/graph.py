# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import sys
import traceback

try:
    import cPickle as pickle
except:
    import pickle

import sgtk
from .item import PublishItem

logger = sgtk.platform.get_logger(__name__)


class PublishGraph(object):
    """
    This class defines the internal representation of a publish graph. Instances
    store the relationships between items (the things to be published) and
    their child items. In addition to items, the graph instances store the tasks
    which operate on items. The tasks represent instances of a configured plugin
    that have been associated with an item.

    At a high level, a publish graph might be structured like this::

        * root
            * item1
                * itemA
                * itemB
            * item2
                * itemC
            * item3
                * itemD
            ...

    Each item in the graph (excluding the root) might have one or more
    associated tasks.

    The :class:`~.PublishGraph` class itself is strictly used for storing the
    associations between items and the tasks that are assigned to items. It has
    no knowledge of what the items represent or what the tasks do. It provides
    methods for traversing the graph and modifying it by
    adding/removing/modifying items and tasks.

    The class also provides an interface for serialization and deserialization
    of graph instances.
    """

    @staticmethod
    def load(file_path):
        """
        This method returns a new :class:`~.PublishGraph` instance by reading
        a serialized graph file from disk.

        :param file_path: The path to a serialized publish graph.
        :return: A :class:`~.PublishGraph` instance
        """

        with open(file_path, "rb") as graph_file:

            # In order to unpickle the file, we rely on the custom unpickler
            # factory. The factory will provide an Unpickler instance that
            # knows how to handle instances of classes that were pickled after
            # being imported using bundle.import_module(). See the unpickler
            # factory class below for more details.
            unpickler = _PublishGraphUnpicklerFactory.create(graph_file)
            try:
                graph = unpickler.load()
            except Exception:
                logger.error(
                    "There was an error trying to load the publish graph for "
                    "the file: %s.\n%s" % (file_path, traceback.format_exc())
                )
                raise

        return graph

    def __init__(self):
        """Initialize the publish graph instance."""

        # these internal members define the structure and relationships of the
        # graph itself. we intentionally only store complex objects in a single
        # place like _items, _tasks, and _plugins. All other lookups are id
        # based to keep the complexity down and simplify serialization of the
        # graph.
        self._child_lookup = {}
        self._items = []
        self._items_by_id = {}
        self._parent_lookup = {}
        self._plugins = {}
        self._tasks = []
        self._tasks_by_item = {}
        self._tasks_by_id = {}
        self._item_by_task = {}

        # The root item is the sole parent of all top-level publish items. It
        # has no use other than organization and provides an easy interface for
        # beginning iteration and accessing all top-level items.
        self._root_item = PublishItem(self, "root", "_root", "_root")
        self.add_item(self._root_item)

    def __iter__(self):
        """Iterates over the graph, depth first."""

        # start at the top and recurse down, yielding items as they're returned
        for item in self._traverse_graph(self._root_item):
            yield item

    def add_item(self, item, parent_item=None):
        """
        Add the supplied item to the graph.

        If a parent is supplied, make it the parent of the supplied item. If no
        parent is supplied, the root item will be the parent.

        :param item: The item to add to the graph. A :class:`~.item.PublishItem`
            instance.
        :param parent_item: The item to parent ``item`` to. A
            :class:`~.item.PublishItem` instance.
        """

        # if specified, ensure the parent item is in the graph
        if parent_item and parent_item.id not in self._items_by_id:
            raise sgtk.TankError(
                "Can not add item %s to the graph because the specified parent "
                "item, %s, does not exist in the graph." % (item, parent_item)
            )

        # use the root if no parent specified and the item being added isn't
        # the root item itself. This means the root item should be the only item
        # without a parent.
        if not parent_item and item != self._root_item:
            parent_item = self._root_item

        # make sure the item doesn't already exist in the graph
        if item.id in self._items_by_id:
            raise sgtk.TankError(
                "The supplied item already exists in the graph.")

        # initialize the child list for the item. this is where we'll store a
        # list of child item ids as they're added to the model with this item
        # as the parent
        self._child_lookup[item.id] = []

        # add the item to the list of items. Note, we're using a list here to
        # maintain order
        self._items.append(item)

        # for convenience, create a lookup by id. this allows us to quickly
        # check if an item already exists in the graph given that we're storing
        # the actual objects in a list.
        self._items_by_id[item.id] = item

        # add the item to the parent and child lookups
        if parent_item:
            # create a quick look up from item to parent and vice versa
            self._parent_lookup[item.id] = parent_item.id
            self._child_lookup[parent_item.id].append(item.id)

        # prepopulate the list of tasks for the item. this is where we'll store
        # a list of tasks associated with this item as they are attached to
        # this item during collection
        self._tasks_by_item[item.id] = []

    def remove_item(self, item):
        # TODO!
        pass

        # remove from items list
        # remove from items_by_id dict
        # remove from parent lookup
        # remove from child lookups
        # do the same for any children recursively

    def add_plugin(self, plugin):
        """Add the supplied plugin to the graph.

        This method is used to store a plugin instance with the graph. This
        allows the graph to house all plugin instance definitions so that the
        Tasks only need store the task-specific settings to be used during
        execution.

        This method typically does not need to be called externally as this is
        handled automatically during Task instance initialization.

        :param plugin: A :class:`~.plugins.PublishPluginInstace` hook with
            configured settings that the graph should be aware of.
        """

        if plugin.id in self._plugins:
            logger.debug(
                "Skipping adding plugin %s to the graph. "
                "It was previously added ot the graph." %
                (plugin,)
            )

        self._plugins[plugin.id] = plugin

    def add_task(self, task, parent_item):
        """
        Add a task to an item.

        The supplied task is associated with the supplied parent item by adding
        it to the list of associated tasks.

        :param task: The :class:`~.task.PublishTask` to associate with the
            supplied item.
        :param parent_item: The :class:`~.item.PublishItem` the task will be
            associated with.
        """

        # ensure the task's plugin has been added to the graph
        if task.plugin.id not in self._plugins:
            raise sgtk.TankError(
                "Unable to add task '%s' to the graph. It references a plugin "
                "that the graph is unaware of. Please be sure to add the "
                "plugin to the graph first by calling `add_plugin()`."
            )

        # ensure the parent item actually exists in the graph
        if parent_item.id not in self._items_by_id:
            raise sgtk.TankError(
                "Unable to add task '%s' to item '%s'. The item does not exist "
                "in the graph."
            )

        # update the internal state to reflect the new task/item association
        self._tasks.append(task)
        self._tasks_by_id[task.id] = task
        self._tasks_by_item[parent_item.id].append(task.id)
        self._item_by_task[task.id] = parent_item.id

    def get_parent(self, child_item):
        """
        Returns the parent item for the supplied child item.

        Will return the root item if the supplied item is a top-level publish
        item. Will return ``None`` if the supplied item is the root item.

        :param child_item: The item for which the parent will be returned.
        :return: A :class:`~.item.PublishItem` instance.
        """

        # use the parent lookup to find the parent item's id
        parent_id = self._parent_lookup.get(child_item.id)
        return self._items_by_id.get(parent_id)

    # TODO: resume here!
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


class _PublishGraphUnpicklerFactory(object):

    MAPPED_MODULES = {}

    @classmethod
    def unpickle_find_class(cls, module_name, class_name):

        # given a namespaced module/classname, return the same module in the new
        # tk namespace. example module name:
        #     tkimp4b0b5e4c49974e21813a21928b101a9f.tk_multi_publish2.base_hooks
        #          ^------------------------------^
        #           this part will be different in
        #           a separate/reloaded tk process

        matched_class = None

        if module_name.startswith("tkimp"):

            if module_name not in cls.MAPPED_MODULES:

                module_parts = module_name.split(".")
                actual_module_name = ".".join(module_parts[1:])

                for (sys_module_name, sys_module) in sys.modules.iteritems():
                    if sys_module_name.endswith(actual_module_name):
                        cls.MAPPED_MODULES[module_name] = getattr(
                            sys_module, class_name)
                        break

            matched_class = cls.MAPPED_MODULES.get(module_name)

        return matched_class

    @classmethod
    def create(cls, file_obj):

        if pickle.__name__ == "cPickle":
            unpickler = pickle.Unpickler(file_obj)
            unpickler.find_global = cls.unpickle_find_class
        else:
            class UnpicklerSubclass(pickle.Unpickler):
                find_class = staticmethod(cls.unpickle_find_class)
            unpickler = UnpicklerSubclass(file_obj)

        return unpickler
