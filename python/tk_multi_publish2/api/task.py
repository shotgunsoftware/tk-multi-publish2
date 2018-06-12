# Copyright (c) 2018 Shotgun Software Inc.
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

logger = sgtk.platform.get_logger(__name__)


class PublishTask(object):
    """
    A task is a particular unit of work which can to be carried by the
    publishing process. A task can be thought of as a 'plugin instance', or a
    particular publishing plugin operating on a collected item.
    """

    def __init__(self, graph, plugin):
        """
        Initialize the task.
        # TODO
        """

        # every task created in the graph has a unique id
        self._id = uuid.uuid4().hex

        # A pointer to the graph that this task is a part of
        self._graph = graph

        # ensure the plugin has been added to the graph
        graph.add_plugin(plugin)

        self._name = plugin.name
        self._description = plugin.description
        self._plugin_id = plugin.id

        # need to make a deep copy of the settings
        self._settings = {}
        for (setting_name, setting) in plugin.settings.items():
            self._settings[setting_name] = setting.deep_copy()

        self._active = True
        self._visible = True
        self._enabled = True

        logger.debug("Created publish graph task: %s" % (self,))

    def __repr__(self):
        """Representation of the item as a string."""
        return "<[%s] %s: %s>" % (self._id, self.__class__.__name__, self._name)

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
        * ``None``: Clear the item's state, rely on inheritance within the graph
        """
        self._active = active_state

    @property
    def description(self):
        """
        The description of the item if it has been explicitly set,
        ``None`` otherwise.
        """
        return self._description

    @description.setter
    def description(self, new_description):
        """Sets a new description for the task with the given string."""
        self._description = new_description

    @property
    def id(self):
        """The unique id of the task."""
        return self._id

    @property
    def item(self):
        """The item this task is associated with"""
        return self._graph.get_item_for_task(self)

    @property
    def name(self):
        """The display name of the task."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Sets a new display name for the task with the given string."""
        self._name = new_name

    @property
    def plugin(self):
        """Returns the plugin associated with this task"""
        return self._graph.get_plugin_by_id(self._plugin_id)

    @property
    def settings(self):
        """The settings associated with this task."""
        return self._settings

