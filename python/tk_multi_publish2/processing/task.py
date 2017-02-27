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
    A task is a particular unit of work which can to be carried
    by the publishing process. A task can be thought of as a
    'plugin instance', e.g a particular publishing plugin operating
    on a particular collector item.
    """

    def __init__(self, plugin, item):
        """
        :param plugin: The plugin instance associated with this task
        :param item: The collector item associated with this task
        """
        self._plugin = plugin
        self._item = item
        self._settings = []
        self._enabled = False
        self._required = False

    def __repr__(self):
        return "<Task: %s for %s >" % (self._plugin, self._item)

    def set_plugin_defaults(self, required, enabled):
        """
        Set the
        :param required:
        :param enabled:
        """
        self._required = required
        self._enabled = enabled

    @property
    def item(self):
        """
        The item associated with this Task
        """
        return self._item

    @property
    def plugin(self):
        """
        The plugin associated with this Task
        """
        return self._plugin

    @property
    def required(self):
        """
        Returns if this Task is required by the publishing
        """
        return self._required

    @property
    def enabled(self):
        """
        Returns if this
        @return:
        """
        return self._enabled

    @property
    def settings(self):
        """
        Dictionary of settings associated with this Task
        """
        # TODO - make settings configurable per task
        return self.plugin.settings

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
