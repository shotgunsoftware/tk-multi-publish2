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
        return ["plugin.property_test"]

    def accept(self, settings, item):
        item.local_properties.publish_type = "Greatness"
        item.local_properties.publish_path = "/foo/bar/baz/publish/image.%04d.jpg"
        item.local_properties["publish_name"] = "render.jpg"
        return {"accepted": True}

    def validate(self, settings, item):
        return self._ensure_properties_correct(settings, item)

    def publish(self, settings, item):
        self._ensure_properties_correct(settings, item)

    def finalize(self, settings, item):
        pass

    def _ensure_properties_correct(self, settings, item):

        # for this plugin, make sure all of the publish properties match their
        # value defined in the collector

        # publish_type
        expected_value = "Greatness"
        publish_type = self.get_publish_type(settings, item)
        if publish_type == expected_value:
            self.logger.info("Publish type property is correct")
        else:
            self.logger.error(
                "Publish type property incorrect. "
                "Should be '%s' but is '%s'" % (expected_value, publish_type)
            )
            return False

        # publish_path
        expected_value = "/foo/bar/baz/publish/image.%04d.jpg"
        publish_path = self.get_publish_path(settings, item)
        if publish_path == expected_value:
            self.logger.info("Publish path property is correct")
        else:
            self.logger.error(
                "Publish path property incorrect. "
                "Should be '%s' but is '%s'" % (expected_value, publish_path)
            )
            return False

        # publish_name
        expected_value = "render.jpg"
        publish_name = self.get_publish_name(settings, item)
        if publish_name == expected_value:
            self.logger.info("Publish name property is correct")
        else:
            self.logger.error(
                "Publish name property incorrect. "
                "Should be '%s' but is '%s'" % (expected_value, publish_name)
            )
            return False

        # publish_version
        expected_value = "007"
        publish_version = self.get_publish_version(settings, item)
        if publish_version == expected_value:
            self.logger.info("Publish version property is correct")
        else:
            self.logger.error(
                "Publish version property incorrect. "
                "Should be '%s' but is '%s'" % (expected_value, publish_version)
            )
            return False

        # publish_dependencies
        expected_value = ["/foo/bar/model.abc", "/foo/bar/rig.ma"]
        publish_dependencies = self.get_publish_dependencies(settings, item)
        if publish_dependencies == expected_value:
            self.logger.info("Publish dependencies property is correct")
        else:
            self.logger.error(
                "Publish dependencies property incorrect. "
                "Should be '%s' but is '%s'" % (expected_value, publish_dependencies)
            )
            return False

        return True
