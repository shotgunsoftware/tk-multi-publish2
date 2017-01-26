# Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Multi Publish

"""

import sgtk

class MultiPublish2(sgtk.platform.Application):

    (VALIDATE, PUBLISH) = range(2)

    def init_app(self):
        """
        Called as the application is being initialized
        """
        tk_multi_publish2 = self.import_module("tk_multi_publish2")

        # register command
        cb = lambda : tk_multi_publish2.show_dialog(self)
        menu_caption = "Publish..."
        menu_options = {"short_name": "publish", "description": "Publishing of data into Shotgun"}
        self.engine.register_command(menu_caption, cb, menu_options)

        self._dropped_files = []

    @property
    def context_change_allowed(self):
        """
        Specifies that context changes are allowed.
        """
        return True

    def destroy_app(self):

        self.log_debug("Destroying tk-multi-publish")


    def add_external_files(self, files):
        self.log_debug("Adding external files: %s" % files)
        self._dropped_files.extend(files)

