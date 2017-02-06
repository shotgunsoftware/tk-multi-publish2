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
        return "Publish Maya Scene"

    @property
    def description_html(self):
        return """Publishes the current maya scene. This will create a versioned backup and publish that."""

    @property
    def settings(self):
        return {
            "Publish Type": {
                "type": "shotgun_publish_type",
                "default": "Maya Scene",
                "description": "Shotgun publish type to associate publishes with."
            },
        }

    @property
    def subscriptions(self):
        return ["maya.scene"]

    def accept(self, log, settings, item):

        return {"accepted": True, "required": False, "enabled": True}

    def validate(self, log, settings, item):

        if item.properties["path"] is None:
            log.error("Please save your scene before you continue!")
            return False

        if item.properties["project_root"] is None:
            log.warning("Your scene is not part of a maya project.")

        return True


    def publish(self, log, settings, item):

        # save the maya scene
        log.info("Saving maya scene...")
        cmds.file(save=True, force=True)

        scene_folder = os.path.dirname(item.properties["path"])
        filename = os.path.basename(item.properties["path"])
        publish_folder = os.path.join(scene_folder, "publishes")
        sgtk.util.filesystem.ensure_folder_exists(publish_folder)

        # figure out if we got any publishes already
        # determine highest version

        (filename_no_ext, extension) = os.path.splitext(filename)
        # strip the period off the extension
        extension = extension[1:]

        glob_pattern = os.path.join(publish_folder, "%s.v[0-9][0-9][0-9].%s" % (filename_no_ext, extension))
        log.debug("Looking for %s" % glob_pattern)

        published_files = glob.glob(glob_pattern)

        log.debug("Got %s" % published_files)

        higest_version_found = 0
        for published_file in published_files:
            # check if path matches pattern fooo.v123.ext
            version = re.search(".*\.v([0-9]+)\.%s$" % extension, published_file)
            if version:
                version_no_leading_zeroes = version.group(1).lstrip("0")
                if int(version_no_leading_zeroes) > higest_version_found:
                    higest_version_found = int(version_no_leading_zeroes)

        version_to_use = higest_version_found + 1

        publish_path = os.path.join(publish_folder, "%s.v%03d.%s" % (filename_no_ext, version_to_use, extension))

        log.info("Will publish to %s" % publish_path)

        sgtk.util.filesystem.copy_file(item.properties["path"], publish_path)

        # Create the TankPublishedFile entity in Shotgun
        args = {
            "tk": self.parent.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": "file://%s" % publish_path,
            "name": filename,
            "version_number": version_to_use,
            "thumbnail_path": item.get_thumbnail(),
            "published_file_type": settings["Publish Type"].value,
        }

        sg_data = sgtk.util.register_publish(**args)

        item.properties["shotgun_data"] = sg_data
        item.properties["shotgun_publish_id"] = sg_data["id"]


    def finalize(self, log, settings, item):
        pass




