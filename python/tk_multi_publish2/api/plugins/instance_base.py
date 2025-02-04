# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from .setting import PluginSetting

logger = sgtk.platform.get_logger(__name__)


class PluginInstanceBase(object):
    """
    A base class for functionality common to plugin hooks (collectors and
    publish plugins).

    Each object reflects an instance in the app configuration.
    """

    def __init__(self, path, settings, publish_logger):
        """
        Initialize a plugin instance.

        :param path: Path to the collector hook
        :param settings: Dictionary of collector-specific settings
        :param publish_logger: a logger object that will be used by the hook
        """

        super().__init__()

        if not publish_logger:
            publish_logger = logger

        self._logger = publish_logger

        # all plugins need a hook and a name
        self._path = path
        self._configured_settings = settings

        self._settings = {}

        # create an instance of the hook
        self._hook_instance = self._create_hook_instance(self._path)

        # kick things off
        self._validate_and_resolve_config()

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance. Subclasses can reimplement for more
        sophisticated hook instantiation.

        :param str path: The path to the hook file.
        :return: A hook instance
        """
        bundle = sgtk.platform.current_bundle()
        return bundle.create_hook_instance(path)

    def __repr__(self):
        """
        String representation
        """
        return "<%s: %s>" % (self.__class__.__name__, self._path)

    def _validate_and_resolve_config(self):
        """
        Init helper method.

        Validates plugin settings and creates PluginSetting objects
        that can be accessed from the settings property.
        """
        try:
            hook_settings_schema = self._hook_instance.settings
        except AttributeError:
            # property not defined by the hook
            logger.debug("no settings property defined by hook")
            hook_settings_schema = {}

        # Settings schema will be in the form:
        # "setting_a": {
        #     "type": "int",
        #     "default": 5,
        #     "description": "foo bar baz"
        # },

        for setting_name, setting_schema in hook_settings_schema.items():

            # if the setting exists in the configured environment, grab that
            # value, validate it, and update the setting's value
            if setting_name in self._configured_settings:
                # this setting was provided by the config
                value = self._configured_settings[setting_name]
            else:
                # no value specified in the actual configuration
                value = setting_schema.get("default")

            # TODO: validate and resolve the configured setting

            setting = PluginSetting(
                setting_name,
                data_type=setting_schema.get("type"),
                default_value=setting_schema.get("default"),
                description=setting_schema.get("description"),
            )
            setting.value = value

            self._settings[setting_name] = setting

    @property
    def configured_settings(self):
        """
        A dictionary of settings data as originally specified for this plugin
        instance in the pipeline configuration.
        """
        return self._configured_settings

    @property
    def logger(self):
        """
        The logger used by this plugin instance.
        """
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        # set the plugin's logger instance
        self._logger = new_logger

    @property
    def path(self):
        """The path to this plugin as specified in the pipeline config."""
        return self._path

    @property
    def settings(self):
        """
        A dict of resolved raw settings given the current state
        """
        return self._settings
