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
            "File Extensions": {"type": "str", "default": "jpeg, jpg, png, mov", "description": "File Extensions of files to include"},
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

        log.info("Uploading version to Shotgun...")
        sg = self.parent.shotgun.create(
            "Version",
            {"project": self.parent.context.project,
             "code": item.properties["filename"],
             "description": self.item.description,
             }
        )
        log.info("sg: %s" % sg)



        log.info("This is publish for item %s" % item)
        time.sleep(0.4)

    def finalize(self, log, settings, item):
        pass



