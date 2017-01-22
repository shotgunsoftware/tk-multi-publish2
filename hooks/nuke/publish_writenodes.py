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



class WriteNodePublisher(HookBaseClass):
    """
    Testing the new awesome hooks
    """
    @property
    def settings(self):
        return {
            "Publish Type":                  {"type": "str", "description": "Publish type to associate the publish with"},
            "Clean up Work Renders":         {"type": "bool", "default": True, "description": "Clean up?"},
            "Upload to Shotgun for Review?": {"type": "bool", "default": True, "description": "review?"}
        }

    @property
    def inputs(self):
        return {
            "version":    {"type": "int", "description": "version number to associate with publishes", "phase": self.parent.VALIDATE},
            "name":       {"type": "str", "description": "foo bar baz", "phase": self.parent.VALIDATE},
            "depends_on": {"type": "int", "description": "publish id for items that ", "phase": self.parent.PUBLISH},
        }

    @property
    def icon(self):
        return os.path.join(self.disk_location, "film.png")

    @property
    def title(self):
        return "Publish Renders"

    @property
    def summary(self):
        return "Publish your renders in Shotgun"

    @property
    def description_html(self):
        return """Thundercats <i>venmo</i> taxidermy, succulents next level poutine tacos pour-over jean shorts four
        loko gluten-free shabby chic lyft pinterest. Tilde drinking vinegar brunch, salvia seitan vinyl
        PBR&B sartorial mlkshk pop-up vegan pickled bitters wayfarers."""

    def scan_scene(self, log, settings):

        log.info("This is scan scene waking up")
        log.info("Settings %s" % settings)

        return {
            "Node A": {"checked": True, "required": True},
            "Node B": {"checked": True},
            "Node C": {"checked": True},
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




