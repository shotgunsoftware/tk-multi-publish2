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

logger = sgtk.platform.get_logger(__name__)



class Task(object):
    """
    A plugin instance or the particular action that
    should be carried out by a plugin on an item.
    """

    def __init__(self, plugin, item):
        self._plugin = plugin
        self._item = item
        self._settings = []
        self._enabled = False
        self._required = False


    def __repr__(self):
        return "<Task: %s for %s >" % (self._plugin, self._item)

    def set_plugin_defaults(self, required, enabled):
        self._required = required
        self._enabled = enabled

    @property
    def item(self):
        return self._item

    @property
    def plugin(self):
        return self._plugin

    @property
    def settings(self):
        return self._settings

    @property
    def required(self):
        return True

    @property
    def enabled(self):
        return True