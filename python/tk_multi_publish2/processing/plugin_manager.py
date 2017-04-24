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
import fnmatch
from .plugin import Plugin
from .item import Item
from .task import Task

logger = sgtk.platform.get_logger(__name__)


class PluginManager(object):
    """
    Manager which handles hook initialization and execution.
    """

    def __init__(self, publish_logger):
        """
        :param publish_logger: A logger object that the
            various hooks can send logging information to.
        """
        logger.debug("Plugin manager waking up")

        self._bundle = sgtk.platform.current_bundle()

        self._logger = publish_logger

        logger.debug("Loading plugin configuration")
        self._plugins = []

        plugin_defs = self._bundle.get_setting("publish_plugins")

        # create plugin objects
        for plugin_def in plugin_defs:
            logger.debug("Find config chunk %s" % plugin_def)

            plugin_instance_name = plugin_def["name"]
            hook_path = plugin_def["hook"]
            settings = plugin_def["settings"]

            plugin = Plugin(plugin_instance_name, hook_path, settings, self._logger)
            self._plugins.append(plugin)
            logger.debug("Created %s" % plugin)

        # create an item root
        self._root_item = Item.create_invisible_root_item()

        # initalize tasks
        self._tasks = []

        # process the current scene
        self._collect(collect_current_scene=True)

    @property
    def top_level_items(self):
        """
        Returns a list of the items which reside on the top level
        of the tree, e.g. all the children of the invisible root item.

        :returns: List if :class:`Item` instances
        """
        return self._root_item.children

    def remove_top_level_item(self, item):
        """
        Removed the given item from the list of top level items
        """
        self._root_item.remove_item(item)

    @property
    def plugins(self):
        """
        Returns a list of the plugin instances loaded from the configuration

        :returns: List of :class:`Plugin` instances.
        """
        return self._plugins

    def add_external_files(self, paths):
        """
        Runs the collector for the given set of paths

        :param str paths: List of full file path
        """
        logger.debug("Adding external files '%s'" % paths)
        self._collect(collect_current_scene=False, paths=paths)

    def _collect(self, collect_current_scene, paths=None):
        """
        Runs the collector and generates fresh items.

        :param bool collect_current_scene: Boolean to indicate if collection should
            be performed for the current scene, e.g. if the collector hook's
            process_current_session() method should be executed.
        :param paths: List of paths for which the collector hook's method
            process_file() should be executed for
        """
        # get existing items
        all_items_before = self._get_item_tree_as_list()

        # pass 1 - collect stuff from the scene and other places
        logger.debug("Executing collector")

        if collect_current_scene:
            self._bundle.execute_hook_method(
                "collector",
                "process_current_session",
                parent_item=self._root_item
            )

        if paths:
            for path in paths:
                self._bundle.execute_hook_method(
                    "collector",
                    "process_file",
                    parent_item=self._root_item,
                    path=path
                )

        # get all items after scan
        all_items_after = self._get_item_tree_as_list()

        # get list of new things
        all_new_items = list(set(all_items_after) - set(all_items_before))

        # now we have a series of items from the scene, visit our plugins
        # to see if there is interest
        logger.debug("Visiting all plugins and offering items")
        for plugin in self._plugins:

            for item in self._get_matching_items(plugin.item_filters, all_new_items):
                logger.debug("seeing if %s is interested in %s" % (plugin, item))
                accept_data = plugin.run_accept(item)
                if accept_data.get("accepted"):
                    # this item was accepted by the plugin!
                    # look for bools accepted/visible/enabled/checked

                    # TODO ---- Implement support for this!
                    # all things are visible by default unless stated otherwise
                    is_visible = accept_data.get("visible", True)

                    # all things are checked by default unless stated otherwise
                    is_checked = accept_data.get("checked", True)

                    # all things are enabled by default unless stated otherwise
                    is_enabled = accept_data.get("enabled", True)

                    task = Task.create_task(plugin, item, is_visible, is_enabled, is_checked)
                    self._tasks.append(task)



    def _get_matching_items(self, item_filters, all_items):
        """
        Given a list of item filters from a plugin,
        yield a series of matching items. Items are
        randomly ordered.

        :param item_filters: List of item filters to glob against.
        :param all_items: Items to match against.
        """
        for item_filter in item_filters:
            logger.debug("Checking matches for item filter %s" % item_filter)
            # "maya.*"
            for item in all_items:
                if fnmatch.fnmatch(item.type, item_filter):
                    yield item

    def _get_item_tree_as_list(self):
        """
        Returns the item tree as a flat list.

        :returns: List if item objects
        """
        def _get_subtree_as_list_r(parent):
            items = []
            for child in parent.children:
                items.append(child)
                items.extend(_get_subtree_as_list_r(child))
            return items

        parent = self._root_item
        return _get_subtree_as_list_r(parent)

