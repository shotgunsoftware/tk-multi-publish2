# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import inspect
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
            path,
            base_class=bundle.base_hooks.CollectorPlugin
        )
        plugin.id = path
        return plugin

    def _get_process_args(self, process_method, needed_args, new_supported_args):
        """
        Find args to be passed for the given process method
        """
        args = []
        if hasattr(self._hook_instance.__class__, "settings"):
            # this hook has a 'settings' property defined. it is expecting
            # 'settings' to be passed to the processing method.
            args.append(self.settings)

        # needed_args are added in any case
        args.extend(needed_args)

        # for backward compatibility
        # now check if the collector hook supports new arguments added afterward
        hook_process_args = inspect.getargspec(process_method).args
        for arg_name, arg_value in new_supported_args:
            has_optional_arg_set = arg_name in hook_process_args
            if has_optional_arg_set:
                # this hook has the given argument.
                # it is expecting to be passed to the processing method.
                args.append(arg_value)

        return args

    def run_process_file(self, item, path, collection_args=None):
        """
        Executes the hook process_file method

        :param item: Item to parent collected items under.
        :param path: The path of the file to collect
        :param collection_args: Custom data to be passed to the collector hook

        :returns: None (item creation handles parenting)
        """
        # build args to be passed to process method
        needed_args = [item, path]
        new_supported_args = [('collection_args', collection_args)]
        process_args = self._get_process_args(self._hook_instance.process_file, needed_args, new_supported_args)

        try:
            return self._hook_instance.process_file(*process_args)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error running process_file for %s. %s" %
                (self, error_msg)
            )

    def run_process_current_session(self, item, collection_args=None):
        """
        Executes the hook process_current_session method

        :param item: Item to parent collected items under.
        :param collection_args: Custom data to be passed to the collector hook

        :returns: None (item creation handles parenting)
        """
        # build args to be passed to process method
        needed_args = [item]
        new_supported_args = [('collection_args', collection_args)]
        process_args = self._get_process_args(self._hook_instance.process_current_session,
                                              needed_args,
                                              new_supported_args)

        try:
            return self._hook_instance.process_current_session(*process_args)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error running process_current_session for %s. %s" %
                (self, error_msg)
            )
