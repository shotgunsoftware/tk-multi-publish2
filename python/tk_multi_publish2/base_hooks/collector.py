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


class CollectorPlugin(sgtk.Hook):
    """
    The base class is used for all collector plugins. This class is inserted
    into any loaded collector plugin's class hierarchy by the publisher itself.

    The collector is used to collect individual files that are browsed or
    dragged and dropped into the Publish2 UI. It can also be subclassed by other
    collectors responsible for creating items to be published within DCCs such
    as Maya, Nuke, or Photoshop.
    """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this collector expects to receive
        through the settings parameter in the process_current_session and
        process_file methods.

        A dictionary on the following form::

            {
                "Work Template": {
                    "type": "template",
                    "default": None,
                    "description": "A work file template required by this collector."
            }

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.

        The settings are exposed via the `collector_settings` setting in the
        app's configuration. Example::

            collector_settings:
              Work Template: my_work_template
        """
        return {}

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current DCC session and creates a hierarchy of items to
        publish.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance
        """
        raise NotImplementedError

    def process_file(self, settings, parent_item, path):
        """
        Analyzes the given file and creates one or more items to represent it.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance
        :param path: Path to analyze

        :returns: The main item that was created, or None if no item was created
            for the supplied path
        """
        raise NotImplementedError
