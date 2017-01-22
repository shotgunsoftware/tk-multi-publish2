# Copyright (c) 2015 Shotgun Software Inc.
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



class TestHook(HookBaseClass):
    """
    Testing the new awesome hooks
    """
    @property
    def settings(self):
        return {
            "work_template": {"type": "template", "description": "Publish file template"},
        }

    @property
    def inputs(self):
        return {
            "version": {"type": "int", "description": "version number for current scene", "phase": self.parent.VALIDATE},
            "name": {"type": "str", "description": "foo bar baz", "phase": self.parent.VALIDATE},
        }

    @property
    def icon(self):
        return os.path.join(self.disk_location, "nuke.png")

    @property
    def title(self):
        return "Version up"

    @property
    def summary(self):
        return "Version up your current scene"

    @property
    def description_html(self):
        return """Thundercats <i>venmo</i> taxidermy, succulents next level poutine tacos pour-over jean shorts four
        loko gluten-free shabby chic lyft pinterest. Tilde drinking vinegar brunch, salvia seitan vinyl
        PBR&B sartorial mlkshk pop-up vegan pickled bitters wayfarers."""

    def scan_scene(self, log, settings):

        return {
            "Current Scene": {"checked": True, "required": True},
        }

    def validate(self, log, item, settings, inputs):

        log.info("This is validate for item %s" % item)
        log.info("Settings %s" % settings)
        log.info("Inputs %s" % inputs)
        time.sleep(0.4)




    def publish(self, log, item, settings, inputs):

        log.info("This is publish for item %s" % item)
        log.info("Settings %s" % settings)
        log.info("Inputs %s" % inputs)

        time.sleep(0.4)




