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

HookBaseClass = sgtk.get_hook_baseclass()


class PluginWithoutUi(HookBaseClass):
    """
    Plugin for creating generic publishes in Shotgun
    """

    @property
    def item_filters(self):
        return ["plugin.test.visibility"]

    def accept(self, settings, item):
        return {"accepted": True, "visible": True}

    def validate(self, settings, item):
        self.logger.info("VALIDATING VISIBLE PLUGIN 3")
        return True

    def publish(self, settings, item):
        self.logger.info("EXECUTING VISIBLE PLUGIN 3")

    def finalize(self, settings, item):
        pass
