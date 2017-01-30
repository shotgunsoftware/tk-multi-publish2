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
from .errors import PluginNotFoundError
from .item import Item
from .task import Task

logger = sgtk.platform.get_logger(__name__)


class PluginManager(object):
    """
    Handles hook execution
    """

    def __init__(self):
        """
        Constructor

        :param parent: The parent QWidget for this control
        """
        logger.debug("plugin manager waking up")

        self._bundle = sgtk.platform.current_bundle()

        logger.debug("Loading plugin configuration")
        self._plugins = []

        plugin_defs = self._bundle.get_setting("publish_plugins")

        for plugin_def in plugin_defs:
            logger.debug("Find config chunk %s" % plugin_def)

            plugin_instance_name = plugin_def["name"]
            hook_path = plugin_def["hook"]
            settings = plugin_def["settings"]

            # maintain a ordered list
            plugin = Plugin(plugin_instance_name, hook_path, settings, logger)
            logger.debug("Created %s" % plugin)
            self._plugins.append(plugin)

        self._root_item = Item("_root", "_root", parent=None)
        self._all_items = []

        self._tasks = []
        self._external_files = []

    def add_external_file(self, path):
        logger.debug("Adding external file '%s'" % path)
        self._external_files.append(path)

    @property
    def top_level_items(self):
        return self._root_item.children

    def _get_matching_items(self, subscriptions):
        """
        Given a list of subscriptions from a plugin,
        yield a series of matching items. Items are
        randomly ordered.
        """
        for subscription in subscriptions:
            logger.debug("Checking matches for subscription %s" % subscription)
            # "maya.*"
            for item in self._all_items:
                if fnmatch.fnmatch(item.type, subscription):
                    yield item


    def _create_task(self, plugin, item):
        task = Task(plugin, item)
        plugin.add_task(task)
        item.add_task(task)
        logger.debug("Created %s" % task)
        return task

    def _populate_items_list(self, parent):
        for child in parent.children:
            self._all_items.append(child)
            self._populate_items_list(child)

    def collect(self):
        """
        Runs the collector and generates fresh items.
        """

        # pass 1 - collect stuff from the scene and other places
        logger.debug("Executing collector")
        self._bundle.execute_hook_method(
            "collector",
            "process_current_scene",
            parent_item=self._root_item
        )

        for path in self._external_files:
            self._bundle.execute_hook_method(
                "collector",
                "process_file",
                parent_item=self._root_item,
                path=path
            )

        # flatten list of items for easier processing
        self._populate_items_list(self._root_item)

        # now we have a series of items from the scene, pass it back to the plugins to see which are interesting
        logger.debug("Visiting all plugins and offering items")
        for plugin in self._plugins:

            for item in self._get_matching_items(plugin.subscriptions):
                logger.debug("seeing if %s is interested in %s" % (plugin, item))
                accept_data = plugin.run_accept(item)
                if accept_data.get("accepted"):
                    # this item was accepted by the plugin!
                    # create a task
                    task = self._create_task(plugin, item)
                    is_required = accept_data.get("required") is True
                    is_enabled = accept_data.get("enabled") is True
                    task.set_plugin_defaults(is_required, is_enabled)
                    self._tasks.append(task)

        # TODO: need to do a cull to remove any items in the tree which do not have tasks


