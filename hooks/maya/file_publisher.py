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
        return {
            #"setting_a": {"type": "int", "default": 5, "description": "foo bar baz"},
        }


    @property
    def subscriptions(self):
        return ["file*"]

    def accept(self, log, settings, item):

        log.debug("%s: Running accept for %s with settings %s" % (self, item, settings))
        return {"accepted": True, "required": True, "enabled": True}

    def validate(self, log, settings, item):

        log.info("This is validate for item %s" % item)
        log.warning("warning!")
        log.error("error!")
        time.sleep(0.4)
        # raise sgtk.TankError("validation failed!")


    def publish(self, log, settings, item):

        log.info("This is publish for item %s" % item)
        time.sleep(0.4)

    def finalize(self, log, settings, item):

        log.info("This is finalize for item %s" % item)
        time.sleep(0.4)



