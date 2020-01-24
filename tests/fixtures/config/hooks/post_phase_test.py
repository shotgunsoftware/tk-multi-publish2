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


# this isn't a realistic example of post phase hook, but it allows for testing
# several non-item-specific methods


class PostPhaseHook(HookBaseClass):
    def post_validate(self, publish_tree):
        self.logger.debug("Executing post validate hook method...")

    def post_publish(self, publish_tree):
        self.logger.debug("Executing post publish hook method...")

    def post_finalize(self, publish_tree):
        self.logger.debug("Executing post finalize hook method...")
