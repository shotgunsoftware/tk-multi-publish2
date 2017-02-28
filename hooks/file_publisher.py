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


class SceneHook(HookBaseClass):
    """
    Testing the new awesome hooks
    """

    @property
    def icon(self):
        return os.path.join(self.disk_location, "icons", "shotgun.png")

    @property
    def title(self):
        return "Publish files to Shotgun"

    @property
    def description_html(self):
        return """
        Publishes files to shotgun.
        """

    @property
    def settings(self):
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
        return ["file*"]

    def accept(self, log, settings, item):

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
        return True

    def publish(self, log, settings, item):

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
            "path": "file://%s" % item.properties["path"],
            "name": "%s%s" % (item.properties["prefix"], item.properties["extension"]),
            "version_number": item.properties["version"],
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": publish_type,
        }

        sg_data = sgtk.util.register_publish(**args)

        item.properties["shotgun_data"] = sg_data
        item.properties["shotgun_publish_id"] = sg_data["id"]


    def finalize(self, log, settings, item):
        pass



