# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class GenericRemotePlugin(HookBaseClass):
    """
    This should NOT process the item locally...
    """

    @property
    def name(self):
        return "Publish Plugin that runs REMOTELY"

    @property
    def description(self):
        return "This plugin should NOT process items locally"

    @property
    def settings(self):
        return {
            "run_on_farm": {
                "type": "bool",
                "default": "True",
                "description": "Indicates whether this plugin should run on farm."
            }
        }

    @property
    def item_filters(self):
        return ["generic.item"]

    @property
    def run_on_farm(self):
        return True

    def accept(self, settings, item):
        # inidicate that this plugin should only run remotely
        return {"accepted": True}

    def validate(self, settings, item):
        self.logger.debug("Executing remote plugin validate.")
        return True

    def publish(self, settings, item):
        self.logger.debug("Executing remote plugin publish.")

    def finalize(self, settings, item):
        self.logger.debug("Executing remote plugin finalize.")
