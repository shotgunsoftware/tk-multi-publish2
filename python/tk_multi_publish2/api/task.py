# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import copy

import sgtk
from .plugins import Setting, PublishPluginInstance

logger = sgtk.platform.get_logger(__name__)


class PublishTask(object):
    """
    A task is a particular unit of work which can to be carried by the
    publishing process. A task can be thought of as a 'plugin instance', or a
    particular publishing plugin operating on a collected item.
    """

    @classmethod
    def from_dict(cls, task_dict, serialization_version, item=None):
        """
        Returns an instance of a PublishTask from serialized data.

        :param task_dict: A dictionary of deserialized task data
        :param serialization_version: The version of serialization logic used to
            serialize this data.
        :param item: Optional item to associate with this task
        """

        # import here to avoid cyclic imports
        from .tree import PublishTree

        # This check is valid until we need to alter the way serialization is
        # handled after initial release. Once that happens, this should be
        # altered to handle the various versions separately with this as the
        # fallback when the serialization version is not recognized.
        if serialization_version != PublishTree.SERIALIZATION_VERSION:
            raise (
                "Unrecognized serialization version for serlialized publish "
                "task. It is unclear how this could have happened. Perhaps the "
                "serialized file was hand edited? Please consult your pipeline "
                "TD/developer/admin."
            )

        # create the plugin instance
        plugin = PublishPluginInstance(
            task_dict["plugin_name"],
            task_dict["plugin_path"],
            task_dict["plugin_settings"],
            logger  # TODO
        )

        new_task = PublishTask(plugin, item)
        new_task._name = task_dict["name"]
        new_task._description = task_dict["description"]
        new_task._active = task_dict["active"]
        new_task._visible = task_dict["visible"]
        new_task._enabled = task_dict["enabled"]

        for (k, setting) in task_dict["settings"].iteritems():
            new_setting = Setting(
                setting["name"],
                setting["type"],
                setting["default_value"],
                setting["description"]
            )
            new_setting.value = setting["value"]
            new_task._settings[k] = new_setting

        return new_task

    def __init__(self, plugin, item):
        """
        Initialize the task.
        """

        self._item = item
        self._plugin = plugin
        self._name = None # task name override of plugin name
        self._description = None # task description override of plugin desc.

        # need to make a deep copy of the settings
        self._settings = {}
        for (setting_name, setting) in plugin.settings.items():
            self._settings[setting_name] = copy.deepcopy(setting)

        self._active = True
        self._visible = True
        self._enabled = True

        logger.debug("Created publish tree task: %s" % (self,))

    def to_dict(self):

        converted_settings = {}
        for (k, setting) in self._settings.iteritems():
            converted_settings[k] = setting.to_dict()

        return {
            "plugin_name": self.plugin.name,
            "plugin_path": self.plugin.path,
            "plugin_settings": self.plugin.configured_settings,
            # TODO: plugin logger
            "name": self._name,
            "description": self._description,
            "settings": converted_settings,
            "active": self._active,
            "visible": self._visible,
            "enabled": self._enabled,
        }

    def __repr__(self):
        """Representation of the item as a string."""
        return "<%s: %s>" % (self.__class__.__name__, self._name)

    def __str__(self):
        """Human readable representation of the task."""
        return self.name

    def validate(self):
        """
        Validate this Task

        :returns: True if validation succeeded, False otherwise.
        """
        return self.plugin.run_validate(self.settings, self.item)

    def publish(self):
        """
        Publish this Task
        """
        self.plugin.run_publish(self.settings, self.item)

    def finalize(self):
        """
        Finalize this Task
        """
        self.plugin.run_finalize(self.settings, self.item)

    @property
    def active(self):
        """
        Returns the item's active state if it has been explicitly set, `None``
        otherwise
        """
        return self._active

    @active.setter
    def active(self, active_state):
        """
        Explicitly set the active state.

        There are 3 active states that can be supplied:

        * ``True``: Set the item to be active
        * ``False``: Set the item to be inactive
        * ``None``: Clear the item's state, rely on inheritance within the tree
        """
        self._active = active_state

    @property
    def description(self):
        """
        The description of the item if it has been explicitly set,
        ``None`` otherwise.
        """
        return self._description or self.plugin.description

    @description.setter
    def description(self, new_description):
        """Sets a new description for the task with the given string."""
        self._description = new_description

    @property
    def item(self):
        """The item this task is associated with"""
        return self._item

    @property
    def name(self):
        """The display name of the task."""
        return self._name or self.plugin.name

    @name.setter
    def name(self, new_name):
        """Sets a new display name for the task with the given string."""
        self._name = new_name

    @property
    def plugin(self):
        """Returns the plugin associated with this task"""
        return self._plugin

    @property
    def settings(self):
        """The settings associated with this task."""
        return self._settings

