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
        return "Maya Scene"

    @property
    def description_html(self):
        return """Thundercats <i>venmo</i> taxidermy, succulents next level poutine tacos pour-over jean shorts four
        loko gluten-free shabby chic lyft pinterest. Tilde drinking vinegar brunch, salvia seitan vinyl
        PBR&B sartorial mlkshk pop-up vegan pickled bitters wayfarers."""


    @property
    def settings(self):
        return {
            "setting_a": {"type": "int", "default": 5, "description": "foo bar baz"},
            "setting_b": {"type": "bool", "default": True, "description": "Should we do stuff?"}
        }


    @property
    def subscriptions(self):
        return ["maya.scene"]

    def accept(self, log, settings, item):

        log.debug("%s: Running accept for %s with settings %s" % (self, item, settings))
        return {"accepted": True, "required": True, "enabled": True}

    def validate(self, log, settings, item):

        log.info("This is validate for item %s" % item)
        log.info("Settings %s" % settings)
        time.sleep(0.4)
        # raise sgtk.TankError("validation failed!")


    def publish(self, log, settings, item):

        log.info("This is publish for item %s" % item)
        log.info("Settings %s" % settings)

        item.parent.data["foo"]

        time.sleep(0.4)

    def finalize(self, log, settings, item):

        log.info("This is finalize for item %s" % item)
        log.info("Settings %s" % settings)
        time.sleep(0.4)



