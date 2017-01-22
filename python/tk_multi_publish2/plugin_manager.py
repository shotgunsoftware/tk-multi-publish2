# Copyright (c) 2015 Shotgun Software Inc.
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
            # maintain a ordered list
            self._plugins.append(Plugin(plugin_def, self))

        # now in a second pass validate and resolve
        for plugin in self.plugins:
            plugin.validate_and_resolve_config()

    @property
    def plugins(self):
        """
        Returns a list of plugins, in the order they were defined
        """
        for plugin in self._plugins:
            yield plugin

    def get_plugin(self, name):
        """
        Find a plugin given its name

        :param name: name of a plugin
        :returns: :class:`Plugin` instance
        :raises: :class:`PluginNotFoundError`
        """
        for plugin in self._plugins:

            if plugin.name == name:
                return plugin

        raise PluginNotFoundError("Plugin %s does not exist as part of the configuration" % name)


