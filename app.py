# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
import os
import sgtk
from tank.util import sgre as re

logger = sgtk.platform.get_logger(__name__)


class MultiPublish2(sgtk.platform.Application):
    """
    This is the :class:`sgtk.platform.Application` subclass that defines the
    top-level publish2 interface.
    """

    CONFIG_PRE_PUBLISH_HOOK_PATH = "pre_publish"

    def init_app(self):
        """
        Called as the application is being initialized
        """

        tk_multi_publish2 = self.import_module("tk_multi_publish2")

        # the manager class provides the interface for publishing. We store a
        # reference to it to enable the create_publish_manager method exposed on
        # the application itself
        self._manager_class = tk_multi_publish2.PublishManager

        # make the util methods available via the app instance
        self._util = tk_multi_publish2.util

        # make the base plugins available via the app
        self._base_hooks = tk_multi_publish2.base_hooks

        display_name = self.get_setting("display_name")
        # "Publish Render" ---> publish_render
        command_name = display_name.lower()
        # replace all non alphanumeric characters by '_'
        command_name = re.sub(r"[^0-9a-zA-Z]+", "_", command_name)

        self.modal = self.get_setting("modal")

        pre_publish_hook_path = self.get_setting(self.CONFIG_PRE_PUBLISH_HOOK_PATH)
        self.pre_publish_hook = self.create_hook_instance(pre_publish_hook_path)

        # register command
        cb = lambda: tk_multi_publish2.show_dialog(self)
        menu_caption = "%s..." % display_name
        menu_options = {
            "short_name": command_name,
            "description": "Publishing of data to ShotGrid",
            # dark themed icon for engines that recognize this format
            "icons": {
                "dark": {"png": os.path.join(self.disk_location, "icon_256_dark.png")}
            },
        }
        self.engine.register_command(menu_caption, cb, menu_options)

    @property
    def base_hooks(self):
        """
        Exposes the publish2 ``base_hooks`` module.

        This module provides base class implementations of collector and publish
        plugin hooks:

        - :class:`~.base_hooks.CollectorPlugin`
        - :class:`~.base_hooks.PublishPlugin`

        Access to these classes won't typically be needed when writing hooks as
        they are are injected into the class hierarchy automatically for any
        collector or publish plugins configured.

        :return: A handle on the app's ``base_hooks`` module.
        """
        return self._base_hooks

    @property
    def util(self):
        """
        Exposes the publish2 ``util`` module.

        This module provides methods that are useful to collector and publish
        plugin hooks. Example code running in a hook:

        .. code-block:: python

            # get a handle on the publish2 app
            app = self.parent

            # call a util method
            path_components = app.util.get_file_path_components(path)

        Some of the methods available via ``util`` are the ``path_info`` hook
        methods. Exposing them via this property allows them to be called
        directly.

        :return: A handle on the app's ``util`` module.
        """
        return self._util

    @property
    def context_change_allowed(self):
        """
        Specifies that context changes are allowed.
        """
        return True

    def create_publish_manager(self, publish_logger=None):
        """
        Create and return a :class:`tk_multi_publish2.PublishManager` instance.
        See the :class:`tk_multi_publish2.PublishManager` docs for details on
        how it can be used to automate your publishing workflows.

        :param publish_logger: This is a standard python logger to use during
            publishing. A default logger will be provided if not supplied. This
            can be useful when implementing a custom UI, for example, with a
            specialized log handler (as is the case with the Publisher)

        :returns: A :class:`tk_multi_publish2.PublishManager` instance
        """
        return self._manager_class(publish_logger=publish_logger)

    def destroy_app(self):
        """
        Tear down the app
        """
        self.log_debug("Destroying tk-multi-publish2")
