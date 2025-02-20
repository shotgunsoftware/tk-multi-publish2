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
from .plugins import PluginSetting, PublishPluginInstance

logger = sgtk.platform.get_logger(__name__)


class PublishTask(object):
    """
    Publish tasks represent the operations to be performed on
    a :ref:`publish-api-item` in the :ref:`publish-api-tree`. Each item has a
    list of associated tasks that will be executed when a publish is initiated.

    Each task wraps a configured publish plugin instance, storing the
    settings defined by that plugin that are specific to the item it is
    associated with.
    """

    __slots__ = [
        "_item",
        "_plugin",
        "_name",
        "_description",
        "_settings",
        "_active",
        "_visible",
        "_enabled",
    ]

    @classmethod
    def from_dict(cls, task_dict, serialization_version, item=None):
        """
        Returns an instance of a PublishTask from serialized data.

        :param dict task_dict: A dictionary of deserialized task data
        :param int serialization_version: The version of serialization logic used to
            serialize this data.
        :param item: Optional item to associate with this task
        """

        # create the plugin instance
        plugin = PublishPluginInstance(
            task_dict["plugin_name"],
            task_dict["plugin_path"],
            task_dict["plugin_settings"],
        )

        # create the instance and assign all the internal members
        new_task = PublishTask(plugin, item)
        new_task._name = task_dict["name"]
        new_task._description = task_dict["description"]
        new_task._active = task_dict["active"]
        new_task._visible = task_dict["visible"]
        new_task._enabled = task_dict["enabled"]

        # create all the setting instances from the data
        for k, setting in task_dict["settings"].items():
            new_setting = PluginSetting(
                setting["name"],
                setting["type"],
                setting["default_value"],
                setting["description"],
            )
            new_setting.value = setting["value"]
            new_task._settings[k] = new_setting

        return new_task

    def __init__(self, plugin, item, visible=True, enabled=True, checked=True):
        """
        Initialize the task.
        """

        self._item = item
        self._plugin = plugin
        self._name = None  # task name override of plugin name
        self._description = None  # task description override of plugin desc.

        # need to make a deep copy of the settings as they may be modified
        self._settings = {}
        for setting_name, setting in plugin.settings.items():
            self._settings[setting_name] = copy.deepcopy(setting)

        self._active = checked
        self._visible = visible
        self._enabled = enabled

        logger.debug("Created publish tree task: %s" % (self,))

    def to_dict(self):
        """
        Returns a dictionary representation of a :class:`~PublishTask` instance.
        Typically used during serialization.
        """

        # Convert each of the settings to a dictionary.
        converted_settings = {}
        for k, setting in self._settings.items():
            converted_settings[k] = setting.to_dict()

        # build the full dictionary representation of this task
        return {
            "plugin_name": self.plugin.name,
            "plugin_path": self.plugin.path,
            "plugin_settings": self.plugin.configured_settings,
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

    def is_same_task_type(self, other_task):
        """
        Indicates if this task represents the same plugin type as the supplied
        publish task.

        :param other_task: The other plugin to test against.
        :type other_task: :class:`PublishTask`
        """
        return self._plugin == other_task._plugin

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

    def validate(self):
        """
        Validate this Task

        :returns: True if validation succeeded, False otherwise.
        """
        return self.plugin.run_validate(self.settings, self.item)

    @property
    def active(self):
        """
        Returns the item's active state if it has been explicitly set, `None``
        otherwise.

        .. note:: This property is shared with ``checked`` and can be used
            interchangeably to make code more readable depending on the context
            (with/without the UI).
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
    def checked(self):
        """
        Boolean property to indicate that this task should be checked by
        default when displayed in a publish UI.

        .. note:: This property is shared with ``active`` and can be used
            interchangeably to make code more readable depending on the context
            (with/without the UI).
        """
        return self._active

    @property
    def visible(self):
        """
        Boolean property to indicate that this task should be visible in a
        publish UI.

        .. note:: This property is shared with ``active`` and can be used
            interchangeably to make code more readable depending on the context
            (with/without the UI).
        """
        return self._visible

    @visible.setter
    def visible(self, is_visible):
        """
        Sets the visibility state.

        :param bool is_enabled: If ``True``, the task will be visible in
            the publish UI. If ``False``, it won't be visible.
        """
        self._visible = is_visible

    @property
    def enabled(self):
        """
        Boolean property to indicate that this task should be editable in a
        publish UI.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, is_enabled):
        """
        Sets the enabled state.

        :param bool is_enabled: If ``True``, the task will be editable in
            the publish UI. If ``False``, it won't be editable.
        """
        self._enabled = is_enabled

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
        """The :ref:`publish-api-item` this task is associated with"""
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
        """Returns the publish plugin instance associated with this task"""
        return self._plugin

    @property
    def settings(self):
        """
        A :py:attr:`dict` of settings associated with this task.

        The keys of this dictionary are the setting names and the values are
        :ref:`publish-api-setting` instances.
        """
        return self._settings
