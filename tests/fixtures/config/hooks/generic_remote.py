# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

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
                "description": "Indicates whether this plugin should run on farm.",
            }
        }

    @property
    def item_filters(self):
        return ["generic.item"]

    def accept(self, settings, item):
        item.local_properties.plugin_name = "remote"

        # force 'run_on_farm' if there is no UI
        publisher = self.parent
        if not publisher.engine.has_ui:
            settings["run_on_farm"].value = True

        return {"accepted": True}

    def validate(self, settings, item):
        if "TEST_LOCAL_PROPERTIES" in os.environ:
            # local properties was properly set, so make sure it raises an error.
            # see test_item:test_local_properties_persistance for more info.
            if item.local_properties.plugin_name == "remote":
                raise Exception("local_properties was serialized properly.")
        self.logger.debug("Executing remote plugin validate.")
        return True

    def publish(self, settings, item):

        publisher = self.parent
        run_on_farm = settings["run_on_farm"].value

        # don't do anything if "run_on_farm" is True and the engine has a UI
        if publisher.engine.has_ui and run_on_farm:
            self.logger.debug("Skipping remote plugin execution.")
            return

        self.logger.debug("Executing remote plugin publish.")

    def finalize(self, settings, item):

        publisher = self.parent
        run_on_farm = settings["run_on_farm"].value

        # don't do anything if "run_on_farm" is True and the engine has a UI
        if publisher.engine.has_ui and run_on_farm:
            self.logger.debug("Skipping remote plugin execution.")
            return

        self.logger.debug("Executing remote plugin finalize.")
