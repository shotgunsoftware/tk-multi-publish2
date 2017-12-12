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
from .plugin import PublishPlugin, CollectorPlugin
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

        # here we maintain a lookup items generated for a given path. this dict
        # is rebuild whenever a full refresh of the tree is created.
        self._path_to_item_lookup = {}

        logger.debug("Loading plugin configuration")
        self._publish_plugins = []

        plugin_defs = self._bundle.get_setting("publish_plugins")

        # create publish plugin objects
        for plugin_def in plugin_defs:
            logger.debug("Find config chunk %s" % plugin_def)

            publish_plugin_instance_name = plugin_def["name"]
            publish_plugin_hook_path = plugin_def["hook"]
            publish_plugin_settings = plugin_def["settings"]

            plugin = PublishPlugin(
                publish_plugin_instance_name,
                publish_plugin_hook_path,
                publish_plugin_settings,
                self._logger
            )
            self._publish_plugins.append(plugin)
            logger.debug("Created %s" % plugin)

        # create collector plugin object
        collector_hook_path = self._bundle.get_setting("collector")
        collector_settings = self._bundle.get_setting("collector_settings")

        self._collector = CollectorPlugin(
            collector_hook_path,
            collector_settings,
            self._logger
        )

        # create an item root
        self._root_item = Item.create_invisible_root_item()

        # initalize tasks
        self._tasks = []

    @property
    def top_level_items(self):
        """
        Returns a list of the items which reside on the top level
        of the tree, e.g. all the children of the invisible root item.

        :returns: List if :class:`Item` instances
        """
        return self._root_item.children

    def remove_top_level_item(self, item_to_remove):
        """
        Removed the given item from the list of top level items
        """

        # since we keep a look of items created from browsed/dropped external
        # files, we can check to see if the item to be deleted is one of those.
        # if it is, we need to remove that item from the lookup and remove the
        # path from the list of external files we're tracking. first, see if the
        # item matches any items created for a path. there should only be one,
        # but we'll check all items in the lookup to be sure.
        paths_to_delete = []
        for (path, item_for_path) in self._path_to_item_lookup.iteritems():
            if item_for_path == item_to_remove:
                paths_to_delete.append(path)

        # now we iterate over the matched paths and remove them from the list of
        # external files and the item lookup.
        for path in paths_to_delete:
            del self._path_to_item_lookup[path]

        self._root_item.remove_item(item_to_remove)

    @property
    def plugins(self):
        """
        Returns a list of the plugin instances loaded from the configuration

        :returns: List of :class:`Plugin` instances.
        """
        return self._publish_plugins

    def run_collectors(self):
        """
        Reestablishes the state. Recomputes everything.

        :returns: List of items created
        """
        logger.debug("Refresh: Removing existing objects")
        self._root_item = Item.create_invisible_root_item()

        # this is a full refresh, so we clear out this lookup. it will be
        # regenerated as items are created for all the external files. before
        # clearning the lookup, get a list of all external files collected.
        external_files = self._path_to_item_lookup.keys()
        self._path_to_item_lookup = {}

        logger.debug("Refresh: Running collection on current scene")
        # process the current scene
        current_scene_items_created = self._collect(
            collect_current_scene=True
        )

        logger.debug("Refresh: Running collection on all external files")
        # process all external paths
        external_files_items_created = self._collect(
            collect_current_scene=False,
            paths=external_files
        )

        return len(current_scene_items_created) + len(external_files_items_created)

    def add_external_files(self, paths):
        """
        Runs the collector for the given set of paths

        :param str paths: List of full file path
        :returns: Number of items created by collectors
        """

        # now run the collection for all the new items
        logger.debug("Running scene collection for new paths")
        items_created = self._collect(
            collect_current_scene=False,
            paths=paths
        )
        return len(items_created)

    def clear_external_files(self):
        """
        Removes all external files
        """
        self._path_to_item_lookup = {}

        self.run_collectors()

    def _collect(self, collect_current_scene, paths=None):
        """
        Runs the collector and generates fresh items.

        :param bool collect_current_scene: Boolean to indicate if collection should
            be performed for the current scene, e.g. if the collector hook's
            process_current_session() method should be executed.
        :param paths: List of paths for which the collector hook's method
            process_file() should be executed for
        :returns: Items created by collectors
        """
        # get existing items
        all_items_before = self._get_item_tree_as_list()

        # pass 1 - collect stuff from the scene and other places
        logger.debug("Executing collector")

        if collect_current_scene:
            self._collector.run_process_current_session(self._root_item)

        if paths:
            for path in paths:
                # we only want to collect file paths for which items have not
                # already been created. we can check the path to item lookup
                # to see if the path already exists as a key. this means that
                # this file path has already been collected and an item
                # created. if the path doesn't exist, we run the collection
                # method and populate the lookup with the item created
                if path in self._path_to_item_lookup:
                    logger.debug("Skipping duplicate path '%s'" % path)
                else:
                    logger.debug("Adding external file '%s'" % path)
                    item = self._collector.run_process_file(self._root_item, path)
                    self._path_to_item_lookup[path] = item

        # get all items after scan
        all_items_after = self._get_item_tree_as_list()

        # get list of new things
        all_new_items = list(set(all_items_after) - set(all_items_before))

        # now we have a series of items from the scene, visit our plugins
        # to see if there is interest
        logger.debug("Visiting all plugins and offering items")
        for plugin in self._publish_plugins:

            for item in self._get_matching_items(plugin.item_filters, all_new_items):
                logger.debug("seeing if %s is interested in %s" % (plugin, item))
                accept_data = plugin.run_accept(item)
                if accept_data.get("accepted"):
                    # this item was accepted by the plugin!
                    # look for bools accepted/visible/enabled/checked

                    # TODO: Implement support for this!
                    # all things are visible by default unless stated otherwise
                    is_visible = accept_data.get("visible", True)

                    # all things are checked by default unless stated otherwise
                    is_checked = accept_data.get("checked", True)

                    # all things are enabled by default unless stated otherwise
                    is_enabled = accept_data.get("enabled", True)

                    task = Task.create_task(plugin, item, is_visible, is_enabled, is_checked)
                    self._tasks.append(task)

        return all_new_items

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

