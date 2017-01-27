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
from sgtk.platform.qt import QtCore, QtGui

from .plugin import Plugin
from .errors import PluginNotFoundError
from .item import Item
from .connection import Connection

logger = sgtk.platform.get_logger(__name__)


class PluginManager(QtCore.QObject):
    """
    Handles hook execution
    """

    def __init__(self, parent=None):
        """
        Constructor

        :param parent: The parent QWidget for this control
        """
        QtCore.QObject.__init__(self, parent)

        logger.debug("plugin manager waking up")

        self._bundle = sgtk.platform.current_bundle()

        logger.debug("Loading plugin configuration")
        self._plugins = []

        plugin_defs = self._bundle.get_setting("publish_plugins")

        for plugin_def in plugin_defs:
            logger.debug("Find config chunk %s" % plugin_def)

            hook_path = plugin_def["hook"]
            settings = plugin_def["settings"]

            # maintain a ordered list
            plugin = Plugin(hook_path, settings, logger)
            logger.debug("Created %s" % plugin)
            self._plugins.append(plugin)

        self._root_items = []
        self._all_items = []
        self._connections = []

    def _create_item(self, item_type, name, parent=None):
        """
        Callback to create item
        """
        item = Item(item_type, name, parent)
        self._all_items.append(item)
        if parent is None:
            self._root_items.append(item)
        logger.debug("created %s" % item)
        return item


    def _get_matching_items(self, subscriptions):
        """
        Given a list of subscriptions from a plugin,
        yield a series of matching items. Items are
        randomly ordered.
        """
        for subscription in subscriptions:
            logger.debug("Checking matches for subscription %s" % subscription)
            # {"type": "maya_node", "maya_type": "camera"},
            for item in self._all_items:
                if item.type == subscription["type"]:
                    # right type!
                    # check rest of properties
                    properties = subscription.keys()
                    item_matching = True
                    for property_name in properties:
                        if property_name == "type":
                            continue
                        if property_name not in item.properties or subscription[property_name] != item.properties[property_name]:
                            # not matching
                            item_matching = False
                            break
                    if item_matching:
                        logger.debug("    match: %s (%s)" % (item, item.properties))
                        yield item





    def collect(self):
        """
        Runs the collector and generates fresh items.
        @return:
        """

        # pass 1 - collect stuff from the scene and other places
        logger.debug("Collecting subscriptions from plugins")
        subscriptions = []
        for plugin in self._plugins:
            subscriptions.extend(plugin.subscriptions)

        # pass 2 - run the collector to generate item to match all
        # subscriptions
        logger.debug("Executing collector")
        self._bundle.execute_hook_method(
            "collector",
            "collect",
            subscriptions=subscriptions,
            create_item=self._create_item
        )

        # now we have a series of items from the scene, pass it back to the plugins to see which are interesting
        logger.debug("Visting all items")
        for plugin in self._plugins:
            logger.debug("visting %s" % plugin)
            for item in self._get_matching_items(plugin.subscriptions):
                accept_data = plugin.run_accept(item)
                if accept_data.get("accepted"):
                    # this item was accepted by the plugin!
                    # create a connection
                    connection = Connection(plugin, item)
                    is_required = accept_data.get("required") is True
                    is_enabled = accept_data.get("enabled") is True
                    connection.set_plugin_defaults(is_required, is_enabled)
                    self._connections.append(connection)


        # now do a cull to get the tree of plugins which


