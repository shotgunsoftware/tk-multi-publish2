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

class MultiPublish2(sgtk.platform.Application):
    """
    Main app class for publisher.

    Command registration and API methods.
    """

    def init_app(self):
        """
        Called as the application is being initialized
        """
        tk_multi_publish2 = self.import_module("tk_multi_publish2")

        # make the util methods available via the app instance
        self.util = tk_multi_publish2.util

        # register command
        cb = lambda: tk_multi_publish2.show_dialog(self)
        menu_caption = "Publish"
        menu_options = {
            "short_name": "publish",
            "description": "Publishing of data to Shotgun",
            # dark themed icon for engines that recognize this format
            "icons": {
                "dark": {
                    "png": os.path.join(self.disk_location, "icon_256_dark.png")
                }
            }
        }
        self.engine.register_command(menu_caption, cb, menu_options)

    @property
    def context_change_allowed(self):
        """
        Specifies that context changes are allowed.
        """
        return True

    def destroy_app(self):
        """
        Tear down the app
        """
        self.log_debug("Destroying tk-multi-publish2")
