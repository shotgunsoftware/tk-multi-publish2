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


class MayaPlayblastReviewPlugin(HookBaseClass):
    """
    Testing the new awesome hooks
    """

    @property
    def icon(self):
        return os.path.join(self.disk_location, "icons", "play.png")

    @property
    def name(self):
        return "Review Playblast"

    @property
    def description(self):
        return """Send playblast to Shotgun for review."""

    @property
    def settings(self):
        return {}

    @property
    def item_filters(self):
        return ["maya.playblast"]


    def accept(self, log, settings, item):

        return {"accepted": True, "required": False, "enabled": True}

    def validate(self, log, settings, item):

        return True

    def publish(self, log, settings, item):

        filename = os.path.basename(item.properties["path"])
        (file_name_no_ext, _) = os.path.splitext(filename)

        data = {
            "project": item.context.project,
            "code": "Maya Playblast %s" % file_name_no_ext.capitalize(),
            "description": item.description,
        }

        # see if the parent has been published
        if "shotgun_publish_id" in item.parent.properties:
            data["published_files"] = [
                {
                    "type": "PublishedFile",
                    "id": item.parent.properties["shotgun_publish_id"]
                }
            ]

        # set the context
        if item.context.project:
            data["entity"] = item.context.project
        if item.context.entity:
            data["entity"] = item.context.entity
        if item.context.task:
            data["entity"] = item.context.task

        log.info("Creating version for review")
        version = self.parent.shotgun.create("Version", data)

        log.info("Uploading content")
        self.parent.shotgun.upload("Version", version["id"], item.properties["path"], "sg_uploaded_movie")



    def finalize(self, log, settings, item):

        mov_path = item.properties["path"]
        log.info("Deleting %s" % item.properties["path"])
        sgtk.util.filesystem.safe_delete_file(mov_path)





