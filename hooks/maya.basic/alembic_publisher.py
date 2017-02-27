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
import re
import time
import glob
import maya.cmds as cmds
import maya.mel as mel

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
        return "Publish Alembic"

    @property
    def description_html(self):
        return """Extracts alembic geometry."""

    @property
    def settings(self):
        return {
            "Publish Type": {
                "type": "shotgun_publish_type",
                "default": "Alembic Cache",
                "description": "Shotgun publish type to associate publishes with."
            },
        }

    @property
    def item_filters(self):
        return ["maya.alembic_file"]

    def accept(self, log, settings, item):

        return {"accepted": True, "required": False, "enabled": True}

    def validate(self, log, settings, item):

        # make sure parent is published
        if not item.parent.properties.get("is_published"):
            log.error("You must publish the main scene in order to publish alembic!")
            return False

        return True


    def publish(self, log, settings, item):

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
            "path": "file://%s" % publish_path,
            "name": filename,
            "version_number": version,
            "thumbnail_path": item.get_thumbnail(),
            "published_file_type": settings["Publish Type"].value,
            "dependency_ids": [item.parent.properties["shotgun_publish_id"]]
        }

        sg_data = sgtk.util.register_publish(**args)

        item.properties["shotgun_data"] = sg_data
        item.properties["shotgun_publish_id"] = sg_data["id"]


    def finalize(self, log, settings, item):

        mov_path = item.properties["path"]
        log.info("Deleting %s" % item.properties["path"])
        sgtk.util.filesystem.safe_delete_file(mov_path)


