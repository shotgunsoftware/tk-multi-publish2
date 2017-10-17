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

HookBaseClass = sgtk.get_hook_baseclass()


class BasicSceneCollector(HookBaseClass):
    """
    A basic collector that handles files and general objects.
    """

    def process_current_session(self, parent_item):
        """
        Analyzes the current scene open in a DCC and parents a subtree of items
        under the parent_item passed in.

        :param parent_item: Root item instance
        """
        parent_item.create_item(
            "plugin.noui",
            "No UI Plugin",
            "No UI Plugin"
        )

        parent_item.create_item(
            "plugin.withui",
            "With UI Plugin",
            "With UI Plugin"
        )
