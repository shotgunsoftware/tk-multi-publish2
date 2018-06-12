# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import uuid

import sgtk
from .setting import Setting

logger = sgtk.platform.get_logger(__name__)


class PluginInstanceBase(object):
    """
    A base class for functionality common to plugin hooks (collectors and
    publish plugins).

    Each object reflects an instance in the app configuration.
    """

    def __init__(self, path, settings, publish_logger):
        """
        :param path: Path to the collector hook
        :param settings: Dictionary of collector-specific settings
        :param logger: a logger object that will be used by the hook
        """

        super(PluginInstanceBase, self).__init__()

        if not publish_logger:
            publish_logger = logger

        self._logger = publish_logger

        # every plugin created for use in the graph has a unique id
        self._id = uuid.uuid4().hex

        # all plugins need a hook and a name
        self._path = path
        self._configured_settings = settings

        self._settings = {}

        # create an instance of the hook
        # TODO: we need to make this picklable. implement __get/setstate__
        #       methods, storing the path
        self._hook_instance = self._create_hook_instance(self._path)

        # kick things off
        self._validate_and_resolve_config()

        self.logger.debug("Created: %s" % (self,))

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance. Subclasses can reimplement for more
        sophisticated hook instantiation.

        :param str path: The path to the hook file.
        :return: A hook instance
        """
        bundle = sgtk.platform.current_bundle()
        return bundle.create_hook_instance(path)

    def __getstate__(self):

        return {
            "id": self._id,
            "path": self._path,
            "configured_settings": self._configured_settings,
            "logger": self.logger.name,
            "settings": self._settings
        }

    def __setstate__(self, state):

        self._id = state["id"]
        self._path = state["path"]
        self._configured_settings = state["configured_settings"]
        self._logger = sgtk.platform.get_logger(state["logger"])
        self._settings = state["settings"]
        self._hook_instance = self._create_hook_instance(self._path)

    def __repr__(self):
        """
        String representation
        """
        return "<[%s] %s: %s>" % (self.id, self.__class__.__name__, self._path)

    def _validate_and_resolve_config(self):
        """
        Init helper method.

        Validates plugin settings and creates Setting objects
        that can be accessed from the settings property.
        """
        try:
            hook_settings_schema = self._hook_instance.settings
        except AttributeError, e:
            import traceback
            # property not defined by the hook
            logger.debug("no settings property defined by hook")
            hook_settings_schema = {}

        # Settings schema will be in the form:
        # "setting_a": {
        #     "type": "int",
        #     "default": 5,
        #     "description": "foo bar baz"
        # },

        for setting_name, setting_schema in hook_settings_schema.iteritems():

            # if the setting exists in the configured environment, grab that
            # value, validate it, and update the setting's value
            if setting_name in self._configured_settings:
                # this setting was provided by the config
                value = self._configured_settings[setting_name]
            else:
                # no value specified in the actual configuration
                value = setting_schema.get("default")

            # TODO: validate and resolve the configured setting

            setting = Setting(
                setting_name,
                data_type=setting_schema.get("type"),
                default_value=setting_schema.get("default"),
                description=setting_schema.get("description")
            )
            setting.value = value

            self._settings[setting_name] = setting

    @property
    def id(self):
        """The id of the plugin.

        This id is unique to the plugin and is persistent across serialization/
        deserialization.
        """
        return self._id

    @property
    def logger(self):
        return self._logger

    @property
    def settings(self):
        """
        Returns a dict of resolved raw settings given the current state
        """
        return self._settings
