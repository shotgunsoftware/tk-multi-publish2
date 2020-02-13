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

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current scene open in a DCC and parents a subtree of items
        under the parent_item passed in.

        :param parent_item: Root item instance
        """
        parent_item.create_item(
            "generic.item", "A Generic Publish Item", "Generic Item 1"
        )

        parent_item.create_item(
            "generic.item", "A Generic Publish Item", "Generic Item 2"
        )

        parent_item.create_item(
            "generic.item", "A Generic Publish Item", "Generic Item 3"
        )

        parent_item.local_properties.collector_property = "collector_property"
