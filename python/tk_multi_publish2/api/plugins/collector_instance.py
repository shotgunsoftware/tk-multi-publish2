# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import traceback

import sgtk
from .instance_base import PluginInstanceBase

logger = sgtk.platform.get_logger(__name__)


class CollectorPluginInstance(PluginInstanceBase):
    """
    Class that wraps around a collector hook

    Each collector plugin object reflects an instance in the app configuration.
    """

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance.

        Injects the collector base class in order to provide default
        implementation.
        """
        bundle = sgtk.platform.current_bundle()
        plugin = bundle.create_hook_instance(
            path, base_class=bundle.base_hooks.CollectorPlugin
        )
        plugin.id = path
        return plugin

    def run_process_file(self, item, path):
        """
        Executes the hook process_file method

        :param item: Item to parent collected items under.
        :param path: The path of the file to collect

        :returns: None (item creation handles parenting)
        """
        try:
            if hasattr(self._hook_instance.__class__, "settings"):
                # this hook has a 'settings' property defined. it is expecting
                # 'settings' to be passed to the processing method.
                return self._hook_instance.process_file(self.settings, item, path)
            else:
                # the hook hasn't been updated to handle collector settings.
                # call the method without a settings argument
                return self._hook_instance.process_file(item, path)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error("Error running process_file for %s. %s" % (self, error_msg))

    def run_process_current_session(self, item):
        """
        Executes the hook process_current_session method

        :param item: Item to parent collected items under.

        :returns: None (item creation handles parenting)
        """
        try:
            if hasattr(self._hook_instance.__class__, "settings"):
                # this hook has a 'settings' property defined. it is expecting
                # 'settings' to be passed to the processing method.
                return self._hook_instance.process_current_session(self.settings, item)
            else:
                # the hook hasn't been updated to handle collector settings.
                # call the method without a settings argument
                return self._hook_instance.process_current_session(item)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error running process_current_session for %s. %s" % (self, error_msg)
            )
