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



class TestHook(HookBaseClass):
    """
    Testing the new awesome hooks
    """
    @property
    def settings(self):
        settings = {}
        settings["setting_a"] = {"type": "int", "default": 5, "description": "foo bar baz"}
        settings["setting_b"] = {"type": "bool", "default": True, "description": "Should we do stuff?"}
        return settings

    @property
    def inputs(self):
        inputs = {}
        inputs["input_a"] = {"type": "str", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        inputs["input_b"] = {"type": "str", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        inputs["depends_on"] = {"type": "int", "description": "foo bar baz", "phase": self.parent.PUBLISH}
        return inputs

    @property
    def outputs(self):
        outputs = {}
        outputs["output_a"] = {"type": "str", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        return outputs

    @property
    def icon(self):
        return os.path.join(self.disk_location, "alembic_icon.png")

    @property
    def title(self):
        return "Testing Testing 1,2,3"

    @property
    def summary(self):
        return "This will befrozzle your guzzle"

    @property
    def description_html(self):
        return """Thundercats <i>venmo</i> taxidermy, succulents next level poutine tacos pour-over jean shorts four
        loko gluten-free shabby chic lyft pinterest. Tilde drinking vinegar brunch, salvia seitan vinyl
        PBR&B sartorial mlkshk pop-up vegan pickled bitters wayfarers."""

    def scan_scene(self, log, settings):

        log.info("This is scan scene waking up")
        log.info("Settings %s" % settings)

        return {
            "Character Manne": {"checked": True, "required": True},
            "Character Foo": {"checked": True},
            "Character Bar": {"checked": True},
        }

    def validate(self, log, item, settings, inputs):

        log.info("This is validate for item %s" % item)
        log.info("Settings %s" % settings)
        log.info("Inputs %s" % inputs)
        time.sleep(0.4)

        # raise sgtk.TankError("validation failed!")

        return {"output_a": "%s_%s" % (item, 9999999)}


    def publish(self, log, item, settings, inputs):

        log.info("This is publish for item %s" % item)
        log.info("Settings %s" % settings)
        log.info("Inputs %s" % inputs)

        time.sleep(0.4)




