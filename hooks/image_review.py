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

HookBaseClass = sgtk.get_hook_baseclass()


class SceneHook(HookBaseClass):
    """
    Testing the new awesome hooks
    """

    @property
    def icon(self):
        return os.path.join(self.disk_location, "icons", "flash.png")

    @property
    def title(self):
        return "Send files to Shotgun review"

    @property
    def description_html(self):
        return """Uploads files to Shotgun for Review."""

    @property
    def settings(self):
        return {
            "File Extensions": {
                "type": "str",
                "default": "jpeg, jpg, png, mov, mp4",
                "description": "File Extensions of files to include"
            },
            "Create Local Link": {
                "type": "bool",
                "default": False,
                "description": "Should the local file be referenced by Shotgun"
            },
            "Upload": {
                "type": "bool",
                "default": True,
                "description": "Upload content to Shotgun?"
            },

        }

    @property
    def subscriptions(self):
        return ["file*"]

    def accept(self, log, settings, item):

        valid_extensions = []

        for ext in settings["File Extensions"].value.split(","):
            ext = ext.strip()
            if ext.startswith("."):
                valid_extensions.append(ext)
            else:
                valid_extensions.append(".%s" % ext)

        log.debug("valid extensions: %s" % valid_extensions)

        if item.properties["extension"] in valid_extensions:
            return {"accepted": True, "required": False, "enabled": True}

        else:
            return {"accepted": False}

    def validate(self, log, settings, item):
        pass


    def publish(self, log, settings, item):

        data = {
            "project": self.parent.context.project,
            "code": item.properties["filename"],
            "description": item.description,
        }

        if settings["Create Local Link"].value:
            data["sg_path_to_movie"] = item.properties["path"]

        log.info("Creating version for review")
        version = self.parent.shotgun.create("Version", data)

        # and thumbnail
        thumb = item.get_thumbnail()
        if thumb:
            log.info("Uploading thumbnail")
            self.parent.shotgun.upload_thumbnail("Version", version["id"], item.get_thumbnail())

        # and payload
        if settings["Upload"].value:
            log.info("Uploading content")
            self.parent.shotgun.upload("Version", version["id"], item.properties["path"], "sg_uploaded_movie")


    def finalize(self, log, settings, item):
        pass



