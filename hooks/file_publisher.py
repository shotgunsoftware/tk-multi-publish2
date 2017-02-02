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
        return os.path.join(self.disk_location, "icons", "shotgun.png")

    @property
    def title(self):
        return "File Publisher"

    @property
    def description_html(self):
        return """Publishes files to shotgun"""

    @property
    def settings(self):
        return {}

    @property
    def subscriptions(self):
        return ["file*"]

    def accept(self, log, settings, item):

        return {"accepted": True, "required": False, "enabled": True}

    def validate(self, log, settings, item):
        return True


    def publish(self, log, settings, item):

        # Create the TankPublishedFile entity in Shotgun
        args = {
            "tk": self.parent.sgtk,
            "context": self.parent.context,
            "comment": item.description,
            "path": "file://%s" % item.properties["path"],
            "name": item.properties["filename"],
            "version_number": 0,
            "thumbnail_path": item.get_thumbnail(),
            "tank_type": item.properties["extension"],
        }

        sgtk.util.register_publish(**args)


    def finalize(self, log, settings, item):
        pass



