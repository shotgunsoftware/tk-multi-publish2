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

HookBaseClass = sgtk.get_hook_baseclass()


class MayaAlembicCachePublishPlugin(HookBaseClass):
    """
    Plugin for creating publishes for maya alembic files that exist on disk
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
        return "Publish Alembic"

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This
        can contain simple html for formatting.
        """
        return """Extracts alembic geometry."""

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
            "Publish Type": {
                "type": "shotgun_publish_type",
                "default": "Alembic Cache",
                "description": "Shotgun publish type to associate publishes with."
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
        return ["maya.alembic_file"]

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
        return {"accepted": True, "required": False, "enabled": True}

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
        # make sure parent is published
        if not item.parent.properties.get("is_published"):
            log.error("You must publish the main scene in order to publish alembic!")
            return False

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
        # save the maya scene
        scene_folder = os.path.dirname(item.properties["path"])
        filename = os.path.basename(item.properties["path"])
        (filename_no_ext, extension) = os.path.splitext(filename)
        # strip the period off the extension
        extension = extension[1:]

        publish_folder = os.path.join(scene_folder, "publishes")
        sgtk.util.filesystem.ensure_folder_exists(publish_folder)

        # use same version as parent scene
        version = item.parent.properties["publish_version"]

        publish_path = os.path.join(publish_folder, "%s.v%03d.%s" % (filename_no_ext, version, extension))

        log.info("Copying to %s" % publish_path)

        sgtk.util.filesystem.copy_file(item.properties["path"], publish_path)

        # Create the TankPublishedFile entity in Shotgun
        args = {
            "tk": self.parent.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": publish_path,
            "name": filename,
            "version_number": version,
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": settings["Publish Type"].value,
            "dependency_ids": [item.parent.properties["shotgun_publish_id"]]
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
        mov_path = item.properties["path"]
        log.info("Deleting %s" % item.properties["path"])
        sgtk.util.filesystem.safe_delete_file(mov_path)


