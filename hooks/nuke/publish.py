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
from sgtk import TankError
import os
import time
import nuke

HookBaseClass = sgtk.get_hook_baseclass()



class NukeScenePublish(HookBaseClass):
    """
    Testing the new awesome hooks
    """

    @property
    def settings(self):
        return {
            "Publish Type":     {"type": "str", "description": "Publish type to associate published nuke file with."},
            "work_template":    {"type": "template", "description": "Work file template"},
            "publish_template": {"type": "template", "description": "Publish file template"},
        }

    @property
    def outputs(self):
        return {
            "version": {"type": "int", "description": "version number to associate with publishes", "phase": self.parent.VALIDATE},
            "scene_name": {"type": "str", "description": "foo bar baz", "phase": self.parent.VALIDATE},
            "publish_id": {"type": "int", "description": "foo bar baz", "phase": self.parent.PUBLISH},
        }

    @property
    def icon(self):
        return os.path.join(self.disk_location, "nuke.png")

    @property
    def title(self):
        return "Publish your nuke script"

    @property
    def summary(self):
        return "Publishes your nuke script to Shotgun"

    @property
    def description_html(self):
        return """foo bar."""

    def scan_scene(self, log, settings):

        return {
            "Current Scene": {"checked": True, "required": True},
        }

    def validate(self, log, item, settings, inputs):

        log.info("This is validate for item %s" % item)
        log.info("Settings %s" % settings)
        log.info("Inputs %s" % inputs)
        time.sleep(0.4)

        return {"version": 5, "scene_name": "scene"}


    def publish(self, log, item, settings, inputs):

        log.info("This is publish for item %s" % item)
        log.info("Settings %s" % settings)
        log.info("Inputs %s" % inputs)

        time.sleep(0.4)

        return {"publish_id": 123}




