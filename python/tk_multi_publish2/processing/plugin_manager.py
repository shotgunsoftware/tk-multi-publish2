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
            plugin = Plugin(hook_path, settings)
            logger.debug("Created %s" % plugin)
            self._plugins.append(plugin)

        self._root_items = []
        self._all_items = []

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



    def collect(self):
        """
        Runs the collector and generates fresh items.
        @return:
        """

        # pass 1 - collect stuff from the scene and other places

        self._bundle.execute_hook_method(
            "collector",
            "collect",
            subscriptions=[],
            create_item=self._create_item
        )


        # now we have a series of items from the scene, see which ones are interesting for plugins


