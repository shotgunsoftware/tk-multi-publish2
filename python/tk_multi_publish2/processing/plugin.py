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



class Plugin(object):

    def __init__(self, name, path, settings, logger):

        # all plugins need a hook and a name
        self._name = name
        self._path = path
        self._raw_config_settings = settings

        self._bundle = sgtk.platform.current_bundle()

        # init the plugin
        self._plugin = self._bundle.create_hook_instance(self._path)

        self._configured_settings = {}
        self._required_runtime_settings = {}
        self._tasks = []

        self._logger = logger

        self._validate_and_resolve_config()


    def __repr__(self):
        return "<Publish Plugin %s>" % self._path

    def _validate_and_resolve_config(self):
        """
        Validate all values. Resolve links
        """
        try:
            settings_defs = self._plugin.settings
        except AttributeError:
            # property not defined by the hook
            logger.debug("no settings property defined by hook")
            settings_defs = {}

        for settings_def_name, settings_def_params in settings_defs.iteritems():
            # todo - validate that the hook provides the relevant params
            if settings_def_name in self._raw_config_settings:
                # this setting was provided by the config
                # todo - validate
                self._configured_settings[settings_def_name] = self._raw_config_settings[settings_def_name]
            else:
                # this setting needs to be pulled from the UI
                # todo - ensure all keys are set
                self._required_runtime_settings[settings_def_name] = settings_def_params

    @property
    def name(self):
        # name as defined in the env config
        return self._name

    @property
    def tasks(self):
        return self._tasks

    @property
    def title(self):
        try:
            return self._plugin.title
        except AttributeError:
            return "Untitled Integration."

    @property
    def description(self):
        try:
            return self._plugin.description_html
        except AttributeError:
            return "No detailed description provided."

    @property
    def subscriptions(self):
        try:
            return self._plugin.subscriptions
        except AttributeError:
            return []

    @property
    def icon_pixmap(self):
        try:
            icon_path = self._plugin.icon
            try:
                pixmap = QtGui.QPixmap(icon_path)
                return pixmap
            except Exception, e:
                logger.warning(
                    "%r: Could not load icon '%s': %s" % (self, icon_path, e)
                )
        except AttributeError:
            return None

    @property
    def resolved_settings(self):
        """
        returns a dict of resolved raw settings given the current state
        """
        return {}


    @property
    def required_settings(self):
        """
        Settings required to be specified by a UI or external process
        {
            "version_number": {"type": "int", "default": 5, "description": "foo bar baz"}
        }
        """
        settings = []
        for (setting_name, setting_params) in self._required_runtime_settings.iteritems():
            settings.append(Setting(setting_name, setting_params))
        return settings


    def add_task(self, task):
        self._tasks.append(task)

    def run_accept(self, item):

        resolved_settings = {}

        return self._plugin.accept(self._logger, resolved_settings, item)

