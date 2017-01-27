# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import re
import sgtk
import collections

from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)

from .errors import PluginValidationError, PluginNotFoundError, ValidationFailure, PublishFailure
from sgtk import TankError


from .setting import Setting


class Connection(object):
    """
    The connection between a plugin and an item
    """

    def __init__(self, plugin, item):
        self._plugin = plugin
        self._item = item
        self._settings = []
        self._enabled = False
        self._required = False


    def __repr__(self):
        return "<Connection %s -- %s >" % (self._plugin, self._item)

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