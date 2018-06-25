# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from contextlib import contextmanager
import traceback

import sgtk
from .instance_base import PluginInstanceBase

logger = sgtk.platform.get_logger(__name__)


class PublishPluginInstance(PluginInstanceBase):
    """
    Class that wraps around a publishing plugin hook

    Each plugin object reflects an instance in the app configuration.
    """

    def __init__(self, name, path, settings, logger):
        """
        :param name: Name to be used for this plugin instance
        :param path: Path to publish plugin hook
        :param settings: Dictionary of plugin-specific settings
        :param logger: a logger object that will be used by the hook
        """
        # all plugins need a hook and a name
        self._name = name

        super(PublishPluginInstance, self).__init__(path, settings, logger)

    def __getstate__(self):
        """
        This method is used during serialization to return the state of the
        plugin instance as a dictionary.
        """

        state = super(PublishPluginInstance, self).__getstate__()
        state["name"] = self._name

        return state

    def __setstate__(self, state):
        """
        This method accepts a deserialized dictionary and returns the current
        instance populated with that state.
        """

        super(PublishPluginInstance, self).__setstate__(state)
        self._name = state["name"]

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance.

        Injects the plugin base hook class in order to provide a default
        implementation.
        """
        bundle = sgtk.platform.current_bundle()
        return bundle.create_hook_instance(
            path,
            base_class=bundle.base_hooks.PublishPlugin
        )

    @property
    def name(self):
        """
        The name of this publish plugin instance
        """
        return self._name

    @property
    def plugin_name(self):
        """
        The name of the publish plugin itself.
        Always a string.
        """
        value = None
        try:
            value = self._hook_instance.name
        except AttributeError:
            pass

        return value or "Untitled Integration."

    @property
    def description(self):
        """
        The description of the publish plugin.
        Always a string.
        """
        value = None
        try:
            value = self._hook_instance.description
        except AttributeError:
            pass

        return value or "No detailed description provided."

    @property
    def item_filters(self):
        """
        The item filters defined by this plugin
        or [] if none have been defined.
        """
        try:
            return self._hook_instance.item_filters
        except AttributeError:
            return []

    @property
    def has_custom_ui(self):
        """
        Checks if a plugin has a custom widget.

        :returns: ``True`` if the plugin supports ``create_settings_widget``,
            ``get_ui_settings`` and ``set_ui_settings``,``False`` otherwise.
        """
        return all(
            hasattr(self._hook_instance, attr)
            for attr in ["create_settings_widget", "get_ui_settings", "set_ui_settings"]
        )

    @property
    def settings(self):
        """
        returns a dict of resolved raw settings given the current state
        """
        return self._settings

    def run_accept(self, item):
        """
        Executes the hook accept method for the given item

        :param item: Item to analyze
        :returns: dictionary with boolean keys accepted/visible/enabled/checked
        """
        try:
            return self._hook_instance.accept(self.settings, item)
        except Exception:
            error_msg = traceback.format_exc()
            self.logger.error("Error running accept for %s" % (self,))
            return {"accepted": False}

    def run_validate(self, settings, item):
        """
        Executes the validation logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        :return: True if validation passed, False otherwise.
        """

        with self._handle_plugin_error(None, "Error Validating: %s"):
            status = self._hook_instance.validate(settings, item)

        # check that we are not trying to publish to a site level context
        if item.context.project is None:
            status = False
            self.logger.error("Please link '%s' to a Shotgun object and task!" % item.name)

        if status:
            self.logger.info("Validation successful!")
        else:
            self.logger.error("Validation failed.")

        return status

    def run_publish(self, settings, item):
        """
        Executes the publish logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        """
        with self._handle_plugin_error("Publish complete!", "Error publishing: %s"):
            self._hook_instance.publish(settings, item)

    def run_finalize(self, settings, item):
        """
        Executes the finalize logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        """
        with self._handle_plugin_error("Finalize complete!", "Error finalizing: %s"):
            self._hook_instance.finalize(settings, item)

    @contextmanager
    def _handle_plugin_error(self, success_msg, error_msg):
        """
        Creates a scope that will properly handle any error raised by the plugin
        while the scope is executed.

        .. note::
            Any exception raised by the plugin is bubbled up to the caller.

        :param str success_msg: Message to be displayed if there is no error.
        :param str error_msg: Message to be displayed if there is an error.
        """

        try:
            # Execute's the code inside the with statement. Any errors will be
            # caught and logged and the events will be processed
            yield
        except Exception as e:
            exception_msg = traceback.format_exc()
            self.logger.error(error_msg % (e,))
            raise
        else:
            if success_msg:
                self.logger.info(success_msg)
