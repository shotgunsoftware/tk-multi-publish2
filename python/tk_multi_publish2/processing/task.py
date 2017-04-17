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

    def __init__(self, plugin, item, visible, enabled, checked):
        """
        :param plugin: The plugin instance associated with this task
        :param item: The collector item associated with this task
        :param bool visible: Indicates that the task is visible
        :param bool enabled: Indicates that the task is enabled
        :param bool checked: Indicates that the task is checked
        """
        self._plugin = plugin
        self._item = item
        self._settings = []
        self._visible = visible
        self._enabled = enabled
        self._checked = checked

    def __repr__(self):
        """
        String representation
        """
        return "<Task: %s for %s >" % (self._plugin, self._item)

    @classmethod
    def create_task(cls, plugin, item, is_visible, is_enabled, is_checked):
        """
        Factory method for new tasks.

        :param plugin: Plugin instance
        :param item: Item object
        :param is_visible: bool to indicate if this option should be shown
        :param is_enabled: bool to indicate if node is enabled (clickable)
        :param is_checked: bool to indicate if this node is checked
        :return: Task instance
        """
        task = Task(plugin, item, is_visible, is_enabled, is_checked)
        plugin.add_task(task)
        item.add_task(task)
        logger.debug("Created %s" % task)
        return task

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
    def visible(self):
        """
        Returns if this Task should be visible in the UI.
        Invisible tasks are still processed but not seen in the UI
        """
        return self._visible

    @property
    def checked(self):
        """
        Returns if this task should be turned on or off by default
        """
        return self._checked

    @property
    def enabled(self):
        """
        Returns if this task's checked state can be manipulated by the user or not.
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
