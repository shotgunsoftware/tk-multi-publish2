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
import os
import time
import urllib

HookBaseClass = sgtk.get_hook_baseclass()


class GenericFilePublishPlugin(HookBaseClass):
    """
    Plugin for creating generic publishes in Shotgun
    """

    @property
    def icon(self):
        """
        Path to an png icon on disk
        """
        return os.path.join(self.disk_location, "icons", "shotgun.png")

    @property
    def name(self):
        """
        One line display name describing the plugin
        """
        return "Publish files to Shotgun"

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This
        can contain simple html for formatting.
        """
        return """
        Publishes files to shotgun.
        """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to recieve
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts
        as part of its environment configuration.
        """
        return {
            "File Types": {
                "type": "list",
                "default": "[]",
                "description": (
                    "List of file types to include. Each entry in the list "
                    "is a list in which the first entry is the Shotgun published "
                    "file type and subsequent entries are file extensions that should "
                    "be associated.")
            },
            "Publish all file types": {
                "type": "bool",
                "default": False,
                "description": (
                    "If set to True, all files will be published, "
                    "even if their extension has not been declared "
                    "in the file types setting.")
            },
        }

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.
        Only items matching entries in this list will be presented
        to the accept() method. Strings can contain glob patters
        such as *, for example ["maya.*", "file.maya"]
        """
        return ["file*"]

    def accept(self, log, settings, item):
        """
        Method called by the publisher to determine if an item
        is of any interest to this plugin. Only items matching
        the filters defined via the item_filters property will
        be presented to this method.

        A publish task will be generated for each item accepted
        here. Returns a dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in
                        this value at all.
            - required: If set to True, the publish task is
                        required and cannot be disabled.
            - enabled:  If True, the publish task will be
                        enabled in the UI by default.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        :returns: dictionary with boolean keys accepted, required and enabled
        """
        extension = item.properties["extension"]
        if extension.startswith("."):
            extension = extension[1:]

        if self._get_matching_publish_type(extension, settings):
            return {"accepted": True, "required": False, "enabled": True}

        else:
            return {"accepted": False}

    def _get_matching_publish_type(self, extension, settings):

        for type_def in settings["File Types"].value:

            publish_type = type_def[0]
            file_extensions = type_def[1:]

            if extension in file_extensions:
                return publish_type

        if settings["Publish all file types"].value:
            # publish type is based on extension
            return "%s File" % extension.capitalize()

        return None

    def validate(self, log, settings, item):
        """
        Validates the given item to check that it is ok to publish.
        Returns a boolean to indicate validity. Use the logger to
        output further details around why validation has failed.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        :returns: True if item is valid, False otherwise.
        """
        return True

    def publish(self, log, settings, item):
        """
        Executes the publish logic for the given
        item and settings. Use the logger to give
        the user status updates.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        """
        extension = item.properties["extension"]
        if extension.startswith("."):
            extension = extension[1:]

        publish_type = self._get_matching_publish_type(extension, settings)

        # Create the TankPublishedFile entity in Shotgun
        # note - explicitly calling
        args = {
            "tk": self.parent.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": item.properties["path"],
            "name": "%s%s" % (item.properties["prefix"], item.properties["extension"]),
            "version_number": item.properties["version"],
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": publish_type,
        }

        sg_data = sgtk.util.register_publish(**args)

        item.properties["shotgun_data"] = sg_data
        item.properties["shotgun_publish_id"] = sg_data["id"]


    def finalize(self, log, settings, item):
        """
        Execute the finalization pass. This pass executes once
        all the publish tasks have completed, and can for example
        be used to version up files.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        """
        pass



